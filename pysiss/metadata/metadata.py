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
from .namespaces import Namespace

from copy import deepcopy
from lxml import etree
from StringIO import StringIO


def yamlify(mdata, namespace, indent_width=2, indent=0):
    """ Convert an Metadata instance into a YAML-esque representation

        Parameters
            mdata - an Metadata instancw
            indent_width - with of a single indent step in characters
            indent - initial number of indentations
    """
    # Build line for current element
    spaces = ' ' * indent_width * indent
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
            tree_or_string - either an XML etree instance, or a
                string containing some XML.
            mdatatype - the datatype for the metadata
            ident - a unique identifier for the metadata. Optional, one will
                be generated for the instance if not specified.
            **kwargs - arbitrary attributes to attach to the metadata instance
    """

    registry = MetadataRegistry()
    ns = Namespace()
    parser = etree.XMLParser(remove_comments=True, recover=True)

    def __init__(self, tree_or_string, mdatatype=None, ident=None, **kwargs):
        super(Metadata, self).__init__()
        self.ident = ident or self.uuid

        # Normalize tree tags
        self.tree = None
        self._init_normalized_etree(tree_or_string)

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
            kwargs['namespaces'].update(self.ns)
        else:
            kwargs.update(namespaces=self.ns)
        return self.tree.xpath(*args, **kwargs)

    def find(self, *args, **kwargs):
        """ Pass ElementPath queries through to underlying tree
        """
        if 'namespaces' in kwargs.keys():
            kwargs['namespaces'].update(self.ns)
        else:
            kwargs.update(namespaces=self.ns)
        return self.tree.find(*args, **kwargs)

    def findall(self, *args, **kwargs):
        """ Pass ElementPath queries through to underlying tree
        """
        if 'namespaces' in kwargs.keys():
            kwargs['namespaces'].update(self.ns)
        else:
            kwargs.update(namespaces=self.ns)
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
                       namespace=self.ns,
                       indent_width=indent_width)

    def _normalize(self, elem):
        """ Normalize the tag for a given element

            Parameters:
                elem - the element to normalize
        """
        new = deepcopy(elem)
        try:
            new.tag = self.ns.expand(self.ns.regularize(elem.tag),
                                     form='xml')
        except ValueError:
            reg = self.ns.regularize(elem.tag)
            string = 'Having trouble normalizing {0}'.format(elem.tag)
            string += '\nRegularized: {0}'.format(reg)
            string += '\nExpanded: {0}'.format(self.ns.expand(reg, form='xml'))
            string += '\nNamespaces: {0}'.format(self.ns)
            raise ValueError(string)
        for child in new.getchildren():
            new.replace(child, self._normalize(child))
        return new

    def _init_normalized_etree(self, data):
        """ Generate a normalized etree from an existing etree or string

            Parameters:
                data - either an lxml.etree.ElementTree instance, an
                    lxml.Element pointing to the root of a tree, or a string
                    containing raw XML data.
        """
        if isinstance(data, basestring):
            # Parse the string first
            tree = etree.parse(StringIO(data), parser=self.parser)
            self.ns.update(tree.getroot().nsmap)
            self.tree = self._normalize(tree.getroot())

        # Matching on etree._ElementTree feels super kludgy here
        elif isinstance(data, etree._ElementTree):
            self.ns.update(data.getroot().nsmap)
            self.tree = self._normalize(data.getroot())

        elif isinstance(data, etree._Element):
            self.ns.update(data.nsmap)
            self.tree = self._normalize(data)

        else:
            raise ValueError("Don't know what to do with this {0}".format(arg))
