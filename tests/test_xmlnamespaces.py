""" file: test_xmlnamespaces.py
    author: Jess Robertson
            CSIRO Earth Science and Resource Engineering
    date: Tuesday May 14, 2013

    description: unittests for namespace maps
"""


from __future__ import print_function, division

from pysiss.metadata.namespaces import NamespaceMap

import unittest


class TestXMLNamespaces(unittest.TestCase):

    """ Tests for XML namespace munging
    """

    def setUp(self):
        self.ns = NamespaceMap({
            'om': 'http://www.opengis.net/om/1.0',
            'ows': 'http://www.opengis.net/ows/1.0',
            'gml': 'http://www.opengis.net/gml',
            'xlink': 'http://www.w3.org/1999/xlink',
            'geosciml': 'urn:cgi:xmlns:CGI:GeoSciML:2.0',
            'wfs': 'http://www.opengis.net/wfs',
            'sa': 'http://www.opengis.net/sampling/1.0',
            'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            'cgu': 'urn:cgi:xmlns:CGI:DbUtils:1.0'
        })

    def test_shorten(self):
        """ Check namespace shortening
        """
        tests = [
            ("http://www.opengis.net/ows", "ows"),
            ("http://www.opengis.net/ogc", "ogc"),
            ("http://www.opengis.net/wfs", "wfs"),
            ("http://www.opengis.net/gml", "gml"),
            ("urn:cgi:xmlns:CGI:GeoSciML:2.0", "geosciml"),
            # Next one should generate a new entry since version numbers don't
            # match
            ("urn:cgi:xmlns:CGI:GeoSciML:22.0", "geosciml:22.0"),
            ("http://www.opengis.net/sampling/1.0", "sampling"),
            # Next one should just be the same
            ("http://www.opengis.net/sampling/1.0", "sampling"),
            # This should generate a new entry
            ("http://www.opengis.net/sampling/1.0.1alpha",
             "sampling:1.0.1alpha"),
            ("http://www.w3.org/1999/xlink", "xlink")
        ]

        ns = NamespaceMap()
        for namespace_uri, short_namespace in tests:
            ns.add_from_url(namespace_uri)
            self.assertEqual(ns.inverse[namespace_uri],
                             short_namespace)
            self.assertEqual(ns[short_namespace],
                             namespace_uri)

    def test_expand(self):
        """ Check namespace expansion
        """
        self.assertEqual(
            str(self.ns.regularize('geosciml:MappedFeature',
                                   short_namespace=False)),
            '{urn:cgi:xmlns:CGI:GeoSciML:2.0}mappedfeature')


if __name__ == '__main__':
    unittest.main()
