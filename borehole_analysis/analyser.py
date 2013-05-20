#!/usr/bin/env python
""" file:   analyser.py (borehole_analysis)
    author: Jess Robertson
            CSIRO Earth Science and Resource Engineering
    email:  jesse.robertson@csiro.au
    date:   Wednesday May 1, 2013

    description: Clustering utilities for the borehole_analysis module.
"""

import numpy
import sklearn.covariance
import sklearn.cluster

class AnalystError(Exception): pass

class Analyst(object):

    """ Object which stores one node of an analysis tree
    """

    def __init__(self, borehole=None, mother=None, data_view=None):
        super(Analyst, self).__init__()
        if borehole is not None:
            if mother is not None:
                raise AnalystError('Analyst requires either a borehole OR another analyst instance to get going')

            # We are at the root of the tree, so generate an analyst which sees the entire borehole dataset
            self.borehole = borehole
            self.labels = borehole.labels
            self.data_view = None
            self.mother = None
        elif mother is not None:
            if borehole is not None:
                raise AnalystError('Analyst requires either a borehole OR another analyst instance to get going')
            if data_view is None:
                raise AnalystError("You need to specify a data view on the mother Analyst instance")

            # We are in a node, so copy in views of mother instance
            self.data = mother.data[data_view]
            self.borehole = mother.borehole
            self.labels = mother.labels
        else: 
            raise AnalystError('Analyst requires either a borehole or another analyst instance to get going')

            # Initialise node topology
        self.products = {
            'edge_model': None,
            'correlations': None,
            'clusters': None
        }
        self.daughters = None

    def partition(self):
        """ Partition the analyst instance into daughter nodes
        """
        # Analyse the current datasets for clusters
        self.__gen_edge_matrix()
        self.__gen_correlation_graph()
        self.__gen_correlation_clusters()

    def __gen_correlation_graph(self, borehole_label, force=False):
        """ Generate connections between signals in a borehole using a graph Lasso algorithm.

            This returns the correlation graph C, which is a strictly lower-
            triangular matrix with the correlation between the ith and jth 
            signal is given by C[i][j].

            :param borehole_label: The label pointing to the borehole data
            :type borehole_label: str
            :returns: the correlation graph C and the fitted edge model
        """
        if self.products['edge_model'] is not None and not force:
            return
        self.print_info('Generating covariance graph', 'info')
        self.__gen_edge_matrix()

        # Get the correlations from the model
        correlations = self.products['edge_model'].precision_.copy()
        determinant = 1 / numpy.sqrt(numpy.diag(correlations))
        correlations *= determinant
        correlations *= determinant[:, numpy.newaxis]

        # We only care about off-axis correlations (since every signal is 
        # perfectly correlated with itself). Also remove half the graph since
        # the results are symmetric
        correlations = -numpy.tril(correlations, k=-1)
        correlations = numpy.ma.masked_array(correlations,
            mask=(numpy.abs(correlations) <= 0.02))
        self[borehole_label]['correlations'] = correlations

    def __gen_edge_matrix(self, force=False):
        """ Generate an edge matrix structure for the current borehole 
        """
        if self.products['edge_model'] is not None and not force:
            return
        self.print_info('Generating edge connections', 'info')
        self.products['edge_model'] = \
            sklearn.covariance.GraphLassoCV()
        self.products['edge_model'].fit(borehole.data)

    def __gen_correlation_clusters(self, force=False):
        """ Generate signal clusters using signal correlations as a metric.

            :param borehole: The borehole data
            :type borehole: `borehole_analysis.Borehole`
            :returns: a set of clusters as a dictionary, where the key is the cluster label, and the value is a list of data labels from the Borehole instance 
        """
        if self[borehole_label]['clusters'] is not None and not force:
            return

        # Generate clusters
        self.print_info('Generating covariance clusters', 'info')
        self.__gen_edge_model()
        _, labels = sklearn.cluster.affinity_propagation(
                                    self.['edge_model'].covariance_)

        # Store results as dictionary - we have two values, one for human 
        # consumption and one by key for looping
        names = [v[1] for v in self.labels.values()]
        self.products['clusters'] = {
            'by_label': dict([(li, [n for l, n in zip(labels, names) 
                                      if l == li]) 
                              for li in range(labels.max() + 1)]),
            'by_key': dict([(li, [k for l, k in zip(labels, self.labels.keys())
                                    if l == li]) 
                             for li in range(labels.max() + 1)]),
        }
        
        # Print information if required
        self.print_info('Clusters: \n' 
            + '\n'.join(['   -- {0}: {1}'.format(l, c)
                for l, c in self.products['clusters']['by_label'].items()]),
            'info')

    def print_info(self, message, flag=None):
        """ Print a message if we're tracking transformations
        """
        header_dict = {
            'default': '         ',
            'info': '   info: ',
            'warn': 'warning: '
        }
        if self.borehole.verbose:
            try:
                header = header_dict[flag]
            except KeyError:
                header = header_dict['default']
            print header, message


class Analyser(dict):
    
    """ Object to run analysis over sets of boreholes

        :param **boreholes: A list of boreholes given as keyword arguments, where the keyword is the borehole label, and the value is a borehole_analysis.Borehole instance.
    """
    
    def __init__(self, **boreholes):
        super(Analyser, self).__init__()

        # Store boreholes, and generate a root Analyst instance to get 
        # things going
        for label, borehole in boreholes.items():
            self[label] = {
                'borehole': borehole
                'analyst_tree': Analyst(borehole)
            }
            self[label]['analyst_tree'].partition()
