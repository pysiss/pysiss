""" file:  test_borehole_collection.py
    author: Jess Robertson
            Minerals Down Under
    date:   today

    description: Tests for BoreholeCollection class.
"""

from pysiss import borehole as pybh
from pysiss.utilities import Collection
import unittest


class TestBoreholeCollection(unittest.TestCase):

    """ Tests for BoreholeCollection
    """

    def setUp(self):
        self.boreholes = [pybh.Borehole("test_{0}".format(idx))
                          for idx in range(10)]
        self.bh_names = [bh.name for bh in self.boreholes]

    def test_creation(self):
        coll = Collection()
        self.assertEqual(len(coll), 0)
        self.assertEqual(len(coll._index), 0)

    def test_creation_2(self):
        """ Test initialization with a list of boreholes
        """
        coll = Collection(self.boreholes)
        for idx, (name, bh) in enumerate(coll.items()):
            self.assertEqual(bh, self.boreholes[idx])
            self.assertEqual(name, self.boreholes[idx].name)

    def test_addition(self):
        coll = Collection()
        for bh in self.boreholes:
            coll.append(bh)

        for idx, bh in enumerate(coll):
            self.assertEqual(bh, self.boreholes[idx])

    def test_iteration(self):
        coll = Collection(self.boreholes)
        for idx, bh in enumerate(coll):
            self.assertEqual(bh, self.boreholes[idx])

    def test_items(self):
        coll = Collection(self.boreholes)
        for idx, (name, bh) in enumerate(coll.items()):
            self.assertEqual(bh, self.boreholes[idx])
            self.assertEqual(name, self.boreholes[idx].name)
