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


def yamlify(tree, indent_width=2, indent=0):
    """ Convert a ElementTree into a YAML-esque representation

        Parameters
            tree - an lxml.etree.ElementTree instance
            indent_width - with of a single indent step in characters
            indent - initial number of indentations
    """
    # Build line for current element
    spaces = ' ' * indent_width * indent
    result = spaces + '{0}:'.format(tree.tag)
    if tree.text and tree.text.strip() != '':
        result += ' {0}\n'.format(tree.text)
    elif tree.attrib:
        tree_attrs = dict(tree.attrib)
        for key, value in tree.attrib.items():
            old_key = key
            key = regularize(key)
            if key != old_key:
                tree_attrs[key] = value
                del tree_attrs[old_key]
        result += '\n' + spaces + ' ' * indent_width
        result += '  {0}\n'.format(tree_attrs)
    else:
        result += '\n'

    # Add lines for children
    for child in tree.getchildren():
        result += yamlify(child,
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
    namespace = Namespace()
    parser = etree.XMLParser(remove_comments=True, recover=True)

    def __init__(self, tree_or_string, mdatatype, ident=None, **kwargs):
        self.mdatatype = mdatatype.lower()
        super(Metadata, self).__init__(ident=self.mdatatype)
        self.ident = ident or self.uuid

        # Normalize tree tags
        self.tree = self._init_normalized_etree(tree_or_string)

        # Store other metadata
        for attrib, value in kwargs.items():
            setattr(self, attrib, value)

        # Register yourself with the registry
        self.registry.register(self)

    def __str__(self):
        template = 'Metadata record {0}, of datatype {1}\n{2}'
        return template.format(self.ident, self.mdatatype, self.tree)

    def xpath(self, *args, **kwargs):
        """ Pass XPath queries through to underlying tree

            Uses the namespace dictionary from the metadata tree
            to expand namespace definitions
        """
        if 'namespaces' in kwargs.keys():
            kwargs['namespaces'].update(self.namespace)
        else:
            kwargs.update(namespaces=self.namespace)
        return self.tree.xpath(*args, **kwargs)

    def find(self, *args, **kwargs):
        """ Pass ElementPath queries through to underlying tree
        """
        if 'namespaces' in kwargs.keys():
            kwargs['namespaces'].update(self.namespace)
        else:
            kwargs.update(namespaces=self.namespace)
        return self.tree.find(*args, **kwargs)

    def yaml(self, indent_width=2):
        """ Return a YAML-like representation of the tags

            Parameters

            Returns:
                a string reprentation of the metadata tree
        """
        return yamlify(self.tree, indent_width=indent_width)

    def _normalize(self, elem):
        """ Normalize the tag for a given element
        """
        new = deepcopy(elem)
        try:
            new.tag = self.namespace.expand_namespace(
                self.namespace.regularize(elem.tag), form='xml')
        except ValueError:
            raise ValueError("Don't know how to normalize {0}".format(new.tag))

        for child in new.getchildren():
            new.replace(child, self._normalize(child))
        return new

    def _init_normalized_etree(self, data):
        """ Generate a normalized etree from an existing etree or string

            Parameters:
                data - either an lxml.etree.ElementTree instance, or a string
                    containing raw XML data.
        """
        if isinstance(data, basestring):
            # Parse the string first
            tree = etree.parse(StringIO(data), parser=self.parser)
            return self._normalize(tree.getroot())

        elif isinstance(data, etree.ElementTree):
            return self._normalize(data)

        else:
            raise ValueError("Don't know what to do with this {0}".format(arg))
