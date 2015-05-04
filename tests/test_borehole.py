#!/usr/bin/env python
""" file:   test_borehole.py
    author: Ben Caradoc-Davies
            CSIRO Earth Science and Resource ENgineering
    date:   November 20, 2013

    description: Unit tests to demonstrate the borehole model.
"""

from __future__ import print_function, division

import pysiss
from pysiss import borehole as pybh

import numpy
import unittest

class BoreholeTest(unittest.TestCase):

    def setUp(self):
        self.borehole = pybh.Borehole("test")

    def test_identifier(self):
        """ Test that identifier is being captured for borehole
        """
        self.assertEqual(self.borehole.ident, "test")

    def test_features(self):
        """ Test store and retrieve a single point feature with a one
            single-valued category property
        """
        feature = pybh.PointDataset("fault-1", [27.3])
        feature.metadata.set('age', 'last Friday')
        self.borehole.add_dataset(feature)
        self.assertIsNotNone(self.borehole.point_datasets['fault-1'].metadata)
        mdata = self.borehole.point_datasets["fault-1"].metadata
        self.assertEqual(
            "last Friday",
            mdata.xpath('/pysiss:boreholePointDataset/@age')[0])

    def test_interval_dataset(self):
        """ Test store and retrieve four intervals with a single multivalued
            category property
        """
        geology_intervals = [
            [7.0, 8.0, "SA"],
            [8.0, 11.0, "SL", "CA"],
            [11.0, 14.0, "SC", "CA"],
            [14.0, 15.0, "SC", "FE"]
        ]

        # Construct dataset
        from_depths = [x[0] for x in geology_intervals]
        to_depths = [x[1] for x in geology_intervals]
        geol = pybh.IntervalDataset(
            ident='geology',
            from_depths=from_depths,
            to_depths=to_depths)
        self.assertTrue(all(numpy.diff(geol.from_depths) > 0))
        self.assertTrue(all(numpy.diff(geol.to_depths) > 0))
        self.assertTrue(all(from_depths == geol.from_depths))
        self.assertTrue(all(to_depths == geol.to_depths))

        # rock type is a multivalued category property
        geol.add_property(
            ident='rock',
            values=[x[2:] for x in geology_intervals],
            long_name='rock type code',
            units='none')
        self.assertEqual(["SC", "FE"], geol['rock'].values[-1])

    def test_point_datasets(self):
        """Test store and retrieve two properties sampled at four depths"""
        # the depths of the dataset
        depths = [4.0, 4.02, 4.0603, 4.0803]

        # two numerical properties
        densities = [2.8073, 2.837, 2.8569, 2.8158]
        impedances = [9010.898, 9250.686, 11854.32, 11621.28]
        dataset = self.borehole.add_point_dataset("samples", depths)
        dataset.add_property('density', densities,
                             long_name="density",
                             units="g/cm3")
        dataset.add_property('impedance', impedances,
                             long_name="impedance",
                             units="kg/m2.s.10-3")
        self.assertTrue(numpy.allclose(
            depths,
            self.borehole.point_datasets["samples"].depths))
        self.assertTrue(numpy.allclose(
            densities,
            self.borehole.point_datasets["samples"]['density']))
        self.assertTrue(numpy.allclose(
            impedances,
            self.borehole.point_datasets["samples"]['impedance']))

    def test_interval_dataset_depths_empty(self):
        """ Test that empty interval depths raises an ValueError
        """
        self.assertRaises(
            ValueError,
            lambda: pybh.IntervalDataset("test", [], []))

    def test_interval_dataset_depths_different_size(self):
        """ Test that interval depths of different size raises an
            ValueError
        """
        self.assertRaises(
            ValueError,
            lambda: pybh.IntervalDataset("test", [1, 3, 5], [2, 4]))

    def test_interval_dataset_depths_decreasing(self):
        """ Test that decreasing interval depths raises an ValueError
        """
        self.assertRaises(
            ValueError,
            lambda: pybh.IntervalDataset("test", [3, 1], [4, 2]))

    def test_interval_dataset_zero_length(self):
        """ Test that zero interval length raises an ValueError
        """
        self.assertRaises(
            ValueError,
            lambda: pybh.IntervalDataset("test", [1, 3], [2, 3]))

    def test_interval_dataset_negative_length(self):
        """ Test that negative interval length raises an ValueError
        """
        self.assertRaises(
            ValueError,
            lambda: pybh.IntervalDataset("test", [1, 4], [2, 3]))

    def test_interval_dataset_overlap(self):
        """ Test that interval overlap raises an ValueError
        """
        self.assertRaises(
            ValueError,
            lambda: pybh.IntervalDataset("test", [1, 2], [3, 4]))

    def test_interval_dataset_wrong_property_size(self):
        """ Test that interval property with wrong number of values raises an
            ValueError
        """
        dset = pybh.IntervalDataset("test", [1, 3], [2, 4])
        self.assertRaises(
            ValueError,
            lambda: dset.add_property('density', [1.3]))

    def test_point_dataset_depths_empty(self):
        """ Test that empty point depths raises an ValueError
        """
        self.assertRaises(
            ValueError,
            lambda: pybh.PointDataset("test", []))

    def test_sampling_dataset_depths_decreasing(self):
        """ Test that decreasing point depths raises an ValueError
        """
        self.assertRaises(
            ValueError,
            lambda: pybh.PointDataset("test", [2, 1]))

    def test_sampling_dataset_wrong_property_size(self):
        """ Test that point property with wrong number of values raises an
            ValueError
        """
        dset = pybh.PointDataset("test", [1, 2])
        self.assertRaises(
            ValueError,
            lambda: dset.add_property('density', [1.3]))


if __name__ == "__main__":
    unittest.main()
