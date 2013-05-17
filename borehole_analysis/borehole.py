#!/usr/bin/env python
""" file:   borehole.py (borehole_analysis)
    author: Jess Robertson
            CSIRO Earth Science and Resource Engineering
    email:  jesse.robertson@csiro.au
    date:   Wednesday May 1, 2013

    description: Data munging utilities for the borehole_analysis module.
"""

import numpy
from csv import DictReader
from itertools import repeat
from borehole_analysis.utilities import ReSampler

class Borehole(object):

    """ A class to manage borehole data

        :param data: A dict containing the following keys: 'ID', with an ID for the dataset, 'label', with the label of the dataset as a value, 'domain', with the sample locations, and 'signal', with the signal values corresponding to the sample locations in 'domain'.
        :type data: tuple
    """

    def __init__(self, verbose=False):
        super(Borehole, self).__init__()
        
        # Initialise attributes
        self.verbose = verbose
        self.long_labels = {}
        self.raw_data = {}
        self.raw_data_array = None
        self.label_indices = {}
        self.data = None
        self.domain = None
        self.resamplable_data = []
        self.default_nsamples = None
        self.default_domain_bounds = None

    def add_datum(self, domain, signal, label, long_label=None, resample=True):
        """ Add a single dataset to the Borehole
        """
        # Update names and symbols
        if long_label is None:
            long_label = label
        self.long_labels.update({label: long_label})
        self.print_info(
            'Adding dataset labelled {0} with {1} entries'.format(
                long_label, len(signal)), 'info')

        # Mask out Nans before generating resampler instance
        if resample:
            self.resamplable_data.append(label)
            nan_mask = numpy.logical_not(numpy.logical_or(numpy.isnan(signal), 
                numpy.isnan(domain)))
            self.raw_data[label] = ReSampler(
                domain = domain[nan_mask],
                signal = signal[nan_mask], 
                order=1)

            # Check whether this will change the bounds of the domain
            if self.default_nsamples is None:
                self.default_nsamples = len(domain[nan_mask])
                self.default_domain_bounds = (domain[nan_mask].min(), 
                    domain[nan_mask].max())
            else:
                self.default_nsamples = max(self.default_nsamples, 
                    len(domain[nan_mask]))
                self.default_domain_bounds = (
                    max(self.default_domain_bounds[0], domain[nan_mask].min()),
                    min(self.default_domain_bounds[1], domain[nan_mask].max()))

        else:
            self.raw_data[label] = dict(domain=domain, signal=signal)


    def align_data(self, nsamples=None, domain_bounds=None):
        """ Aligns and resamples data so that all vectors have the same length
            and sample spacing.

            This uses masked arrays to remove NaN values from a series, and 
            then realigns the data sampling so that all signals are 
            sampled at the same time. It does this using linear 
            interpolation.
        """
        # Align data
        self.print_info('Aligning datasets', 'info')

        # Define domain vector
        if nsamples is None:
            nsamples = self.default_nsamples
        if domain_bounds is None:
            domain_bounds = self.default_domain_bounds

        # Generate empty data array and populate with data
        self.raw_data_array = numpy.empty(
            (len(self.resamplable_data), nsamples), dtype=numpy.float_)
        self.label_indices = {}
        for index, label in enumerate(self.resamplable_data):
            resampled_domain, resampled_signal = \
                self.raw_data[label].resample(
                    domain_bounds=domain_bounds,
                    nsamples=nsamples) 
            self.raw_data_array[index] = resampled_signal
            self.label_indices[label] = index
        self.domain = resampled_domain

        # Generate normalised data
        self.print_info('Normalising datasets', 'info')
        self.data = (self.raw_data_array - self.raw_data_array.mean(axis=0)) \
                        / self.raw_data_array.std(axis=0)

    def get_raw_data(self):
        """ Returns the raw data used in the Borehole
        """
        data = {}
        for label, data in self.raw_data.items():
            try:
                # Assume data is a ReSampler instance
                data[label] = dict(
                    label=label,
                    signal=data.signal, 
                    domain=data.domain, 
                    long_label=self.long_labels[label])
            except AttributeError:
                # Oops, we've only got a dictionary
                data[label] = dict(
                    label=label,
                    signal=data['signal'], 
                    domain=data['domain'], 
                    long_label=self.long_labels[label])

        return data

    def import_from_csv(self, filename, domain_key, not_float=None, long_labels=None):
        """ Import table from a CSV file. 

            Don't try to read massive files in with this - it will probably fall over.
        """
        # Parse data from csv file
        with open(filename, 'rb') as fhandle:
            # Read in data to DictReader
            reader = DictReader(fhandle)
            data_dicts = [l for l in reader]
            
            # Generate the list of dicts
            all_keys = set(reader.fieldnames)
            all_data = dict([(k, []) for k in all_keys])
            
            # Cycle through and covert where necessady
            for ddict in data_dicts:
                current_dict = dict(zip(all_keys, repeat(numpy.nan)))
                current_dict.update(ddict)
                for key, value in current_dict.items():
                    try:
                        # This should work 99% of the time because most things are numbers
                        all_data[key].append(float(value))
                    except ValueError:
                        if key in not_float:
                            # We've got a string, so just append to the list
                            all_data[key].append(value)
                        else:
                            # We need floats, so just tag with NaN
                            all_data[key].append(numpy.nan)

        # Convert arrays to numpy arrays
        all_data = dict([(k, numpy.asarray(all_data[k])) for k in all_keys])
        domain_data = numpy.asarray(all_data[domain_key])
        if long_labels is not None:
            for key, dataset in all_data.items():
                try:
                    long_label = long_labels[key]
                except KeyError:
                    long_label = None
                self.add_datum(
                    domain=domain_data,
                    signal=numpy.asarray(dataset),
                    label=key,
                    resample=(key not in not_float),
                    long_label=long_label)
        else:
            for key, dataset in all_data.items():
                self.add_datum(
                    domain=domain_data,
                    signal=numpy.asarray(dataset),
                    label=key,
                    resample=(key not in not_float))

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