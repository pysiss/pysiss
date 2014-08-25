""" file: xml_REGISTRY.expand.py

    description: namespace handling for XML and etree formats

    TODO: Pull unknown namespace definitions from XML file and add to registry
"""

from pysiss.utilities import Singleton


class NamespaceRegistry(dict):

    """ Registry for namespace objects
    """

    __metaclass__ = Singleton

    def __init__(self):
        super(NamespaceRegistry, self).__init__()
        self.update({
            'gsml': 'urn:cgi:xmlns:CGI:GeoSciML:2.0',
            'gml': 'http://www.opengis.net/gml',
            'wfs': "http://www.opengis.net/wfs",
            'sa': "http://www.opengis.net/sampling/1.0",
            'om': "http://www.opengis.net/om/1.0",
            'cgu': "urn:cgi:xmlns:CGI:DbUtils:1.0",
            'xlink': "http://www.w3.org/1999/xlink",
            'ns': "http://www.w3.org/XML/1998/namespace"
        })
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


def shorten_namespace(tag):
    """ Strip a namespace out of an XML tag and replace it with the shortcut
        version
    """
    ns, tag = split_namespace(tag)
    return _NAMESPACE_REGISTRY.inverse[ns] + ':' + tag


def expand_namespace(tag, form='xml'):
    """ Expand a tag's namespace
    """
    ns, tag = split_namespace(tag)
    if form == 'xml':
        return '{' + _NAMESPACE_REGISTRY[ns] + '}' + tag
    elif form == 'rdf':
        return _NAMESPACE_REGISTRY[ns] + ':' + tag
    else:
        raise ValueError(
            ('Unknown format type {0}. '
             'Allowed values are {1}').format(form, ['xml', 'rdf']))


def split_namespace(tag):
    """ Split a tag into a namespace and a tag
    """
    if tag.startswith('{'):
        # We have an expanded namespace to deal with
        ns, tag = tag.lstrip('{').split('}')
    elif tag.count(':') > 1:
        # We have an expanded namespace of the form ns:ns:ns:ns:tag
        tokens = tag.split(':')
        tag = tokens.pop()
        ns = ':'.join(tokens)
    elif tag.count(':') == 1:
        # We have a shortened namespaces of the form ns:tag
        ns, tag = tag.split(':')
    else:
        # Don't know what to do here? Just return None for namespace
        ns = None
    return ns, tag


__all__ = [add_namespace, shorten_namespace,
           expand_namespace, split_namespace]


if __name__ == '__main__':
    import unittest

    class TestXMLNamespaces(unittest.TestCase):

        """ Tests for XML namespace munging
        """

        def test_split_namespace(self):
            """ Test namespace splitting returns the right values
            """
            expected = ('urn:cgi:xmlns:CGI:GeoSciML:2.0', 'MappedFeature')
            self.assertEqual(
                split_namespace('urn:cgi:xmlns:CGI:GeoSciML:2.0:MappedFeature'),
                expected)
            self.assertEqual(
                split_namespace('{urn:cgi:xmlns:CGI:GeoSciML:2.0}MappedFeature'),
                expected)
            self.assertEqual(
                split_namespace('gsml:MappedFeature'),
                ('gsml', 'MappedFeature'))

        def test_shorten_namespace(self):
            """ Check namespace shortening
            """
            self.assertEqual(
                shorten_namespace('{http://www.opengis.net/gml}boundedBy'),
                'gml:boundedBy')

        def test_expand_namespace(self):
            """ Check namespace expansion
            """
            self.assertEqual(
                expand_namespace('gsml:MappedFeature'),
                '{urn:cgi:xmlns:CGI:GeoSciML:2.0}MappedFeature')
            self.assertEqual(
                expand_namespace('gsml:MappedFeature', form='rdf'),
                'urn:cgi:xmlns:CGI:GeoSciML:2.0:MappedFeature')

    unittest.main()
