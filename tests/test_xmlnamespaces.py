import unittest
from pysiss.metadata import split_namespace, \
    shorten_namespace, expand_namespace


class TestXMLNamespaces(unittest.TestCase):

    """ Tests for XML namespace munging
    """

    def test_namespace_shortening(self):
        namespaces = {
            "ows:tag": "{http://www.opengis.net/ows}tag",
            "ows:1.0:tag": "{http://www.opengis.net/ows/1.0}tag",
            "gsml:2.0:tag": "urn:cgi:xmlns:CGI:GeoSciML:2.0:tag",
            "gsml:tag": "urn:cgi:xmlns:CGI:GeoSciML:tag"
        }
        for sname, lname in namespaces.items():
            self.assertEqual(sname, shorten_namespace(lname))

    def test_namespace_lengthening_rdf(self):
        namespaces = {
            "ows:tag": "http://www.opengis.net/ows:tag",
            "ows:1.0:tag": "http://www.opengis.net/ows/1.0:tag",
            "gsml:2.0:tag": "urn:cgi:xmlns:CGI:GeoSciML:2.0:tag",
            "gsml:tag": "urn:cgi:xmlns:CGI:GeoSciML:tag"
        }
        for sname, lname in namespaces.items():
            self.assertEqual(expand_namespace(sname, form='rdf'), lname)

    def test_namespace_lengthening_xml(self):
        namespaces = {
            "ows:tag": "{http://www.opengis.net/ows}tag",
            "ows:1.0:tag": "{http://www.opengis.net/ows/1.0}tag",
            "gsml:2.0:tag": "{urn:cgi:xmlns:CGI:GeoSciML:2.0}tag",
            "gsml:tag": "{urn:cgi:xmlns:CGI:GeoSciML}tag"
        }
        for sname, lname in namespaces.items():
            self.assertEqual(expand_namespace(sname), lname)

    def test_split_namespace(self):
        """ Test namespace splitting returns the right values
        """
        self.assertEqual(
            split_namespace('urn:cgi:xmlns:CGI:GeoSciML:2.0:MappedFeature'),
            ('urn:cgi:xmlns:CGI:GeoSciML:2.0', 'MappedFeature'))
        self.assertEqual(
            split_namespace('{urn:cgi:xmlns:CGI:GeoSciML:2.0}MappedFeature'),
            ('urn:cgi:xmlns:CGI:GeoSciML:2.0', 'MappedFeature'))
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
            '{urn:cgi:xmlns:CGI:GeoSciML}MappedFeature')
        self.assertEqual(
            expand_namespace('gsml:2.0:MappedFeature', form='rdf'),
            'urn:cgi:xmlns:CGI:GeoSciML:2.0:MappedFeature')


if __name__ == '__main__':
    unittest.main()
