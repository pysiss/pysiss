""" file:   metadata.py (pysiss.metadata)
    author: Jess Robertson
            CSIRO Minerals Resources Flagship
    date:   Wednesday 27 August, 2014

    description: Functions to deal with gsml:geologicFeature data

    Geologic features can be shared by many different objects, so it makes
    sense to seperate these out into a seperate registry.
"""

from ..utilities import id_object
from .registry import MetadataRegistry
from .namespaces import NamespaceMap

from copy import deepcopy
from lxml import etree
from StringIO import StringIO

def qname_str(qname):
    """ Represent a QName in a namespace:localname string
    """
    if qname.namespace not in (None, 'None'):
        result = '{0}:{1}'.format(qname.namespace, qname.localname)
    else:
        result = '{0}'.format(qname.localname)
    return result


def yamlify(mdata, nsmap, indent_width=2, indent=0):
    """ Convert an ETree instance into a YAML-esque representation

        Parameters
            mdata - an Metadata instance
            indent_width - with of a single indent step in characters
            indent - initial number of indentations
    """
    # Build line for current element
    spaces = ' ' * indent_width * indent
    result = spaces + qname_str(nsmap.regularize(mdata.tag))

    # Add lines for text
    if mdata.text and mdata.text.strip() != '':
        result += ' {0}'.format(mdata.text)

    # ... and metadata
    if mdata.attrib:
        for key in mdata.attrib.keys():
            qname = qname_str(nsmap.regularize(key, short_namespace=True))
            result += '\n' + spaces + ' ' * indent_width + \
                      '@{0}: {1}'.format(qname, mdata.attrib[key])

    # Add lines for children
    result += '\n'
    for child in mdata.getchildren():
        result += yamlify(child, nsmap,
                          indent_width=indent_width,
                          indent=indent + 1)
    return result


class Metadata(id_object):

    """ Class to store metadata record

        Parameters:
            xml - either a handle to an open xml file, or a string of XML.
                Optional, but one of 'xml' or tree must be specified.
            tree - either an etree.ElementTree or etree.Element instance
                containing already-parsed data. Optional, but one of 'xml' or
                tree must be specified.
            dtype - the datatype for the metadata. Optional, if not specified
                the tag of the root of the metadata tree will be used.
            ident - a unique identifier for the metadata. Optional, one will
                be generated for the instance if not specified.
            **kwargs - arbitrary attributes to attach to the metadata instance
    """

    registry = MetadataRegistry()

    def __init__(self, xml=None, tree=None, dtype=None, ident=None,
                 **kwargs):
        super(Metadata, self).__init__()
        self.ident = ident or self.uuid

        # Slurp in data
        if xml is not None:
            self.tree, self.namespaces = self.parse(xml)
        elif tree is not None:
            if type(tree) is etree._ElementTree:
                self.tree, self.namespaces = tree, NamespaceMap(tree.nsmap)
            elif type(tree) is etree._Element:
                self.tree = etree.ElementTree(tree)
                self.namespaces = NamespaceMap(tree.nsmap)
            else:
                raise ValueError("Argument to 'tree' in Metadata constructor "
                                 "is not of type lxml.etree.ElementTree or "
                                 "lxml.etree.Element (it's type is "
                                 "{0})".format(type(tree)))
        else:
            raise ValueError('One of tree or xml has to be specified to '
                             'create a Metadata instance')

        # Store other metadata
        for attr in ('tag', 'attrib', 'text'):
            setattr(self, attr, getattr(self.tree.getroot(), attr))
        for attrib, value in kwargs.items():
            setattr(self, attrib, value)

        # Register yourself with the registry
        if dtype is not None:
            self.dtype = dtype.lower()
        else:
            self.dtype = self.tag
        self.registry.register(self)

    def __str__(self):
        """ String representation
        """
        template = 'Metadata record {0}, of datatype {1}\n{2}'
        return template.format(self.ident, self.dtype, self.tree)

    def get(self, attribute):
        """ Get the value of the given attribute
        """
        return self.attrib.get(attribute)

    def parse(self, xml):
        """ Parse some XML containing a metadata record

            Parameters:
                xml - either a handle to an open xml file, or a string of XML

            Returns:
                a tuple containing an lxml.etree.ElementTree instance holding
                the parsed data, and a pysiss.metadata.NamespaceMap instance
                holding the namespace urls and keys
        """
        # Initialize tree and XML namespaces
        if not isinstance(xml, file):
            xml = StringIO(xml)
        nspace = NamespaceMap()

        # Process root first, stash for later
        context = iter(etree.iterparse(xml, events=('end', 'start-ns'),
                                       remove_comments=True,
                                       recover=True))

        # Walk tree and generate parsing events to normalize tags
        for event, elem in context:
            if event == 'start-ns':
                nskey, nsurl = elem  # start-ns elem is a tuple
                nspace[nskey] = nsurl
            else:
                elem.tag = nspace.regularize(elem.tag, short_namespace=False)
        return etree.ElementTree(elem), nspace

    def xpath(self, *args, **kwargs):
        """ Pass XPath queries through to underlying tree

            Uses the namespace dictionary from the metadata tree
            to expand namespace definitions

            Parameters: see lxml.etree.xpath for details
        """
        if 'namespaces' in kwargs.keys():
            kwargs['namespaces'].update(self.namespaces)
        else:
            kwargs.update(namespaces=self.namespaces)

        # We need to check that we've actually got back element tree elements
        # before trying to wrap in a Metadata instance - xpath results may be
        # strings!
        results = []
        for result in self.tree.xpath(*args, **kwargs):
            try:
                results.append(Metadata(tree=result))
            except ValueError:
                results.append(result)
        return results

    def find(self, *args, **kwargs):
        """ Pass ElementPath queries through to underlying tree
        """
        if 'namespaces' in kwargs.keys():
            kwargs['namespaces'].update(self.namespaces)
        else:
            kwargs.update(namespaces=self.namespaces)
        return Metadata(tree=self.tree.find(*args, **kwargs))

    def findall(self, *args, **kwargs):
        """ Pass ElementPath queries through to underlying tree
        """
        if 'namespaces' in kwargs.keys():
            kwargs['namespaces'].update(self.namespaces)
        else:
            kwargs.update(namespaces=self.namespaces)
        return map(lambda x: Metadata(tree=x),
                   self.tree.findall(*args, **kwargs))

    def yaml(self, indent_width=2):
        """ Return a YAML-like representation of the tags

            Parameters:
                indent_width - the number of spaces in each indent level.
                    Optional, defaults to 2.

            Returns:
                a string reprentation of the metadata tree
        """
        return yamlify(self.tree.getroot(), self.namespaces,
                       indent_width=indent_width)
