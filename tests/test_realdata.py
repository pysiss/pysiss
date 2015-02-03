#!/usr/bin/env python
""" file: test_real_data.py
    author: Jess Robertson
            CSIRO Earth Science and Resource Engineering
    date:   Wednesday November 20, 2013

    description: Test running pysiss.borehole over a real dataset. This is
    bascially just a couple of scripts pulled from the example sets.
"""

import pysiss
import pandas
import numpy
import cPickle as pickle
import itertools
import os
import unittest

# Location of data files
PROP_TYPE_PKL = os.path.join('.', 'test_real_ptypes.pkl')
TEST_DATA_PKL = os.path.join('.', 'test_real_data.pkl')
DATA_FILE = os.path.join(
    '..', 'examples',
    'Vogue_Apr_2013_combined_pXR__ME_data_classified.csv')


def make_property_types():
    """ Makes property type instances
    """
    try:
        with open(PROP_TYPE_PKL, 'rb') as pkl_file:
            return pickle.load(pkl_file)
    except IOError:
        # We'll just keep going and generate the pickle by hand
        pass

    ## INFORMATION ABOUT DATAFILE
    # Labels and long-form version
    vogue_data = pandas.read_csv(DATA_FILE)
    long_names = dict(zip(vogue_data.keys(), itertools.repeat(None)))
    long_names.update({
        'As_ppm': 'Arsenic',
        'CaO_pct': 'Calcium',
        'Co_ppm': 'Cobalt',
        'Cr_ppm': 'Chromium',
        'Cu_ppm': 'Copper',
        'Fe2O3_pct': 'Ferric Iron (3+)',
        'K2O_pct': 'Potassium',
        'MnO_pct': 'Manganese',
        'Ni_ppm': 'Nickel',
        'Rb_ppm': 'Rubidium',
        'SO3_pct': 'Sulphur',
        'Sr_ppm': 'Strontium',
        'TiO2_pct': 'Titanium',
        'V_ppm': 'Vanadium',
        'Zn_ppm': 'Zinc',
        'Zr_ppm': 'Zirconium',
        'Sample': 'Sample number',
        'Hole_ID': 'Borehole ID',
        'From': 'Depth from',
        'To': 'Depth to',
        'TYPE': 'Measurement method',
        'Litho2': 'Lithology label'
    })

    # Set units
    def units(key):
        """ Returns the units for the given key
        """
        if 'ppm' in key:
            return 'ppm'
        elif 'pct' in key and 'O' in key:
            return 'oxide wt. %'
        elif key in ['From', 'To'] or 'mid' in key:
            return 'metres'
        else:
            return None

    def is_numeric(key):
        """ Returns whether data is numeric or not
        """
        numeric_labels = ['ppm', 'pct', 'Litho2']
        return any([l in key for l in numeric_labels])

    # Generate property_types
    property_types = dict()
    for key in vogue_data.keys():
        isnumeric = is_numeric(key)
        property_types[key] = pysiss.borehole.PropertyType(
            name=key, long_name=long_names[key], units=units(key),
            isnumeric=isnumeric)

    # Dump property types to pickle file and return
    with open(PROP_TYPE_PKL, 'wb') as pkl_file:
        pickle.dump(property_types, pkl_file)
    return property_types


class TestRealData(unittest.TestCase):

    """ Test running pysiss.borehole over a real dataset
    """

    def setUp(self):
        # Reload prewarmed data if available, else load data & cache
        property_types = make_property_types()
        try:
            pkl_file = open(self.test_data_pkl, 'rb')
            self.boreholes = pickle.load(pkl_file)
            return
        except IOError:
            pass

        # If we're here, we need to generate the data from the datafile
        vogue_data = pandas.read_csv(DATA_FILE)
        vogue_data = vogue_data.sort(('Hole_ID', 'From', 'To'))
        property_keys = [
            'As_ppm', 'CaO_pct', 'Co_ppm', 'Cr_ppm', 'Cu_ppm',
            'Fe2O3_pct', 'K2O_pct', 'MnO_pct', 'Ni_ppm', 'Rb_ppm', 'SO3_pct',
            'Sr_ppm', 'TiO2_pct', 'V_ppm', 'Zn_ppm', 'Zr_ppm']
        boreholes = dict()
        for name, data in vogue_data.groupby("Hole_ID"):
            # Construct the borehole instance first
            bh = boreholes[name] = pysiss.borehole.Borehole(name)

            # Generate an IntervalDataSet corresponding to the values in the
            # spreadsheet
            data = data.dropna()
            from_depths = numpy.asarray(data['From'])
            to_depths = numpy.asarray(data['To'])
            dataset = bh.add_interval_dataset(
                'geochemistry', from_depths, to_depths)

            # Add all the geochemistry values as Properties
            for key in property_keys:
                datum = numpy.asarray(
                    data[key].convert_objects(convert_numeric=True))
                dataset.add_property(property_types[key], datum)
