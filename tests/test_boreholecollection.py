""" file:  test_borehole_collection.py
    author: Jess Robertson
            Minerals Down Under
    date:   today

    description: Tests for BoreholeCollection class.
"""

from __future__ import print_function, division

from pysiss import borehole as pybh
from pysiss.utilities import collection

import unittest


class TestBoreholeCollection(unittest.TestCase):

    """ Tests for BoreholeCollection
    """

    def setUp(self):
        self.boreholes = [pybh.Borehole("test_{0}".format(idx))
                          for idx in range(10)]
        self.bh_idents = [bh.ident for bh in self.boreholes]

    def test_creation(self):
        coll = collection()
        self.assertEqual(len(coll), 0)
        self.assertEqual(len(coll._index), 0)

    def test_creation_2(self):
        """ Test initialization with a list of boreholes
        """
        coll = collection(self.boreholes)
        for idx, (ident, bh) in enumerate(coll.items()):
            self.assertEqual(bh, self.boreholes[idx])
            self.assertEqual(ident, self.boreholes[idx].ident)

    def test_addition(self):
        coll = collection()
        for bh in self.boreholes:
            coll.append(bh)

        for idx, bh in enumerate(coll):
            self.assertEqual(bh, self.boreholes[idx])

    def test_iteration(self):
        coll = collection(self.boreholes)
        for idx, bh in enumerate(coll):
            self.assertEqual(bh, self.boreholes[idx])

    def test_items(self):
        coll = collection(self.boreholes)
        for idx, (ident, bh) in enumerate(coll.items()):
            self.assertEqual(bh, self.boreholes[idx])
            self.assertEqual(ident, self.boreholes[idx].ident)
