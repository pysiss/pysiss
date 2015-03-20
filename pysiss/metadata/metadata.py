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
    """ Convert an Metadata instance into a YAML-esque representation

        Parameters
            mdata - an Metadata instance
            indent_width - with of a single indent step in characters
            indent - initial number of indentations
    """
    # Build line for current element
    spaces = ' ' * indent_width * indent
    tag = QName(mdata.tag)
    result = spaces + '{0}:'.format(nsmap)

    result = spaces + '{0}:'.format(namespace.regularize(mdata.tag))
    if mdata.text and mdata.text.strip() != '':
        result += ' {0}\n'.format(mdata.text)
    elif mdata.attrib:
        mdata_attrs = dict(mdata.attrib)
        for key, value in mdata.attrib.items():
            old_key = key
            key = namespace.regularize(key)
            if key != old_key:
                mdata_attrs[key] = value
                del mdata_attrs[old_key]
        result += '\n' + spaces + ' ' * indent_width
        result += '  {0}\n'.format(mdata_attrs)
    else:
        result += '\n'

    # Add lines for children
    for child in mdata.getchildren():
        result += yamlify(child, namespace,
                          indent_width=indent_width,
                          indent=indent + 1)
    return result


class Metadata(id_object):

    """ Class to store metadata record

        Parameters:
            xml - either a handle to an open xml file, or a string of XML
            mdatatype - the datatype for the metadata
            ident - a unique identifier for the metadata. Optional, one will
                be generated for the instance if not specified.
            **kwargs - arbitrary attributes to attach to the metadata instance
    """

    registry = MetadataRegistry()
    parser = etree.XMLParser(remove_comments=True, recover=True)

    def __init__(self, xml, mdatatype=None, ident=None, **kwargs):
        super(Metadata, self).__init__()
        self.ident = ident or self.uuid

        # Initialize tree and XML namespaces
        if not isinstance(xml, file):
            xml = StringIO(xml)

        # Slurp in data
        self.tree = etree.parse(xml, parser=self.parser)
        self.namespaces = NamespaceMap(self.tree.getroot().nsmap)

        # Store other metadata
        for attrib, value in kwargs.items():
            setattr(self, attrib, value)

        # Register yourself with the registry
        if mdatatype is not None:
            self.mdatatype = mdatatype.lower()
            self.registry.register(self)

    def __str__(self):
        """ String representation
        """
        template = 'Metadata record {0}, of datatype {1}\n{2}'
        return template.format(self.ident, self.mdatatype, self.tree)

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
        return self.tree.xpath(*args, **kwargs)

    def find(self, *args, **kwargs):
        """ Pass ElementPath queries through to underlying tree
        """
        if 'namespaces' in kwargs.keys():
            kwargs['namespaces'].update(self.namespaces)
        else:
            kwargs.update(namespaces=self.namespaces)
        return self.tree.find(*args, **kwargs)

    def findall(self, *args, **kwargs):
        """ Pass ElementPath queries through to underlying tree
        """
        if 'namespaces' in kwargs.keys():
            kwargs['namespaces'].update(self.namespaces)
        else:
            kwargs.update(namespaces=self.namespaces)
        return self.tree.findall(*args, **kwargs)

    def yaml(self, indent_width=2):
        """ Return a YAML-like representation of the tags

            Parameters:
                indent_width - the number of spaces in each indent level.
                    Optional, defaults to 2.

            Returns:
                a string reprentation of the metadata tree
        """
        return yamlify(self.tree,
                       namespace=self.namespaces,
                       indent_width=indent_width)
