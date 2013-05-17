#!/usr/bin/env python
""" file:   clustering.py (borehole_analysis)
    author: Jess Robertson
            CSIRO Earth Science and Resource Engineering
    email:  jesse.robertson@csiro.au
    date:   Wednesday May 1, 2013

    description: Clustering utilities for the borehole_analysis module.
"""

import numpy
import sklearn.covariance
import sklearn.cluster

def generate_correlation_graph(borehole):
    """ Generate connections between signals using a graph Lasso algorithm.

        This returns the correlation graph C, which is a strictly lower-triangular matrix with the correlation between the ith and jth signal is given by C[i][j].

        :param borehole: The borehole data
        :type borehole: `borehole_analysis.Borehole`
        :returns: the correlation graph C and the fitted edge model
    """
    borehole.print_info('Generating covariance graph...')
    edge_model = sklearn.covariance.GraphLassoCV()
    edge_model.fit(borehole.data)

    # Get the correlations from the model
    correlations = edge_model.precision_.copy()
    determinant = 1 / numpy.sqrt(numpy.diag(correlations))
    correlations *= determinant
    correlations *= determinant[:, numpy.newaxis]

    # We only care about off-axis correlations (since every signal is 
    # perfectly correlated with itself). Also remove half the graph since
    # the results are symmetric
    correlations = -numpy.tril(correlations, k=-1)
    correlations = numpy.ma.masked_array(correlations,
        mask=(numpy.abs(correlations) <= 0.02))
    return correlations, edge_model

def generate_correlation_clusters(borehole):
    """ Generate signal clusters using signal correlations as a metric.

        :param borehole: The borehole data
        :type borehole: `borehole_analysis.Borehole`
        :returns: a set of clusters as a dictionary, where the key is the cluster label, and the value is a list of data labels from the Borehole instance 
    """
    borehole.print_info('Generating covariance clusters...')
    edge_model = sklearn.covariance.GraphLassoCV()
    edge_model.fit(borehole.data)
    _, labels = sklearn.cluster.affinity_propagation(edge_model.covariance_)
    n_labels = labels.max()

    # Pass through clusters to borehole data
    clusters = dict([(i, borehole.names[labels == i]) 
        for i in range(n_labels + 1)])
    borehole.label_signals(labels)
    borehole.print_info('\n'.join(
        ['Cluster {0}: {1}'.format(l, c) for l, c in clusters.items()]))

