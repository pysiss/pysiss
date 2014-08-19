""" file:   test_earthchem.py (lithologies)
    author: Jess Robertson
            CSIRO Minerals Resources Flagship
    date:

    description: Unit tests for EarthChem REST queries
"""

import unittest
from pysiss.vocabulary.lithology.composition import EarthChemQuery


class TestEarthChemQuery(unittest.TestCase):

    """ Unit tests for EarthChemQuery class
    """

    def test_url(self):
        query = EarthChemQuery(
            author='jess',
            keyword='basalt')
        expected = ('http://ecp.iedadata.org/restsearchservice?outputtype=json'
                    '&searchtype=rowdata&keyword=basalt&author=jess')
        self.assertTrue(query.url == expected)
        self.assertTrue(set(query.keys()) == set(('keyword', 'author')))
        self.assertTrue(set(query.values()) == set(('basalt', 'jess')))

    def test_changes(self):
        """ Check that changes to the query values are represented in the url
        """
        query = EarthChemQuery(
            author='jess',
            keyword='basalt')
        expected = ('http://ecp.iedadata.org/restsearchservice?outputtype=json'
                    '&searchtype=rowdata&keyword=basalt&author=jess')
        self.assertTrue(query.url == expected)
        query['author'] = 'ben'
        expected = ('http://ecp.iedadata.org/restsearchservice?outputtype=json'
                    '&searchtype=rowdata&keyword=basalt&author=ben')
        self.assertTrue(query.url == expected)
        query['author'] = None
        expected = ('http://ecp.iedadata.org/restsearchservice?outputtype=json'
                    '&searchtype=rowdata&keyword=basalt')
        self.assertTrue(query.url == expected)
        self.assertTrue(set(query.keys()) == set(['keyword']))

    def test_unknown_key(self):
        """ Check that submitting an unknown key raises a KeyError
        """
        query = EarthChemQuery(
            author='jess',
            keyword='basalt')
        self.assertRaises(KeyError,
                          lambda x, y: query.__setitem__(x, y),
                          'foo', 'bar')
        self.assertRaises(KeyError, EarthChemQuery, foo='bar')

    def test_unknown_value(self):
        """ Check that submitting an unknown value for the EarthChem
            query raises a KeyError
        """
        query = EarthChemQuery(
            author='jess',
            keyword='basalt')
        self.assertRaises(KeyError,
                          lambda x, y: query.__setitem__(x, y),
                          'level4', 'bar')
        self.assertRaises(KeyError, EarthChemQuery, evel4='bar')

    def test_jsondecode_load_empty(self):
        """ Check that empty search results are handled properly.
        """
        query = EarthChemQuery(level3='exotic',
                               level4='basanite')
        query.result

if __name__ == '__main__':
    unittest.main()
