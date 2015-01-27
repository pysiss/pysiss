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
from .namespaces import shorten_namespace


def yamlify(tree, indent_width=2, indent=0):
    """ Convert an etree into a YAML-esque representation

        Parameters
            tree - an etree instance (try lxml.etree.Etree)
            indent_width - with of a single indent step in characters
            indent - initial number of indentations
    """
    # Build line for current element
    spaces = ' ' * indent_width * indent
    result = spaces + '{0}:'.format(shorten_namespace(tree.tag))
    if tree.text and tree.text.strip() != '':
        result += ' {0}\n'.format(tree.text)
    elif tree.attrib:
        tree_attrs = dict(tree.attrib)
        for key, value in tree.attrib.items():
            old_key = key
            key = shorten_namespace(key)
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
    """

    registry = MetadataRegistry()

    def __init__(self, tree, mdatatype, ident=None, **kwargs):
        self.mdatatype = mdatatype.lower()
        super(Metadata, self).__init__(ident=self.mdatatype)
        self.ident = ident or self.uuid
        self.tree = tree

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
        """
        return self.tree.xpath(*args, **kwargs)

    def find(self, *args, **kwargs):
        """ Pass ElementPath queries through to underlying tree
        """
        return self.tree.find(*args, **kwargs)

    def pretty(self, indent_width=2):
        """ Return a YAML-like representation of the tags

            Parameters
                indent_width - with of a single indent step in characters

            Returns:
                a string reprentation of the metadata tree
        """
        return yamlify(self.tree, indent_width=indent_width)
