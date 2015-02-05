""" file: xml_namespaces.py
    author: Jess Robertson
            CSIRO Mineral Resources Flagship
    date:   Monday 25 August, 2014

    description: namespace handling for XML and etree formats

    TODO: Pull unknown namespace definitions from XML file and add to registry
"""

import simplejson
import pkg_resources
from ..utilities import Singleton


class NamespaceRegistry(dict):

    """ Registry for namespace objects
    """

    __metaclass__ = Singleton

    # Load default namespaces list in namespaces.json
    default_namespaces = simplejson.load(
        pkg_resources.resource_stream(
            "pysiss.metadata", "namespaces.json"))

    def __init__(self):
        super(NamespaceRegistry, self).__init__()
        self.update(self.default_namespaces)
        self.inverse = dict(reversed(item) for item in self.items())

    def __setitem__(self, key, value):
        super(NamespaceRegistry, self).__setitem__(key, value)
        self.inverse[value] = key

    def __delitem__(self, key):
        del self.inverse[self[key]]
        super(NamespaceRegistry, self).__delitem__(key)


_NAMESPACE_REGISTRY = NamespaceRegistry()


def add_namespace(abbrev, url):
    """ Add an XML namespace to the registry
    """
    _NAMESPACE_REGISTRY[abbrev] = url


def split_namespace(tag):
    """ Split a tag into a namespace and a tag
    """
    # : and / have special delimiter status unless part of http:// spec
    tag = tag.replace('://', '@')

    try:
        if tag.startswith('{'):
            # We have an expanded namespace to deal with
            nspace, tag = tag.lstrip('{').split('}')
        elif ':' in tag:
            # We have a URIi namespace of the form ns:ns:ns:ns:tag
            tokens = tag.split(':')
            tag = tokens.pop()
            nspace = ':'.join(tokens).replace('http_', 'http:')
        elif '/' in tag:
            # We have a namespace of the form root/ns/ns/ns/tag
            tokens = tag.split('/')
            tag = tokens.pop()
            nspace = '/'.join(tokens)
        else:
            # Don't know what to do here? Just return None for namespace
            nspace = None
    except AttributeError, err:
        print tag
        raise err

    # Reinstate :// string
    if nspace:
        nspace = nspace.replace('@', '://')
    return nspace, tag


def shorten_namespace(tag):
    """ Strip a namespace out of an XML tag and replace it with the shortcut
        version
    """
    nspace, tag = split_namespace(tag)
    try:
        return _NAMESPACE_REGISTRY.inverse[nspace] + ':' + tag
    except KeyError:
        if nspace is not None:
            # We need to check whether we have some of the namespace already
            # So we re-run on the namespace recursively
            return shorten_namespace(nspace) + ':' + tag

        else:
            # We can't do anything with this one, just return the tag
            return tag


def expand_namespace(tag, form=None):
    """ Expand a tag's namespace
    """
    tokens = tag.strip().split(':')
    try:
        nspace = _NAMESPACE_REGISTRY[tokens[0]]
        tag = ':'.join(tokens[1:])
    except KeyError:
        # We can't do anything with this tag, so just return it
        return tag

    if form is None or form == 'xml':
        tag_tokens = tag.split(':')
        if ":" in nspace.replace('://', ''):
            return '{' + ':'.join([nspace] + tag_tokens[:-1]) + '}' + tag_tokens[-1]
        elif "/" in nspace.replace('://', ''):
            return '{' + '/'.join([nspace] + tag_tokens[:-1]) + '}' + tag_tokens[-1]
    elif form == 'rdf':
        tag_tokens = tag.split(':')
        if ":" in nspace.replace('://', ''):
            return ':'.join([nspace] + tag_tokens[:-1]) + ':' + tag_tokens[-1]
        elif "/" in nspace.replace('://', ''):
            return '/'.join([nspace] + tag_tokens[:-1]) + ':' + tag_tokens[-1]
        return nspace + ':' + tag
    else:
        raise ValueError(
            ('Unknown format type {0}. '
             'Allowed values are {1}').format(form, ['xml', 'rdf']))
