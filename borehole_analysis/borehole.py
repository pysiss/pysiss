#!/usr/bin/env python
""" file:   borehole.py (borehole_analysis)
    author: Jess Robertson
            CSIRO Earth Science and Resource Engineering
    email:  jesse.robertson@csiro.au
    date:   Wednesday May 1, 2013

    description: Data munging utilities for the borehole_analysis module.
"""

import numpy
from borehole_analysis.utilities import ReSampler, mask_all_nans, detrend

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
        self.samplers = {}
        self.labels = {}
        self.data = None
        self.domain = None
        self.default_sprops = {
            'nsamples': None,
            'domain_bounds': None
        }

    def add_datum(self, domain, signal, key, label=None):
        """ Add a single dataset to the Borehole
        """
        # Update names and symbols
        if label is None:
            label = key
        self.labels.update({key: (None, label)})
        self.print_info(
            'Adding dataset {0} with {1} entries, and label {2}'.format(
                key, len(signal), label), 'info')

        # Mask out Nans before generating resampler instance
        nan_mask = mask_all_nans(domain, signal)
        self.samplers[key] = ReSampler(
            domain = domain[nan_mask],
            signal = signal[nan_mask], 
            order=1)

        # Check whether this will change the bounds of the domain
        if self.default_sprops['nsamples'] is None:
            self.default_sprops['nsamples'] = len(domain[nan_mask])
            self.default_sprops['domain_bounds'] = (domain[nan_mask].min(), 
                domain[nan_mask].max())
        else:
            self.default_sprops['nsamples'] = max(
                self.default_sprops['nsamples'], 
                len(domain[nan_mask]))
            self.default_sprops['domain_bounds'] = (
                max(self.default_sprops['domain_bounds'][0], 
                    domain[nan_mask].min()),
                min(self.default_sprops['domain_bounds'][1], 
                    domain[nan_mask].max()))

    def resample(self, nsamples=None, domain_bounds=None, normalize=False, 
        detrend_method=None):
        """ Aligns and resamples data so that all vectors have the same length
            and sample spacing.

            This generates `data` and `domain` attributes for the Borehole 
            instance. The domain is a one-dimensional vector of length 
            `nsamples` containing the sample locations, and the `data` 
            instance is an array where each column contains the resampled data 
            for one of the datasets in the borehole.

            This uses masked arrays to remove NaN values from a series, and 
            then realigns the data sampling so that all signals are sampled at 
            the same time. It does this using linear interpolation.

            If `normalize=True`, then the data is then normalised so that 
            each column has zero mean and unit variance. To clear this (and go 
            back to unnormalised data), just call resample again wiht 
            `normalize=False`
        """
        # Align data
        self.print_info('Aligning datasets', 'info')

        # Define domain vector
        sampler_properties = self.default_sprops
        if nsamples is not None:
            sampler_properties['nsamples'] = nsamples
        if domain_bounds is None:
            sampler_properties['domain_bounds'] = domain_bounds

        # Generate empty data array and populate with data
        ndata = len(self.samplers)
        self.data = numpy.empty((ndata, sampler_properties['nsamples']), 
                                dtype=numpy.float)
        for index, key_and_sampler in enumerate(self.samplers.items()):
            key, sampler = key_and_sampler
            resampled_domain, resampled_signal = \
                sampler.resample(**sampler_properties) 
            if detrend_method is not None:
                detrend(resampled_signal, detrend_method)
            self.data[index] = resampled_signal
            self.labels[key] = (index, self.labels[key][1])

        # Transpose data
        self.data = self.data.T
        self.domain = resampled_domain

        # Generate normalised data if required
        if normalize:
            self.print_info('Normalising datasets', 'info')
            self.data = (self.data - self.data.mean(axis=0)) \
                        / self.data.std(axis=0)

    def get_raw_data(self, *keys):
        """ Returns the raw data used in the Borehole resamplers.
        """
        if keys is None:
            keys = self.labels.keys()

        data = {}
        for key in keys:
            data[key] = dict(
                key=key,
                signal=self.samplers[key].signal, 
                domain=self.samplers[key].domain, 
                label=self.labels[key])

        return data

    def get_keys(self):
        """ Return the keys for all the variables in the borehole dataset

            These are guarenteed to come back in the order they are stored in 
            the data array.
        """
        keys, indices = [], []
        for key in self.labels.keys():
            keys.append(key)
            indices.append(self.labels[key][0])
        return [keys[i] for i in indices]

    def get_labels(self, *keys):
        """ Return the labels for the given keys. If no keys are specified, 
            return labels for all keys.

            These are guarenteed to come back in the order they are stored in 
            the data array.
        """
        if not keys: 
            return [self.labels[k][1] for k in self.get_keys()]
        else:
            return [self.labels[k][1] for k in self.get_keys()
                                      if k in keys]

    def get_domain(self):
        """ Returns a view of the current domain
        """
        return self.domain

    def get_signal(self, *keys):
        """ Returns views of the current data for the given keys. If no keys 
            are specified, return views for all keys.

            These are guarenteed to come back in the order they are stored in 
            the data array.
        """
        if keys is None:
            indices = [self.labels[k][0] for k in self.get_keys()]
        else:
            indices = [self.labels[k][0] for k in self.get_keys() if k in keys]
        return dict((k, self.data.T[i]) for k, i in zip(keys, indices))

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
