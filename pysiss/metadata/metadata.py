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


class Metadata(id_object):

    """ Class to store metadata record
    """

    registry = MetadataRegistry()

    def __init__(self, ident, tree, type, **kwargs):
        super(Metadata, self).__init__(name=type)
        self.ident = ident or self.uuid
        self.tree = tree
        self.type = type

        # Store other metadata
        for attrib, value in kwargs.items():
            setattr(self, attrib, value)

        # Register yourself with the registry
        self.registry.register(self)

    def __str__(self):
        template = 'Metadata record {0}, of type {1}\n{2}'
        return template.format(self.ident, self.type, self.ttree)

    def xpath(self, *args, **kwargs):
        """ Pass XPath queries through to underlying tree
        """
        return self.tree.xpath(*args, **kwargs)

    def find(self, *args, **kwargs):
        """ Pass ElementPath queries through to underlying tree
        """
        return self.tree.find(*args, **kwargs)

    @property
    def tag_tree(self):
        """ Return a YAML-like representation of the tags
        """
        pass
