""" file: test_service.py
    author: Jess Robertson
            CSIRO Mineral Resources Flagship
    date:   Monday February 2, 2015

    description: Tests for utilities to describe service  from
        values to the correct version of the OGC Webservice API.
"""

from __future__ import print_function, division

from pysiss.utilities import accumulator
from pysiss.webservices.ogc.service import OGCService, OGCQueryString

import unittest
import logging
import httmock
from mocks.resource import mock_resource


LOGGER = logging.getLogger('pysiss')
ENDPOINT = ('http://aster.nci.org.au/thredds/wcs/aster/vnir/Aus_Mainland/'
            'Aus_Mainland_AlOH_group_composition_reprojected.nc4')


class Testaccumulator(unittest.TestCase):

    """ Tests for accumulator object
    """

    def test_init_by_pairs(self):
        """ Init from pairs
        """
        acc = accumulator([('a', 'b'), ('a', 'c'), ('foo', 'quux')])
        self.assertEqual(sorted(acc.keys()), ['a', 'foo'])
        self.assertEqual(acc['a'], ['b', 'c'])

    def test_init_by_dicts(self):
        """ Init from pairs
        """
        acc = accumulator({'a': 'b'}, {'a': 'c', 'foo': 'quux'})
        self.assertEqual(sorted(acc.keys()), ['a', 'foo'])
        self.assertEqual(acc['a'], ['b', 'c'])

    def test_init_by_keywords(self):
        """ Init from keywords
        """
        acc = accumulator({'a': 'b'}, a='c', foo='quux')
        self.assertEqual(sorted(acc.keys()), ['a', 'foo'])
        self.assertEqual(acc['a'], ['b', 'c'])

    def test_init_by_mixed(self):
        """ Init from everything
        """
        acc = accumulator({'a': 'b'}, [('a', 'c')], foo='quux')
        self.assertEqual(sorted(acc.keys()), ['a', 'foo'])
        self.assertEqual(acc['a'], ['b', 'c'])


class TestOGCQueryString(unittest.TestCase):

    """ Tests for QueryString object
    """

    def setUp(self):
        self.query = OGCQueryString()
        self.query['a'] = 'b'
        self.query['foo'] = 'bar'
        self.query['quux'] = 'longitude(140)'
        self.query['a'] = 'c'

    def test_init(self):
        """ Check that the keys and values are initialized ok
        """
        self.assertEqual(self.query['a'],
                         ['b', 'c'])
        self.assertEqual(self.query['quux'],
                         'longitude(140)')

    def test_keys_query(self):
        """ Keys should come back from underlying dictionary
        """
        self.assertEqual(sorted(self.query.keys()),
                         ['a', 'foo', 'quux'])

    def test_values_query(self):
        """ Values should return values listed by key
        """
        self.assertEqual(len(list(self.query.values())), 3)

    def test_repr(self):
        """ Representation should just return the string
        """
        self.assertEqual(repr(self.query), str(self.query))

    def test_str_creation(self):
        """ Check that the string comes back as expected
        """
        query = str(self.query)
        self.assertTrue(query.startswith('?'))
        for frag in ('a=b', 'a=c', 'foo=bar'):
            self.assertTrue(frag in query)
        self.assertFalse(query.endswith('&'))


class TestServiceMapping(unittest.TestCase):

    """ Tests for ServiceMapping object
    """

    requests = [dict(request='getcapabilities',
                     method='get'),
                dict(request='describecoverage',
                     ident='foo',
                     method='get'),
                dict(request='getcoverage',
                     ident='foo',
                     method='get',
                     minlongitude=132, maxlongitude=145,
                     minlatitude=34, maxlatitude=55,
                     projection='CRS_something',
                     format='geotiff'),
                dict(request='getcoverage',
                     ident='foo',
                     method='get',
                     mintime='1-1-2015', maxtime='5-1-2015',
                     format='geotiff'),
                dict(request='getcoverage',
                     ident='foo',
                     method='get',
                     time='1-1-2015',
                     format='geotiff'),
                dict(request='getcoverage',
                     ident='foo',
                     method='get',
                     latitude=45, longitude=42,
                     projection='CRS_something',
                     format='geotiff'),
                dict(request='getcoverage',
                     ident='foo',
                     method='get',
                     projection='CRS_something',
                     latitude=45, longitude=42,
                     time='1-1-2015',
                     format='geotiff')]

    def test_init_v100(self):
        self._run_init('1.0.0')

    def test_init_v110(self):
        self._run_init('1.1.0')

    def test_init_v200(self):
        self._run_init('2.0.0')

    def _run_init(self, version):
        """ Service object should init ok
        """
        with httmock.HTTMock(mock_resource):
            service = OGCService(endpoint=ENDPOINT, service_type='wcs')

        for request in self.requests:
            # Construct query string
            prepped_request = service.request(send=False, **request)

            # Check that templates have been replaced
            self.assertTrue('@' not in prepped_request.url)
            self.assertTrue('?' not in s
                            for s in prepped_request.url.split('?')[1:])
            for key, value in request.items():
                if key is not 'method':
                    self.assertTrue(str(value) in prepped_request.url,
                                    'Missing value {0} '.format(value) +
                                    'associated with key {0}'.format(key))

if __name__ == '__main__':
    unittest.main()
