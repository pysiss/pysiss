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
import sklearn.manifold
import matplotlib.pyplot
import borehole_analysis.plotting

class AnalystError(Exception): 

    """ Exception class thrown by Analyst class
    """

    pass


class AnalystNode(object):

    """ Object which stores one node of an analysis tree
    """

    def __init__(self, borehole=None, mother=None, data_mask=None):
        super(AnalystNode, self).__init__()
        if borehole is not None:
            if mother is not None:
                raise AnalystError('Analyst requires either a borehole OR '
                    'another analyst instance to get going')

            # We are at the root of the tree, so generate an analyst which 
            # sees the entire borehole dataset
            self.borehole = borehole
            self.labels = borehole.labels
            self.domain = borehole.domain
            self.data = borehole.data
            self.data_mask = None
            self.mother = None

        elif mother is not None:
            if borehole is not None:
                raise AnalystError('Analyst requires either a borehole OR '
                    'another analyst instance to get going')
            if data_mask is None:
                raise AnalystError('You need to specify a data view on the '
                    'mother Analyst instance')

            # We are in a node, so copy in views of mother instance
            self.domain = mother.domain[data_mask]
            self.data = mother.data[data_mask]
            self.borehole = mother.borehole
            self.labels = mother.labels

        else: 
            raise AnalystError('Analyst requires either a borehole or another '
                'analyst instance to get going')

        # Initialise node topology
        self.daughters = None

        # Analyse the current datasets for clusters
        self.products = {
            'edge_graph': None,
            'correlations': None,
            'clusters': None
        }
        self.__gen_edge_graph(force=True)
        self.__gen_correlation_graph(force=True)
        self.__gen_correlation_clusters(force=True)
        
    def partition(self):
        """ Partition the analyst instance into daughter nodes
        """
        pass

    def get_domain(self):
        """ Returns a view of the current domain
        """
        return self.domain

    def get_signal(self, *keys):
        """ Returns views of the current data for the given keys. If no keys 
            are specified, return views for all keys.
        """
        if keys is None:
            keys = self.labels.keys()
        indices = [self.labels[k][0] for k in keys]
        return dict((k, self.data.T[i]) for k, i in zip(keys, indices))

    def plot_connection_matrix(self):
        """ Plots the connection matrix assicated with the data in the current 
            node.

            :returns: handles to the figure and axes
        """
        # Calculate correlation matrix
        names = self.borehole.get_labels()
        correlations = self.products['correlations']

        # Plot results
        side_len = 0.5*len(names)
        fig = matplotlib.pyplot.figure(figsize=(side_len, side_len))
        axes = matplotlib.pyplot.gca()
        image = axes.imshow(correlations, 
            interpolation='none', 
            cmap=matplotlib.cm.get_cmap("RdBu_r"))
        cbar = matplotlib.pyplot.colorbar(image, 
            fraction=0.2, 
            shrink=(1 - 0.25))
        cbar.set_label('Correlation')
        axes.set_xticks(range(len(names)))
        axes.set_xticklabels(names, rotation=90,
            horizontalalignment='center',
            verticalalignment='top')
        axes.set_yticks(range(len(names)))
        axes.set_yticklabels(names)
        return fig, axes

    def plot_connection_graph(self, embedding=None):
        """ Plot the clusters and connections between data signals.

            We use manifold learning methods to find a low-dimension embedding 
            for visualisation. For the methods here we use a dense eigensolver 
            to achieve reproducibility (since arpack is initialised with 
            random vectors - the result would be different each time) In 
            addition, we use a large number of neighbours to capture the large-
            scale structure.

            This could potentially be sped up significantly by using a sparse 
            representation, at the cost of introducing some randomness to the 
            visualisation.

            :param embedding: The model to use to embed the nodes in two-dimensional space. If None, it defaults to 'isomap'.
            :type embedding: `'lle'` or `'isomap'`
            :returns: handles to the figure and axes
        """
        # Get node infomation
        names = self.borehole.get_labels()
        clusters = self.products['clusters']['as_vector'] 

        # Calculate embedding
        embedding = embedding or 'isomap'
        if embedding is 'isomap':
            node_position_model = sklearn.manifold.Isomap(
                n_components=2, 
                eigen_solver='dense', 
                n_neighbors=len(names) - 2)
        elif embedding is 'lle':
            node_position_model = sklearn.manifold.LocallyLinearEmbedding(
                n_components=2, 
                eigen_solver='dense', 
                n_neighbors=len(names) - 2)
        else:
            raise AnalystError("Embedding argument to plot_connection_graph"
                "must be one of 'lle' or 'isomap'")
        embedding = node_position_model.fit_transform(self.data.T).T

        # Plot results
        fig = matplotlib.pyplot.figure(figsize=(15, 15))
        borehole_analysis.plotting.plot_connection_graph(
            names=names,
            cluster_labels=clusters,
            embedding=embedding, 
            correlations=self.products['correlations'])
        return fig, matplotlib.pyplot.gca()

    def plot_borehole_data(self, keys_to_plot=None):
        """ Plot the data stored in the current node object

            :returns: handles to the figure and axes
        """
        if keys_to_plot is None:
            keys_to_plot = self.borehole.get_keys()

        # Get data from self
        domain = self.get_domain()
        signals = self.get_signal(*keys_to_plot)
        domain_bounds = (self.domain.min(), self.domain.max())

        # Plot data
        fig = matplotlib.pyplot.figure(figsize=(20, 1*len(keys_to_plot)))
        for i, key in enumerate(keys_to_plot):
            axes = matplotlib.pyplot.subplot(1, len(keys_to_plot), i+1)
            borehole_analysis.plotting.plot_signal(axes, 
                signal=signals[key], 
                domain=domain,
                orientation='vertical')
            axes.set_xlabel("")
            if i == 0:
                axes.set_ylabel('Depth (m)')
            else:
                axes.set_ylabel("")
                axes.set_yticklabels("")
            axes.set_ylim(domain_bounds)
            axes.set_title(self.labels[key][1])
        fig.tight_layout()
        return fig, axes

    def __gen_correlation_graph(self, force=False):
        """ Generate connections between signals in a borehole using a graph 
            Lasso algorithm.

            This returns the correlation graph C, which is a strictly lower-
            triangular matrix with the correlation between the ith and jth 
            signal is given by C[i][j].

            :param borehole_label: The label pointing to the borehole data
            :type borehole_label: str
            :returns: the correlation graph C and the fitted edge model
        """
        if self.products['correlations'] is not None and not force:
            return
        self.borehole.print_info('Generating covariance graph', 'info')
        self.__gen_edge_graph()

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

    def __gen_edge_graph(self, force=False):
        """ Generate an edge matrix structure for the current borehole 
        """
        if self.products['edge_graph'] is not None and not force:
            return
        self.borehole.print_info('Generating edge connections', 'info')
        self.products['edge_graph'] = \
            sklearn.covariance.GraphLassoCV()
        self.products['edge_graph'].fit(self.data)

    def __gen_correlation_clusters(self, force=False):
        """ Generate signal clusters using signal correlations as a metric.

            :param borehole: The borehole data
            :type borehole: `borehole_analysis.Borehole`
            :returns: a set of clusters as a dictionary, where the key is the 
                cluster label, and the value is a list of data labels from the 
                Borehole instance 
        """
        if self.products['clusters'] is not None and not force:
            return

        # Generate clusters
        self.borehole.print_info('Generating covariance clusters', 'info')
        self.__gen_edge_graph()
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


class Analyst(dict):
    
    """ Object to run analysis over sets of boreholes

        :param boreholes: A dict of boreholes, where the keyword is the 
            borehole label, and the value is a borehole_analysis.Borehole 
            instance.
        :type boreholes: dict
    """
    
    def __init__(self, boreholes):
        super(Analyst, self).__init__()

        # Store boreholes, and generate a root Analyst instance to get 
        # things going
        for label, borehole in boreholes.items():
            self[label] = {
                'borehole': borehole,
                'analyst_tree': AnalystNode(borehole)
            }
            self[label]['analyst_tree'].partition()
