import urllib
import re
import pkg_resources
from bs4 import BeautifulSoup
import textwrap
from collections import OrderedDict
from lxml import etree
import pandas
import simplejson

CACHED_SCHEMA_FILE = pkg_resources.resource_filename(
    "pysiss.vocabulary.resources",
    "earthchem_soap_search_schema.xsd")

with open(CACHED_SCHEMA_FILE, 'rb') as fhandle:
    SCHEMA_TREE = etree.parse(fhandle)


def strip_whitespace(string):
    """ Strip newline, tab and multple whitespace from a string
    """
    return re.sub(' +', ' ',
                  string.replace('\n', ' ').replace('\t', ' ').strip())


def get_enumeration_values_from_schema(attribute_name):
    """ Get the enumeration values associated with a given attribute name
        from the EarthChem SOAP schema
    """
    # Query looks for nodes with the given name that have a restriction
    # and then lists the enumerated values after that
    return SCHEMA_TREE.xpath(
        ('//xs:attribute[@name="{0}"]/xs:simpleType/xs:restriction/'
         'xs:enumeration/@value').format(attribute_name),
        namespaces={'xs': "http://www.w3.org/2001/XMLSchema"})


def get_documentation():
    """ Get query items and documentaton by scraping the EarthChem rest
        documentation
    """
    # Keys to ignore when constructing the query class
    ignore_values = (
        re.compile('Example.*'),
    )
    rest_doco_url = 'http://ecp.iedadata.org/rest_search_documentation/'

    # Construct request from EarthChem rest documentation
    url, schema = None, None
    cached_doco_file = pkg_resources.resource_filename(
        "pysiss.vocabulary.resources",
        "earthchem_rest_search_documentation.html")
    try:
        url = urllib.urlopen(rest_doco_url)
        schema = url.read()
        with open(cached_doco_file, 'wb') as fhandle:
            fhandle.write(schema)
    except IOError:
        # We can just use the cached version
        schema = open(cached_doco_file, 'rb')
    except Exception, err:
        print err
    finally:
        if url:
            url.close()

    # Parse schema for proper values
    soup, docs, restrictions = BeautifulSoup(schema), OrderedDict(), {}
    for item in soup.select('.itemtitle'):
        # Check that we actually want to keep this value
        itemname = strip_whitespace(item.contents[0])
        if any(map(lambda regex: regex.match(itemname),
                   ignore_values)):
            continue

        # Parse document string, add to dictionary
        itemdoc = strip_whitespace(item.contents[1].contents[0])
        docs[itemname] = itemdoc

        # Check whether the item is restricted in the values it can take
        allowed_vals = get_enumeration_values_from_schema(itemname)
        if allowed_vals:
            restrictions[itemname] = set(allowed_vals)

    return docs, restrictions


def _make_query_docstring():
    """ Constructs a docstring from the documentation dictionary
    """
    wrapper = textwrap.TextWrapper(width=80, subsequent_indent='    ')
    docstr = textwrap.dedent("""
        Holds a query for the EarthChem REST API

        Initialize by providing key-value pairs to build into a query URL. The
        URL is available in the `url` attribute, and the results from the
        `results` attribute.

        Providing a keyword not in the list below will raise a KeyError.

        Allowed keywords are:
        """)
    docdict, restrictions = get_documentation()
    for item in docdict.items():
        current_item_str = '{0} - {1}'.format(*item)
        if current_item_str.endswith('EarthChem SOAP search'):
            current_item_str = \
                current_item_str[:-len('in the EarthChem SOAP search')]
            current_item_str += (
                'by calling '
                'EarthChemQuery().restrictions["{0}"]'
            ).format(item[0])
        docstr += '\n' + wrapper.fill(current_item_str)
    return docstr


class EarthChemQuery(dict):

    __doc__ = _make_query_docstring()
    docdict, restrictions = get_documentation()
    _valid_keys = None

    def __init__(self, max_results=None, *args, **kwargs):
        self.max_results = max_results
        super(EarthChemQuery, self).__init__(*args, **kwargs)

    def __getitem__(self, key):
        self._check_key(key)
        try:
            return super(EarthChemQuery, self).__getitem__(key)
        except KeyError:
            return None

    def __setitem__(self, key, value):
        self._check_key(key)
        if key == 'outputtype':
            raise KeyError("If you change the output type to something other"
                           "than JSON I won't know how to parse the results "
                           "of the query.")
        if value is None and key in self.keys():
            del self[key]
        elif key in self.restrictions.keys() and \
                value not in self.restrictions[key].values:
            raise KeyError('Unknown value {0} for key {1}. Allowed '
                           'values are {2}'.format(value, key,
                                                   self.restrictions[key]))
        else:
            super(EarthChemQuery, self).__setitem__(key, value)

    @property
    def url(self):
        query_string = ('http://ecp.iedadata.org/restsearchservice?'
                        'outputtype=json&searchtype=rowdata&standarditems=yes')
        for item in self.items():
            query_string += '&{0}={1}'.format(*item)
        return query_string

    @property
    def result(self):
        """ Query the webservice using the current query

            Raises an IOError if the URL call fails.
        """
        # Function to make webservice call
        def get_slab(start, end):
            print 'Getting results {0} to {1}'.format(start, end - 1)
            url = self.url + \
                '&startrow={0}&endrow={1}'.format(index, end_index)
            return simplejson.load(urllib.urlopen(url))

        # Make a call to the webservice
        max_rows_per_call = 50  # EarthChem imposes this limit
        have_everything, index = False, 0
        results = []
        if self.max_results is not None:
            while len(results) < self.max_results:
                end_index = min(index + max_rows_per_call, self.max_results)
                slab = get_slab(index, end_index)
                results.extend(slab)
                if len(slab) < max_rows_per_call:
                    break
                else:
                    index += max_rows_per_call
        else:
            # We just loop til we run out of results from the server
            while True:
                end_index = index + max_rows_per_call
                slab = get_slab(index, end_index)
                results.extend(slab)
                if len(slab) < max_rows_per_call:
                    break
                else:
                    index += max_rows_per_call

        # Convert data to DataFrame, munge in floats
        results = pandas.DataFrame(results)
        for key in results.keys():
            if key not in ('sample_id', 'source'):
                results[key] = \
                    results[key].convert_objects(convert_numeric=True)
        return results

    def _check_key(self, key):
        """ Check that a key is a valid search parameter
        """
        if not self._valid_keys:
            self._valid_keys = set(self.docdict.keys())

        if key not in self._valid_keys:
            raise KeyError('Unknown key {0}'.format(key))
