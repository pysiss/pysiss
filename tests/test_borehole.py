#!/usr/bin/env python
"""Unit tests to demonstrate the borehole model.
"""

import borehole as bh
import unittest

DENSITY = bh.PropertyType(name="d", long_name="density", units="g/cm3")

# bogus unit from original spreadsheet
IMPEDANCE = bh.PropertyType(name="imp", long_name="impedance", units="kg/m2.s.10-3")

ROCK_TYPE = bh.PropertyType(name="rock", long_name="rock type")

class BoreholeTest(unittest.TestCase):

    def setUp(self):
        self.borehole = bh.Borehole("test")

    def test_features(self):
        """Test store and retrieve a single point feature with a one single-valued category property"""
        feature = self.borehole.add_feature("fault-1", 27.3)
        feature.add_property(bh.PropertyType("age"), "last friday")
        self.assertEquals("last friday", self.borehole.features["fault-1"].properties["age"].values)

    def test_interval_domain(self):
        """Test store and retrieve four intervals with a single multivalued category property"""
        geology_intervals = [
            [7.0, 8.0, "SA"],
            [8.0, 11.0, "SL", "CA"],
            [11.0, 14.0, "SC", "CA"],
            [14.0, 15.0, "SC", "FE"]
        ]
        # the starts and ends of the intervals
        from_depths = [x[0] for x in geology_intervals]
        to_depths = [x[1] for x in geology_intervals]
        # rock type is a multivalued category property
        rock_type = [x[2:] for x in geology_intervals]
        domain = self.borehole.add_interval_domain("geology", from_depths, to_depths)
        domain.add_property(ROCK_TYPE, rock_type)
        self.assertEquals(from_depths, self.borehole.interval_domains["geology"].from_depths)
        self.assertEquals(to_depths, self.borehole.interval_domains["geology"].to_depths)
        self.assertEquals(["SC", "FE"], self.borehole.interval_domains["geology"].properties["rock"].values[-1])

    def test_sampling_domain(self):
        """Test store and retrieve two properties sampled at four depths"""
        # the depths of the domain
        depths = [4.0, 4.02, 4.0603, 4.0803]
        # two numerical properties
        densities = [2.8073, 2.837, 2.8569, 2.8158]
        impedances = [9010.898, 9250.686, 11854.32, 11621.28]
        domain = self.borehole.add_sampling_domain("samples", depths)
        domain.add_property(DENSITY, densities)
        domain.add_property(IMPEDANCE, impedances)
        self.assertEquals(depths, self.borehole.sampling_domains["samples"].depths)
        self.assertEquals(densities, self.borehole.sampling_domains["samples"].properties["d"].values)
        self.assertEquals(impedances, self.borehole.sampling_domains["samples"].properties["imp"].values)

    def test_interval_domain_depths_empty(self):
        """Test that empty interval depths raises an AssertionError"""
        self.assertRaises(AssertionError, lambda: bh.IntervalDomain("test", [], []))

    def test_interval_domain_depths_different_size(self):
        """Test that interval depths of different size raises an AssertionError"""
        self.assertRaises(AssertionError, lambda: bh.IntervalDomain("test", [1, 3, 5], [2, 4]))

    def test_interval_domain_depths_decreasing(self):
        """Test that decreasing interval depths raises an AssertionError"""
        self.assertRaises(AssertionError, lambda: bh.IntervalDomain("test", [3, 1], [4, 2]))

    def test_interval_domain_zero_length(self):
        """Test that zero interval length raises an AssertionError"""
        self.assertRaises(AssertionError, lambda: bh.IntervalDomain("test", [1, 3], [2, 3]))

    def test_interval_domain_negative_length(self):
        """Test that negative interval length raises an AssertionError"""
        self.assertRaises(AssertionError, lambda: bh.IntervalDomain("test", [1, 4], [2, 3]))

    def test_interval_domain_overlap(self):
        """Test that interval overlap raises an AssertionError"""
        self.assertRaises(AssertionError, lambda: bh.IntervalDomain("test", [1, 2], [3, 4]))

    def test_interval_domain_wrong_property_size(self):
        """Test that interval property with wrong number of values raises an AssertionError"""
        self.assertRaises(AssertionError,
                          lambda: bh.IntervalDomain("test", [1, 3], [2, 4]).add_property(DENSITY, [1.3]))

    def test_sampling_domain_depths_empty(self):
        """Test that empty sampling depths raises an AssertionError"""
        self.assertRaises(AssertionError, lambda: bh.SamplingDomain("test", []))

    def test_sampling_domain_depths_decreasing(self):
        """Test that decreasing sampling depths raises an AssertionError"""
        self.assertRaises(AssertionError, lambda: bh.SamplingDomain("test", [2, 1]))

    def test_sampling_domain_wrong_property_size(self):
        """Test that sampling property with wrong number of values raises an AssertionError"""
        self.assertRaises(AssertionError,
                          lambda: bh.SamplingDomain("test", [1, 2]).add_property(DENSITY, [1.3]))


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(BoreholeTest)
    unittest.TextTestRunner(verbosity=2).run(suite)
