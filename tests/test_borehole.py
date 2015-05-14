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
        self.assertIsNotNone(str(self.borehole))
        self.assertEqual(self.borehole.ident, "test")

    def test_interval_dataset_depths_empty(self):
        """ Test that empty interval depths raises an ValueError
        """
        self.assertRaises(
            ValueError,
            lambda: pybh.IntervalDataset([], []))

    def test_interval_dataset_depths_different_size(self):
        """ Test that interval depths of different size raises an
            ValueError
        """
        self.assertRaises(
            ValueError,
            lambda: pybh.IntervalDataset([1, 3, 5], [2, 4]))

    def test_interval_dataset_depths_decreasing(self):
        """ Test that decreasing interval depths raises an ValueError
        """
        self.assertRaises(
            ValueError,
            lambda: pybh.IntervalDataset([3, 1], [4, 2]))

    def test_interval_dataset_zero_length(self):
        """ Test that zero interval length raises an ValueError
        """
        self.assertRaises(
            ValueError,
            lambda: pybh.IntervalDataset([1, 3], [2, 3]))

    def test_interval_dataset_negative_length(self):
        """ Test that negative interval length raises an ValueError
        """
        self.assertRaises(
            ValueError,
            lambda: pybh.IntervalDataset([1, 4], [2, 3]))

    def test_interval_dataset_overlap(self):
        """ Test that interval overlap raises an ValueError
        """
        self.assertRaises(
            ValueError,
            lambda: pybh.IntervalDataset([1, 2], [3, 4]))

    def test_interval_dataset_wrong_property_size(self):
        """ Test that interval property with wrong number of values raises an
            ValueError
        """
        dset = pybh.IntervalDataset([1, 3], [2, 4])
        self.assertRaises(
            ValueError,
            lambda: dset.add_property('density', [1.3]))

    def test_point_dataset_depths_empty(self):
        """ Test that empty point depths raises an ValueError
        """
        self.assertRaises(
            ValueError,
            lambda: pybh.PointDataset([]))

    def test_sampling_dataset_depths_decreasing(self):
        """ Test that decreasing point depths raises an ValueError
        """
        self.assertRaises(
            ValueError,
            lambda: pybh.PointDataset([2, 1]))

    def test_sampling_dataset_wrong_property_size(self):
        """ Test that point property with wrong number of values raises an
            ValueError
        """
        dset = pybh.PointDataset([1, 2])
        self.assertRaises(
            ValueError,
            lambda: dset.add_property('density', [1.3]))

class BoreholeIntervalDataTest(unittest.TestCase):

    """ Test store and retrieve four intervals with a single multivalued
        category property
    """

    def setUp(self):
        geology_intervals = [
            [7.0, 8.0, "SA"],
            [8.0, 11.0, "SL", "CA"],
            [11.0, 14.0, "SC", "CA"],
            [14.0, 15.0, "SC", "FE"]
        ]

        # Construct dataset
        self.from_depths = [x[0] for x in geology_intervals]
        self.to_depths = [x[1] for x in geology_intervals]
        self.dataset = pybh.IntervalDataset(
            ident='geology',
            from_depths=self.from_depths,
            to_depths=self.to_depths)

        # rock type is a multivalued category property
        self.dataset.add_property(
            ident='rock',
            values=[x[2:] for x in geology_intervals],
            long_name='rock type code',
            units='none')

        # Add to a borehole
        self.borehole = pybh.Borehole("test")
        self.borehole.add_dataset(self.dataset)

    def test_setting_depths(self):
        """ Check depths are set correctly
        """
        self.assertTrue(numpy.allclose(
            self.from_depths,
            self.borehole.interval_datasets["geology"].from_depths))
        self.assertTrue(numpy.allclose(
            self.to_depths,
            self.borehole.interval_datasets["geology"].to_depths))
        self.assertTrue(all(numpy.diff(self.dataset.from_depths) > 0))
        self.assertTrue(all(numpy.diff(self.dataset.to_depths) > 0))

    def test_setting_property_values(self):
        """ Check property values are set correctly
        """
        self.assertEqual(["SC", "FE"], self.dataset['rock'].values[-1])

    def test_setting_property_metadata(self):
        """ Check property metadata is set correctly
        """
        md = self.borehole.metadata

        # Check that metadata propagates back to borehole
        md = self.borehole.metadata
        query_items = [
            ('//pysiss:property', None),
            ('//*[@ident="rock"]', None),
            ('//pysiss:boreholeDataset', None)
        ]
        for query, expected in query_items:
            if expected is None:
                self.assertIsNotNone(md.xpath(query, unwrap=True))
            else:
                self.assertEqual(md.xpath(query, unwrap=True),
                                 expected)

class BoreholePointDataTest(unittest.TestCase):

    """ Test store and retrieve four points with two numerical properties
    """

    def setUp(self):
        # Construct borehole instance
        self.borehole = pybh.Borehole("test")

        # Construct dataset
        self.depths = [4.0, 4.02, 4.0603, 4.0803]
        self.densities = [2.8073, 2.837, 2.8569, 2.8158]
        self.impedances = [9010.898, 9250.686, 11854.32, 11621.28]
        self.dataset = self.borehole.add_point_dataset("samples", self.depths)
        self.dataset.add_property(ident='density', 
                                  values=self.densities,
                                  long_name="density",
                                  units="g/cm3")
        self.dataset.add_property(ident='impedance', 
                                  values=self.impedances,
                                  long_name="impedance",
                                  units="kg/m2.s.10-3")

        # Add a feature
        feature = pybh.PointDataset(depths=[27.3], ident="fault-1")
        feature.metadata.set_attributes(age='last Friday')
        self.borehole.add_dataset(feature)

    def test_feature_depth(self):
        """ Check feature depth is set correctly
        """
        feature = self.borehole.point_datasets['fault-1']
        self.assertIsNotNone(feature)
        self.assertTrue(numpy.allclose([27.3], feature.depths))

    def test_feature_metadata(self):
        """ Check feature metadata is set correctly
        """
        feature = self.borehole.point_datasets['fault-1']
        self.assertEqual(feature.metadata.get_attribute('age'),
                        'last Friday')
        self.assertEqual(
            "last Friday",
            self.borehole.metadata.xpath('//pysiss:boreholeDataset/@age')[0])

    def test_setting_depths(self):
        """ Check depths are set correctly
        """
        self.assertTrue(numpy.allclose(
            self.depths,
            self.borehole.point_datasets["samples"].depths))

    def test_setting_property_values(self):
        """ Check property values are set correctly
        """
        self.assertTrue(numpy.allclose(
            self.densities,
            self.borehole.point_datasets["samples"]['density']))
        self.assertTrue(numpy.allclose(
            self.impedances,
            self.borehole.point_datasets["samples"]['impedance']))

    def test_setting_property_metadata(self):
        """ Check property metadata is set correctly
        """
        md = self.borehole.metadata

        # Check that metadata propagates back to borehole
        md = self.borehole.metadata
        self.assertIsNotNone(md.xpath('//*[@ident="density"]', unwrap=True))
        query_items = [
            ('//pysiss:property', None),
            ('//*[@ident="density"]', None),
            ('//pysiss:boreholeDataset', None)
        ]
        for query, expected in query_items:
            if expected is None:
                self.assertIsNotNone(md.xpath(query, unwrap=True))
            else:
                self.assertEqual(md.xpath(query, unwrap=True),
                                 expected)
        

if __name__ == "__main__":
    unittest.main()
