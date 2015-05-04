""" file:  test_borehole_collection.py
    author: Jess Robertson
            Minerals Down Under
    date:   today

    description: Tests for mock Resource class.
"""

from __future__ import print_function, division

from mocks.resource import Resource

import unittest
import json
import httmock
import os


class TestResource(unittest.TestCase):

    def setUp(self):
        fname = os.path.join(os.path.dirname(__file__),
                             'mocks', 'mocks.json')
        with open(fname, 'r') as fhandle:
            self.mocks = json.load(fhandle)
        self.test_endpoint = self.mocks[0]

    def test_init(self):
        """ Resource should initialize with no errors
        """
        resource = Resource(**self.test_endpoint)
        expected_attrs = ['data', 'method', 'params', 'url']
        for attr in expected_attrs:
            self.assertTrue(getattr(resource, attr) is not None)

    def test_wrong_url(self):
        """ Resource should return a 404 on error
        """
        self.test_endpoint['params'] = {'quux': 'foobar'}
        resource = Resource(**self.test_endpoint)
        response = resource.response()
        self.assertTrue(response.status_code == 404)
