import unittest
from pysiss.vocabulary.namespaces import split_namespace, \
    shorten_namespace, expand_namespace


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


if __name__ == '__main__':
    unittest.main()
