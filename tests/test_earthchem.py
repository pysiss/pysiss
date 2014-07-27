""" file:   test_earthchem.py (lithologies)
    author: Jess Robertson
            CSIRO Minerals Resources Flagship
    date:

    description: Unit tests for EarthChem REST queries
"""

import unittest
from pysiss.vocabulary.lithology.composition import EarthChemQuery


class TestEarthChemQue(unittest.TestCase):

    """ Unit tests for EarthChemQuery class
    """

    def test_url(self):
        query = EarthChemQuery(
            author='jess',
            keyword='basalt')
        expected = ('http://ecp.iedadata.org/restsearchservice?outputtype=json'
                    '&keyword=basalt&author=jess')
        self.assertTrue(query.url == expected)
        self.assertTrue(set(query.keys) == set('keyword', 'author'))
        self.assertTrue(set(query.values) == set('basalt', 'jess'))

    def test_changes(self):
        """ Check that changes to the query values are represented in the url
        """
        query = EarthChemQuery(
            author='jess',
            keyword='basalt')
        expected = ('http://ecp.iedadata.org/restsearchservice?outputtype=json'
                    '&keyword=basalt&author=jess')
        self.assertTrue(query.url == expected)
        query['author'] = 'ben'
        expected = ('http://ecp.iedadata.org/restsearchservice?outputtype=json'
                    '&keyword=basalt&author=ben')
        self.assertTrue(query.url == expected)
        query['author'] = None
        expected = ('http://ecp.iedadata.org/restsearchservice?outputtype=json'
                    '&keyword=basalt')
        self.assertTrue(query.url == expected)
        self.assertTrue(set(query.keys) == set(['keyword']))
