""" file: xml_namespaces.py
    author: Jess Robertson
            CSIRO Mineral Resources Flagship
    date:   Monday 25 August, 2014

    description: namespace handling for XML and etree formats

    TODO: Pull unknown namespace definitions from XML file and add to registry
"""

from __future__ import print_function, division

from lxml import etree


class NamespaceMap(dict):

    """ Two-way dictionary to store shortened XML namespace keys

        This dictionary can be initialized by passing a dictionary or
        keyword-value pairs on initilization. These parameters are optional,
        an empty dictionary is created if neither of these are passed.

        Parameters:
            *namespaces - a list of URIs to refer to.
            **kwargs - keyword-value pairs specifying namespaces (e.g.
                gsml='urn:cgi:xmlns:GCI:GeoSciML:2.0').
    """

    def __init__(self, *namespaces, **kwargs):
        super(NamespaceMap, self).__init__()
        self.inverse = dict(reversed(item) for item in self.items())

        # Init with namespace dictionaries
        for namespace in namespaces:
            try:
                # If we've been tossed a tag, split it first
                # Will raise a ValueError if not a Name
                qname = etree.QName(namespace)
                if qname.namespace:
                    self.add_from_uri(qname.namespace)
                else:
                    continue

            except ValueError:
                self.add_from_uri(namespace)

        if kwargs:
            self.update(kwargs)

        # Init internal variables
        self._cached = False
        self._stored_uris, self._stored_namespaces = set(), set()

    def __str__(self):
        return super(NamespaceMap, self).__str__()

    def __repr__(self):
        return super(NamespaceMap, self).__repr__()

    def __setitem__(self, key, value):
        """ Associate the given shortened namespace with the given
            namespace URI.

            If key is None, 'None', 'none' or '', then a key is generated, i.e.
            so that `nsmap[None] = 'some/uri'` does the same thing as
            `nsmap.add_from_uri('some/uri')`. This is done because sometimes
            a namespace can map to an empty prefix.
        """
        if key in (None, 'None', 'none', ''):
            # Use the namespaces from etree where possible, but sometimes a
            # namespace might map to None (if the default namespace) so we need
            # to assign it a shortened version so that xpath doesn't bork...
            self.add_from_uri(value)

        else:
            # Make sure that all our namespaces are lowercase
            key = key.lower()

            # Add the keys to the mapping and the inverse
            super(NamespaceMap, self).__setitem__(key, value)
            self.inverse[value] = key

        # Invalidate cache for later
        self._cached = False

    def update(self, namespaces, **kwargs):
        """ Add new namespaces to the registry

            Parameters:
                namespaces - a dictionary of namespace instances
                **kwargs - key/namespace pairs
        """
        # Add namespaces from dict
        for args in (namespaces, kwargs):
            for key, namespace_url in args.items():
                self[key] = namespace_url

    def _update_cache(self):
        """ Update the cached namespace urls and keys
        """
        if not self._cached:
            self._stored_namespaces = set(self.keys())
            self._stored_uris = set(self.inverse.keys())
            self._cached = True

    def harvest_namespaces(self, elem):
        """ Harvest namespace definitions from an lxml tree

            Parameters:
                elem - an lxml.etree.Element instance
        """
        # Add namespaces from tag and attributes
        self.add_from_tag(elem.tag)
        if elem.attrib:
            for key, value in elem.attrib.items():
                self.add_from_tag(key)
                self.add_from_tag(value)

        # Harvest namespaces from children
        for child in elem.getchildren():
            self.harvest_namespaces(child)

    @property
    def stored_namespace_uris(self):
        """ Return a set of the stored namespace urls
        """
        self._update_cache()
        return self._stored_uris

    @property
    def stored_namespace_keys(self):
        """ Return a set of the stored namespace keys
        """
        self._update_cache()
        return set(self.keys())

    def __delitem__(self, key):
        del self.inverse[self[key]]
        super(NamespaceMap, self).__delitem__(key)
        self._cached = False

    def expand(self, tag):
        """ Return a tag with a namespace in expanded form

            Parameters:
                tag - the tag to regularize, in lxml format: 'ns:tag'

            Returns:
                an lxml QName string which contains a regularized tag name
        """
        namespace, localname = tag.split(':')
        if namespace not in self.stored_namespace_keys:
            raise ValueError(
                'Unknown namespace key {0}'.format(namespace)
                + ' in tag {0}'.format(tag))
        else:
            return etree.QName(self[namespace], localname)

    def shorten(self, tag):
        """ Return a tag with a namespace in shortened form.

            Note: if the tag has an associated namespace that isn't in the
            mapping, then it is added.

            Parameters:
                tag - the tag to regularize, in lxml format: '{ns}tag'
                short_namespace - whether you want the namespace to be expanded
                    or not (default is True for a short namespace).

            Returns:
                an lxml etree.QName string which contains a regularized tag name
        """
        # Check input tag, try to assign a namespace and value
        try:
            qname = etree.QName(tag)
            if qname.namespace not in (None, '', 'None'):
                # Check whether we should add the uri
                if qname.namespace not in self.stored_namespace_uris:
                    self.add_from_uri(qname.namespace)
                return self.inverse[qname.namespace] + ':' + qname.localname
            else:
                raise ValueError()
        except ValueError:
            return tag

    def add_from_tag(self, tag):
        """ Add a namespace from an lxml tag.

            The namespace is denoted using lxml's `{namespace}tag` qname
            specification. This is really just a convenience wrapper -
            the tag is passed to lxml.etree.QName and then the namespace is passed
            off to the `add_from_uri` method. To see what the shortened namespace
            will look like then check out the documentation for `add_from_uri`.

            If the tag has no namespace then nothing is done

            Parameters:
                tag - the (namespaced) tag containing the tag to be added
        """
        try:
            qname = etree.QName(tag)
            if qname.namespace:
                self.add_from_uri(qname.namespace)
        except ValueError:
            pass

    def add_from_uri(self, namespace_uri):
        """ Shorten a namespace URI using some heuristics

            Shortened namespace will be a lowercase version of the
            last word in the URI (e.g. "http://foo/bar/baz" -> "baz")

            Version numbers are skipped, so namespaces ending with a version
            number will shorten to the same base (e.g. this tag shortens as
            "{http://foo/bar/baz/2.0}quux" -> "baz:quux"). Version numbers are
            defined as numbers seperated by periods, except for the last value
            which can be a string (to catch version numbers like 1.0.2dev).

            If a different version of the same namespace is already present,
            then new versions will have a version number appended present in
            the dataset: "http://foo/bar/baz/1.0/quux" -> "baz:quux" and then
            "http://foo/bar/baz/2.0/quux" -> "baz:2.0:quux". This could mean
            that you won't know what the namespace is ahead of time - if this
            is important for you (i.e. you're trying to write parsing code)
            then try not to mix different versions of the same namespace.

            Also plays nicely with URNs. It will tokenize on '/' if '://' is in
            the string, and tokenize on ':' otherwise.

            Some more examples:

                "http://www.opengis.net/wfs" -> "wfs",
                "http://www.opengis.net/gml" -> "gml",
                "http://www.w3.org/1999/xlink" -> "xlink"

                "urn:cgi:xmlns:CGI:GeoSciML:2.0" -> "geosciml",
                "urn:cgi:xmlns:CGI:GeoSciML:22.0" -> "geosciml:22.0",

                "http://www.opengis.net/sampling/1.0" -> "sampling",
                "http://www.opengis.net/sampling/1.0.1" -> "sampling:1.0.1",
                "http://www.opengis.net/sampling/1.0.1alpha"
                    -> "sampling:1.0.1alpha",

            Parameters:
                namespace_uri - a URI denoting a namespace
        """
        # Can shortcut if we already have this namespace
        if namespace_uri in self.stored_namespace_uris:
            return

        # Get tokens from namespace
        if '://' in namespace_uri:
            # We have a namespace of the form protocol://root/ns/ns/ns/tag
            _, namespace = namespace_uri.replace('://', '@').split('@')
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
