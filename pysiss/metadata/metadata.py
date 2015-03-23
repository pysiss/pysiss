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


def yamlify(mdata, nsmap, indent_width=2, indent=0):
    """ Convert an ETree instance into a YAML-esque representation

        Parameters
            mdata - an Metadata instance
            indent_width - with of a single indent step in characters
            indent - initial number of indentations
    """
    # Build line for current element
    spaces = ' ' * indent_width * indent
    tag = nsmap.regularize(mdata.tag, short_namespace=True)
    if tag.namespace is not None:
        result = spaces + '{0}:{1}:'.format(tag.namespace, tag.localname)
    else:
        result = spaces + '{1}:'.format(tag.localname)

    # Add lines for text
    if mdata.text and mdata.text.strip() != '':
        result += ' {0}'.format(mdata.text)

    # ... and metadata
    if mdata.attrib:
        for key in mdata.attrib.keys():
            qname = nsmap.regularize(key, short_namespace=True)
            if qname.namespace not in (None, 'None'):
                attrib = '@{0}:{1}: {2}'.format(qname.namespace,
                                               qname.localname,
                                               mdata.attrib[key])
            else:
                attrib = '@{0}: {1}'.format(qname.localname,
                                           mdata.attrib[key])
            result += '\n' + spaces + ' ' * indent_width + attrib

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
            dtype - the datatype for the metadata. Optional but if
                specified will cause the metadata to be registered with the
                metadata registry under this datatype.
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
            self.tree, self.namespaces = tree, NamespaceMap(tree.nsmap)
        self.tag = self.tree.getroot().tag

        # Store other metadata
        for attrib, value in kwargs.items():
            setattr(self, attrib, value)

        # Register yourself with the registry
        if dtype is not None:
            self.dtype = dtype.lower()
            self.registry.register(self)

    def __str__(self):
        """ String representation
        """
        template = 'Metadata record {0}, of datatype {1}\n{2}'
        return template.format(self.ident, self.dtype, self.tree)

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
        context = iter(etree.iterparse(xml,
                                       remove_comments=True,
                                       recover=True))

        # Walk tree and generate parsing events to normalize tags
        for _, elem in context:
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
        return map(self._to_metadata, self.tree.xpath(*args, **kwargs))

    def find(self, *args, **kwargs):
        """ Pass ElementPath queries through to underlying tree
        """
        if 'namespaces' in kwargs.keys():
            kwargs['namespaces'].update(self.namespaces)
        else:
            kwargs.update(namespaces=self.namespaces)
        return map(self._to_metadata, self.tree.find(*args, **kwargs))

    def findall(self, *args, **kwargs):
        """ Pass ElementPath queries through to underlying tree
        """
        if 'namespaces' in kwargs.keys():
            kwargs['namespaces'].update(self.namespaces)
        else:
            kwargs.update(namespaces=self.namespaces)
        return map(self._to_metadata, self.tree.findall(*args, **kwargs))

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

    def _to_metadata(self, elem, nsmap=None):
        """ Converts an etree element to a Metadata instance with appropriate
            namespace etc.

            Parameters:
                elem - an etree.Element instance to convert to a Metadata
                    instance
                nsmap - a NamespaceMap instance, optional, if not specified
                    then the current namespace map is used

            Returns:
                The constructed Metadata instance
        """
        result = Metadata()
        result.tree = elem
        result.namespaces = nsmap or self.namespaces
        return result
