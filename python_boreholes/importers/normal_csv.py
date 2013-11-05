#!/usr/bin/env python
""" file: normal_csv.py
    author: Jess Robertson
            CSIRO Earth Science and Resource Engineering
    date: Tuesday 21 May, 2013

    description: Utilities for munging CSV data.
"""

import numpy
import itertools
from csv import DictReader
from python_boreholes.utilities import try_float

def parse_csv(csv_filename, all_keys):
    """ Parse a CSV file, return data as numpy arrays
    """
    # Parse data from csv file
    with open(csv_filename, 'rb') as fhandle:
        # Read in data to DictReader
        reader = DictReader(fhandle)
        data_dicts = [l for l in reader]

        # Just check that you aren't passing some weird key which will end
        # up with all NaNs
        for key in all_keys:
            if key not in reader.fieldnames:
                print ("Warning: you've specified at least one key ({0}) to "
                    "get from the CSV file '{1}' which is not present in the "
                    "file (it's keys are {2}). I've filled the array with "
                    "NaNs instead, but if you pass this to a Borehole "
                    "instance it will probably choke.\n\n").format(key,
                        fhandle.name, ', '.join(reader.fieldnames))

        # Generate the list of dicts
        all_data = dict([(k, []) for k in all_keys])

        # Cycle through and convert where necessary
        for ddict in data_dicts:
            current_dict = dict(zip(all_keys, itertools.repeat(numpy.nan)))
            current_dict.update(ddict)
            for key, value in current_dict.items():
                if key in all_keys:
                    all_data[key].append(try_float(value))

    # Convert arrays to numpy arrays
    all_data = dict([(k, numpy.asarray(all_data[k])) for k in all_keys])
    return all_data

def add_to_borehole(borehole, domain_data, data, labels):
    """ Add data to a borehole
    """
    for key, signal in data.items():
        borehole.add_datum(
            domain=domain_data,
            signal=signal,
            key=key,
            label=labels[key])

def add_csv(borehole, csv_filename, domain_key, data_keys, labels=None):
    """ Add data from a CSV file

        Don't try to read massive files in with this - it will probably
        fall over.
    """
    # Generate labels
    if labels is None:
        labels = dict([(k, k.replace('_', ' ')) for k in data_keys])

    # Parse file
    all_keys = [domain_key] + data_keys
    data = parse_csv(csv_filename, all_keys)

    # Generate domain data from intervals (we take midpoints here)
    domain_data = data[domain_key]
    del data[domain_key]

    # Add the datasets that need adding
    add_to_borehole(borehole, domain_data, data, labels)