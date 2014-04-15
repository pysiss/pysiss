#!/usr/bin/env python
"""Tests for detcrc_csv.py
"""

import unittest
import pyboreholes.importers.detcrc_csv as det
import os.path
import pyboreholes

TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), "data", "detcrc_csv")

def find_test_filename(basefilename):
    return os.path.join(TEST_DATA_DIR, basefilename)

class DetCrcCsvTest(unittest.TestCase):

    def test_load_log(self):
        dataset = det.load_log(find_test_filename("xRD01_alt_log.csv"))
        self.assertIsInstance(dataset, pyboreholes.IntervalDataSet)

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(DetCrcCsvTest)
    unittest.TextTestRunner(verbosity=2).run(suite)
