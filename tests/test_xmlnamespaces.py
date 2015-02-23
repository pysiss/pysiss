import unittest
from pysiss.metadata import Namespace


class TestXMLNamespaces(unittest.TestCase):

    """ Tests for XML namespace munging
    """

    def setUp(self):
        self.ns = Namespace({
            'om': 'http://www.opengis.net/om/1.0',
            'ows': 'http://www.opengis.net/ows/1.0',
            'gml': 'http://www.opengis.net/gml',
            'xlink': 'http://www.w3.org/1999/xlink',
            'gsml': 'urn:cgi:xmlns:CGI:GeoSciML:2.0',
            'wfs': 'http://www.opengis.net/wfs',
            'sa': 'http://www.opengis.net/sampling/1.0',
            'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            'cgu': 'urn:cgi:xmlns:CGI:DbUtils:1.0'
        })

    def test_namespace_shortening(self):
        """ Adding namespaces should work ok
        """
        test_namespaces = {
            "ows:tag": "{http://www.opengis.net/ows/1.0}tag",
            "gsml:tag": "urn:cgi:xmlns:CGI:GeoSciML:2.0:tag"
        }
        for sname, lname in test_namespaces.items():
            self.assertEqual(sname, self.ns.shorten(lname))

    def test_namespace_lengthening_rdf(self):
        namespaces = {
            "ows:tag": "http://www.opengis.net/ows/1.0:tag",
            "gsml:tag": "urn:cgi:xmlns:CGI:GeoSciML:2.0:tag"
        }
        for sname, lname in namespaces.items():
            self.assertEqual(self.ns.expand(sname, form='rdf'),
                             lname)

    def test_namespace_lengthening_lxml(self):
        namespaces = {
            "ows:tag": "{http://www.opengis.net/ows/1.0}tag",
            "gsml:tag": "{urn:cgi:xmlns:CGI:GeoSciML:2.0}tag"
        }
        for sname, lname in namespaces.items():
            self.assertEqual(self.ns.expand(sname), lname)

    def test_split_namespace(self):
        """ Test namespace splitting returns the right values
        """
        self.assertEqual(
            self.ns.split('urn:cgi:xmlns:CGI:GeoSciML:2.0:MappedFeature'),
            ('urn:cgi:xmlns:CGI:GeoSciML:2.0', 'MappedFeature'))
        self.assertEqual(
            self.ns.split('{urn:cgi:xmlns:CGI:GeoSciML:2.0}MappedFeature'),
            ('urn:cgi:xmlns:CGI:GeoSciML:2.0', 'MappedFeature'))
        self.assertEqual(
            self.ns.split('gsml:MappedFeature'),
            ('gsml', 'MappedFeature'))

    def test_shorten(self):
        """ Check namespace shortening
        """
        self.assertEqual(
            self.ns.shorten('{http://www.opengis.net/gml}boundedBy'),
            'gml:boundedBy')

    def test_expand(self):
        """ Check namespace expansion
        """
        self.assertEqual(
            self.ns.expand('gsml:MappedFeature'),
            '{urn:cgi:xmlns:CGI:GeoSciML:2.0}MappedFeature')
        self.assertEqual(
            self.ns.expand('gsml:MappedFeature', form='rdf'),
            'urn:cgi:xmlns:CGI:GeoSciML:2.0:MappedFeature')


if __name__ == '__main__':
    unittest.main()
