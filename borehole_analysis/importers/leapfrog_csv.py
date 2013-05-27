#!/usr/bin/env python
""" file: leapfrog_csv.py
    author: Jess Robertson
            CSIRO Earth Science and Resource Engineering
    date: Tuesday 21 May, 2013

    description: Utilities for munging CSV data exported from Leapfrog.
"""

from borehole_analysis.importers.normal_csv import parse_csv, add_to_borehole

def add_leapfrog_csv(borehole, csv_filename, data_keys, labels=None):
    """ Add data from a CSV file exported from Leapfrog 

        Don't try to read massive files in with this - it will probably 
        fall over.
    """
    # Generate labels
    if labels is None:
        labels = dict([(k, k.replace('_', ' ')) for k in data_keys])

    # Parse data from csv file
    all_keys = ['From', 'To'] + data_keys
    data = parse_csv(csv_filename, all_keys)

    # Generate domain data from intervals (we take midpoints here)
    domain_data = (data['To'] + data['From']) / 2.0
    del data['To']
    del data['From']

    # Add the datasets that need adding
    add_to_borehole(borehole, domain_data, data, labels)