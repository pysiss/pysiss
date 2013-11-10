#!/usr/bin/env python
""" file:   borehole.py (python_boreholes)
    author: Jess Robertson
            CSIRO Earth Science and Resource Engineering
    email:  jesse.robertson@csiro.au
    date:   Wednesday May 1, 2013

    description: Data munging utilities for the python_boreholes module.
"""

import pandas, numpy
from python_boreholes.utilities import mask_all_nans

def boreholes_from_csv(csvfile, borehole_key, domain_key=None,
    labels=None, verbose=False):
    """ Return a borehole from a csv via a pandas.dataframe instance
    """
    dataframe = pandas.read_csv(csvfile)
    dataframe = dataframe.convert_objects(convert_numeric=True)
    if domain_key is None:
        dataframe['Depth'] = (dataframe['From'] + dataframe['To']) / 2.
        domain_key = 'Depth'
    if labels is None:
        labels = { k: k for k in dataframe.keys() }

    # Group into boreholes
    grouped = dataframe.groupby(borehole_key)
    boreholes = list()
    for name, datum in grouped:
        data_dict = { key: (numpy.asarray(datum[key]), label)
            for key, label in labels.items() }
        boreholes.append((name,
            Borehole(
                domain=numpy.asarray(datum[domain_key]),
                data=data_dict,
                verbose=verbose)))
    return boreholes


class Borehole(object):

    """ A class to manage borehole data

        :param data: A dict containing the following keys: 'ID', with an ID
            for the dataset, 'label', with the label of the dataset as a
            value, 'domain', with the sample locations, and 'signal', with the
            signal values corresponding to the sample locations in 'domain'.
        :type data: tuple
    """

    def __init__(self, verbose=False):
        super(Borehole, self).__init__()

        # Initialise attributes
        self.verbose = verbose
        self.labels = {}
        self.data = {}
        self.__current_index = 0

    def add_datum(self, domain, data, key, label=None):
        """ Add a single dataset to the borehole
        """
        # Update labels
        if label is not None:
            labels[key] = label
        else:
            labels[key] = key

        # Check that all data is (a) NaN-free ...
        datum = data_values[0]
        nan_mask = mask_all_nans(domain, datum)
        _domain = domain[nan_mask]
        _datum = datum[nan_mask]

        # ... and (b) domain-ordered
        order_idx = numpy.argsort(_domain)
        self.data[key]['domain'] = _domain[order_idx][:]
        self.data[key]['data'] = _data[order_idx][:]

        # Split domain into seperate values

    def print_info(self, message, flag=None):
        """ Print a message if we're tracking transformations
        """
        header_dict = {
            'default': '         ',
            'info': '   info: ',
            'warn': 'warning: '
        }
        if self.verbose:
            try:
                header = header_dict[flag]
            except KeyError:
                header = header_dict['default']
            print header, message

    def find_sampling_interval_gaps(sampling_interval, coeff=10):
        """ Find subdomains which remove large gaps in a given dataset.

            A 'large' gap is defined as any non-NaN data for which the gap
            between this sample and the next is more than coeff * the median
            sample spacing. This function identifies these gaps and returns a
            set of domain intervals which are 'non-gappy' by this definition.

            :returns:
                An IntervalDomain subdivided into 'data' and 'gap' regions
        """
        # Generate subdomains within the domain
        spacing = numpy.diff(self.domain)
        med_spacing = numpy.median(spacing)
        gap_indices = numpy.flatnonzero(spacing > coeff * med_spacing)

        # Form a list of data subdomains
        subdomains = [(self.domain[0], self.domain[gap_indices[0]])]
        for idx in range(len(gap_indices) - 1):
            subdomains.append((p0
                self.domain[gap_indices[idx] + 1],   # Start _after_ the gap!
                self.domain[gap_indices[idx + 1]]))  # End with next gap
        subdomains.append((self.domain[gap_indices[-1] + 1], self.domain[-1]))
        return subdomains