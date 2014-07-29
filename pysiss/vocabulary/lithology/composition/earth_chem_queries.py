import urllib
import re
import pkg_resources
from bs4 import BeautifulSoup
import textwrap
from collections import OrderedDict


def strip_whitespace(string):
    """ Strip newline, tab and multple whitespace from a string
    """
    return re.sub(' +', ' ',
                  string.replace('\n', ' ').replace('\t', ' ').strip())


def get_documentation():
    """ Get query items and documentaton by scraping the EarthChem rest
        documentation
    """
    # Keys to ignore when constructing the query class
    ignore_values = (
        re.compile('Example.*'),
        re.compile('level[0-9]')
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
    soup, docs = BeautifulSoup(schema), OrderedDict()
    for item in soup.select('.itemtitle'):
        # Check that we actually want to keep this value
        itemname = strip_whitespace(item.contents[0])
        if any(map(lambda regex: regex.match(itemname),
                   ignore_values)):
            continue

        # Parse document string, add to dictionary
        itemdoc = strip_whitespace(item.contents[1].contents[0])
        docs[itemname] = itemdoc

    return docs


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
    docdict = get_documentation()
    for item in docdict.items():
        docstr += '\n' + wrapper.fill('{0} - {1}'.format(*item))
    return docstr


class EarthChemQuery(dict):

    __doc__ = _make_query_docstring()
    docdict = get_documentation()

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            # Check that items are ok to query
            if key not in self.docdict.keys():
                raise KeyError('Unknown key {0}'.format(key))

            # Add to dictionary
            self[key] = str(value)

    def __setitem__(self, key, value):
        if value is None:
            del self[key]
        else:
            super(EarthChemQuery, self).__setitem__(key, value)

    @property
    def url(self):
        query_string = ('http://ecp.iedadata.org/restsearchservice?'
                        'outputtype=json')
        for item in self.items():
            query_string += '&{0}={1}'.format(*item)
        return query_string

    @property
    def result(self):
        """ Query the webservice using the current query

            Raises an IOError if the URL call fails.
        """
        # Make a call to the webservice
        results = simplejson.load(urllib.urlopen(self.url))

        # Parse the data from that
