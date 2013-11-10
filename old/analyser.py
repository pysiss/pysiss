#!/usr/bin/env python
""" file:   analyser.py (python_boreholes)
    author: Jess Robertson
            CSIRO Earth Science and Resource Engineering
    email:  jesse.robertson@csiro.au
    date:   Wednesday May 1, 2013

    description: Clustering utilities for the python_boreholes module.
"""

import numpy
from python_boreholes.utilities import detrend
import sklearn.covariance
import sklearn.cluster
import sklearn.manifold
import sklearn.decomposition

class AnalystError(Exception):
    """ Exception class thrown by Analyst class
    """
    pass


class Analyst(object):

    """ Object which stores one node of an analysis tree
    """

    def __init__(self, borehole=None, mother=None, data_mask=None):
        if borehole is not None:
            if mother is not None:
                raise AnalystError('Analyst requires either a borehole OR '
                    'another analyst instance to get going')

            # We are at the root of the tree, so generate an analyst which
            # sees the entire borehole dataset
            self.borehole = borehole
            self.labels = borehole.labels
            self.domain = borehole.domain
            self.data_mask = numpy.ones(len(self.domain))
            self.mother = None

        elif mother is not None:
            if borehole is not None:
                raise AnalystError('Analyst requires either a borehole OR '
                    'another analyst instance to get going, not both!')
            if data_mask is None:
                raise AnalystError('You need to specify a data view on the '
                    'mother Analyst instance')

            # We are in a node, so copy in views of mother instance
            self.data_mask = data_mask
            self.borehole = mother.borehole
            self.domain = self.borehole.domain[self.data_mask]
            self.data = self.borehole.data[self.data_mask]
            self.labels = self.borehole.labels

        else:
            raise AnalystError('Analyst requires either a borehole or another '
                'analyst instance to get going')

        # Initialise node topology
        self.daughters = None
        self.products = {
            'edge_graph': None,
            'clusters': None,
            'correlations': None,
            'eigensignals': None
        }
        self.default_sampler_props = {
            'nsamples': None,
            'domain_bounds': None,
        }

    def partition(self):
        """ Partition the analyst instance into daughter nodes
        """
        pass

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
        self.borehole.print_info('Aligning datasets', 'info')

        # Define domain vector
        sampler_properties = self.default_sampler_props
        if nsamples is not None:
            sampler_properties['nsamples'] = nsamples
        if domain_bounds is None:
            sampler_properties['domain_bounds'] = domain_bounds

        # Generate empty data array and populate with data
        ndata = len(self.samplers)
        self.data = numpy.empty((ndata, sampler_properties['nsamples']),
                                dtype=numpy.float)
        for index, key_and_sampler in enumerate(self.borehole.samplers.items()):
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
            self.borehole.print_info('Normalising datasets', 'info')
            self.data = (self.data - self.data.mean(axis=0)) \
                        / self.data.std(axis=0)

    def generate_correlation_graph(self, force=False):
        """ Generate connections between signals in a borehole using a graph
            Lasso algorithm.
        """
        if self.products['correlations'] is not None and not force:
            return
        self.borehole.print_info('Generating covariance graph', 'info')
        self.generate_edge_graph()

        # Get the correlations from the model
        correlations = self.products['edge_graph'].precision_.copy()
        determinant = 1 / numpy.sqrt(numpy.diag(correlations))
        correlations *= determinant
        correlations *= determinant[:, numpy.newaxis]

        # We only care about off-axis correlations (since every signal is
        # perfectly correlated with itself). Also remove half the graph since
        # the results are symmetric
        correlations = -numpy.tril(correlations, k=-1)
        self.products['correlations'] = numpy.ma.masked_array(correlations,
            mask=(numpy.abs(correlations) <= 0.02))

    def generate_edge_graph(self, force=False):
        """ Generate an edge matrix structure for the current borehole
        """
        if self.products['edge_graph'] is not None and not force:
            return
        self.borehole.print_info('Generating edge connections', 'info')
        self.products['edge_graph'] = \
            sklearn.covariance.GraphLassoCV()
        self.products['edge_graph'].fit(self.data)

    def generate_correlation_clusters(self, force=False):
        """ Generate signal clusters using signal correlations as a metric.
        """
        if self.products['clusters'] is not None and not force:
            return

        # Generate clusters
        self.borehole.print_info('Generating covariance clusters', 'info')
        self.generate_edge_graph()
        _, cluster_labels = sklearn.cluster.affinity_propagation(
            self.products['edge_graph'].covariance_)

        # Store results as dictionary - we have two values, one for human
        # consumption and one by key for looping
        keys = self.borehole.get_keys()
        labels = self.borehole.get_labels()
        self.products['clusters'] = {
            'by_label': dict([(li, [n for l, n in zip(cluster_labels, labels)
                                      if l == li])
                              for li in range(cluster_labels.max() + 1)]),
            'by_key': dict([(li, [k for l, k in zip(cluster_labels, keys)
                                    if l == li])
                             for li in range(cluster_labels.max() + 1)]),
            'as_vector': cluster_labels
        }

        # Print information if required
        self.borehole.print_info('Clusters: \n'
            + '\n'.join(['   -- {0}: {1}'.format(l, c)
                for l, c in self.products['clusters']['by_label'].items()]),
            'info')

    def generate_eigensignals(self, force=False):
        """ Generate eigensignals using ICA for each cluster
        """
        if self.products['eigensignals'] is not None and not force:
            return

        estimator = sklearn.decomposition.FastICA(
            n_components=None, algorithm='parallel', whiten=True, max_iter=10)
        clusters = self.products['clusters']['by_key']
        self.products['eigensignals'] = []
        self.products['mixing_matrices'] = []
        for cluster_keys in clusters.values():
            # Get signals for current cluster
            indices = numpy.array([self.labels[k][0] for k in cluster_keys])
            data = self.data.T[indices]

            # Generate sources from cluster signals
            estimator.fit(data.T)
            self.products['eigensignals'].append(estimator.sources_.T)
            self.products['mixing_matrices'].append(estimator.components_.T)
