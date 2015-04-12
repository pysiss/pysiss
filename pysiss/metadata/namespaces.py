""" file: xml_namespaces.py
    author: Jess Robertson
            CSIRO Mineral Resources Flagship
    date:   Monday 25 August, 2014

    description: namespace handling for XML and etree formats

    TODO: Pull unknown namespace definitions from XML file and add to registry
"""

from __future__ import print_function, division

import re
import pkg_resources
from lxml.etree import QName


class NamespaceMap(dict):

    """ Two-way dictionary to store shortened XML namespace keys

        This dictionary can be initialized by passing a dictionary or
        keyword-value pairs on initilization. These parameters are optional,
        an empty dictionary is created if neither of these are passed.

        Parameters:
            namespaces - a dict with each key referring to a shortened
                namespace, and the value referring to a URI representing that
                namespace (e.g. {'gsml': 'urn:cgi:xmlns:GCI:GeoSciML:2.0'}).
            **kwargs - keyword-value pairs specifying namespaces (e.g.
                gsml='urn:cgi:xmlns:GCI:GeoSciML:2.0').
    """

    def __init__(self, namespaces=None, **kwargs):
        super(NamespaceMap, self).__init__()
        self.inverse = dict(reversed(item) for item in self.items())

        # Init with namespace dictionaries
        if namespaces:
            self.update(namespaces)
        if kwargs:
            self.update(kwargs)

    def __setitem__(self, key, value):
        if key in (None, 'None', 'none', ''):
            # Use the namespaces from etree where possible, but sometimes a
            # namespace might map to None (if the default namespace) so we need
            # to assign it a shortened version so that xpath doesn't bork...
            self.add_from_url(value)

        else:
            # Make sure that all our namespaces are lowercase
            key = key.lower()

            # Add the keys to the mapping and the inverse
            super(NamespaceMap, self).__setitem__(key, value)
            self.inverse[value] = key

    def update(self, namespaces, **kwargs):
        """ Add new namespaces to the registry
        """
        # Add namespaces from dict
        for args in (namespaces, kwargs):
            for key, namespace_url in args.items():
                self[key] = namespace_url

    @property
    def stored_namespace_urls(self):
        """ Return a list of the stored namespace urls
        """
        return list(self.inverse.keys())

    @property
    def stored_namespace_keys(self):
        """ Return a list of the stored namespace keys8
        """
        return list(self.keys())

    def __delitem__(self, key):
        del self.inverse[self[key]]
        super(NamespaceMap, self).__delitem__(key)

    def regularize(self, tag, short_namespace=True):
        """ Return a namespace in shortened form, and lowercase.

            Note: if the tag has an associated namespace that isn't in the
            mapping, then it is added.

            Parameters:
                tag - the tag to regularize, in lxml format: '{ns}tag'
                short_namespace - whether you want the namespace to be expanded
                    or not (default is True for a short namespace).

            Returns:
                an lxml QName string which contains a regularized tag name
        """
        # Check input tag, try to assign a namespace and value
        try:
            tag = QName(tag)
            if tag.namespace not in (None, '', 'None'):
                if tag.namespace not in self.stored_namespace_urls:
                    print('Adding new namespace url {0}'.format(tag.namespace),
                          'keys: ', list(self.keys()))
                    self.add_from_url(tag.namespace)
        except ValueError:
            # the tag is already given as a shortened version
            if ':' in tag:
                namespace, localname = tag.split(':')
                if namespace not in self.stored_namespace_keys:
                    raise ValueError(
                        'Unknown namespace key {0}'.format(namespace)
                        + ' in tag {0}'.format(tag))
                else:
                    tag = QName(self[namespace], localname)
            else:
                tag = QName(None, localname)

        # Return regularized result
        localname = tag.localname.lower()
        if short_namespace and tag.namespace is not None:
            return QName(self.inverse[tag.namespace], localname)
        else:
            return QName(tag.namespace, localname)

    def add_from_url(self, namespace_uri):
        """ Shorten a namespace URL using some heuristics

            Plays nicely with namespace versions etc.

            Examples:
                "http://www.opengis.net/wfs" -> "wfs",
                "http://www.opengis.net/gml" -> "gml",
                "urn:cgi:xmlns:CGI:GeoSciML:2.0" -> "geosciml",
                "urn:cgi:xmlns:CGI:GeoSciML:22.0" -> "geosciml",
                "http://www.opengis.net/sampling/1.0" -> "sampling",
                "http://www.opengis.net/sampling/1.0.1" -> "sampling",
                "http://www.opengis.net/sampling/1.0.1alpha" -> "sampling",
                "http://www.w3.org/1999/xlink" -> "xlink"
        """
        # Get tokens from namespace
        if '://' in namespace_uri:
            # We have a namespace of the form protocol://root/ns/ns/ns/tag
            protocol, namespace = namespace_uri.replace('://', '@').split('@')
            tokens = namespace.split('/')
        elif ':' in namespace_uri:
            # We have a URN namespace of the form ns:ns:ns:ns:tag
            tokens = namespace_uri.split(':')
        else:
            raise ValueError("Can't shorten namespace "
                             "URI {0}".format(namespace_uri))

        # Find the shortened namespace - last token can often be a version number,
        # (e.g. maj.min.build*) so we just split on periods and look for that.
        last = tokens.pop()
        last_is_version = len(last.split('.')) > 1 and \
                          all([tk.isdigit() for tk in last.split('.')[:-1]])
        if last_is_version:
            version = last
            short_namespace = tokens.pop().lower()
        else:
            short_namespace = last.lower()
            version = tokens.pop()

        # Check that we don't already have this namespace/url combination
        # We need to qualify our namespace with another version
        nspaces, uris = set(self.keys()), set(self.inverse.keys())
        if short_namespace in nspaces:
            if namespace_uri not in uris:
                short_namespace = short_namespace + ':' + version

        # Add the latest mapping
        self[short_namespace] = namespace_uri
