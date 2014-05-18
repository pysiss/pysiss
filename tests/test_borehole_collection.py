""" file:  test_borehole_collection.py
    author: Jess Robertson
            Minerals Down Under
    date:   today

    description: Tests for BoreholeCollection class.
"""

import pyboreholes as pybh
import unittest


class TestBoreholeCollection(unittest.TestCase):

    """ Tests for BoreholeCollection
    """

    def setUp(self):
        self.boreholes = [pybh.Borehole("test_{0}".format(idx))
                          for idx in range(10)]
        self.bh_names = [bh.name for bh in self.boreholes]

    def test_creation(self):
        coll = pybh.BoreholeCollection()
        self.assertEqual(len(coll), 0)
        self.assertEqual(len(coll._index), 0)

    def test_creation_2(self):
        """ Test initialization with a list of boreholes
        """
        coll = pybh.BoreholeCollection(self.boreholes)
        self.assertEqual(coll.values, self.boreholes)
        self.assertEqual(coll.keys, self.bh_names)

    def test_addition(self):
        coll = pybh.BoreholeCollection()
        for bh in self.boreholes:
            coll.append(bh)

        self.assertEqual(coll.values, self.boreholes)
        self.assertEqual(coll.keys, self.bh_names)

    def test_iteration(self):
        coll = pybh.BoreholeCollection(self.boreholes)
        for idx, bh in enumerate(coll):
            self.assertEqual(bh, self.boreholes[idx])

    def test_items(self):
        coll = pybh.BoreholeCollection(self.boreholes)
        for idx, (name, bh) in enumerate(coll.items()):
            self.assertEqual(bh, self.boreholes[idx])
            self.assertEqual(name, self.boreholes[idx].name)
