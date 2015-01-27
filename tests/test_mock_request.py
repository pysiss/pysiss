""" file:  test_borehole_collection.py
    author: Jess Robertson
            Minerals Down Under
    date:   today

    description: Tests for mock Resource class.
"""

from .mocks.request import Resource

import unittest
import simplejson


class TestResource(unittest.TestSuite):

    def setUp(self):
        with open('mocks.json', 'rb') as fhandle:
            self.mocks = simplejson.load(fhandle)
        self.test_key, self.test_endpoint = self.mocks.items()[0]

    def test_init(self):
        """ Resource should initialize with no errors
        """
        resource = Resource(**self.test_endpoint)
        expected_attrs = ['data', 'method', 'params', 'url']
        for attr in expected_attrs:
            assert(getattr(resource, attr) is not None)

    def test_wrong_url(self):
        """ Resource should return a 404 on error
        """
        wrong_params = {'quux': 'foobar'}
        wrong_params.update(self.test_endpoint.params)
        resource = Resource(**self.test_endpoint)
        resource.params.update({'quux': 'foobar'})
        response = resource.response()
        assert(response.status_code == 404)
