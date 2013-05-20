#!/usr/bin/env python
""" file:   plotting.py (borehole_analysis)
    author: Jess Robertson
            CSIRO Earth Science and Resource Engineering
    email:  jesse.robertson@csiro.au
    date:   Wednesday May 1, 2013

    description: Plotting for the borehole_analysis module.
"""

import matplotlib.cm
import matplotlib.pyplot
import numpy
from borehole_analysis.clustering import generate_correlation_graph

def plot_connection_matrix(borehole):
    """ Plots the connection matrix assicated with an edge model

        This assumes you have a matrix with the connection between 
        the ith and jth nodes given in edge_matrix[i][j].

        :param edge_matrix: the matrix of edge weights
        :type edge_matrix: numpy.ndarray
        :param names: the labels for each node in the matrix
        :type names: iterable containing strings
        :returns: handles to the figure and axes
    """
    # Calculate correlation matrix
    names = borehole.get_labels()
    correlations, _ = generate_correlation_graph(borehole)

    # Plot results
    side_len = 0.5*len(names)
    fig = matplotlib.pyplot.figure(figsize=(side_len, side_len))
    axes = matplotlib.pyplot.gca()
    image = axes.imshow(correlations, 
        interpolation='none', 
        cmap=matplotlib.cm.get_cmap("RdBu_r"))
    cbar = matplotlib.pyplot.colorbar(image, fraction=0.2, shrink=(1 - 0.25))
    cbar.set_label('Correlation')
    axes.set_xticks(range(len(names)))
    axes.set_xticklabels(names, rotation=90,
                    horizontalalignment='center',
                    verticalalignment='top')
    axes.set_yticks(range(len(names)))
    axes.set_yticklabels(names)
    return fig, axes

def make_figure_grid(nplots, ncols=3, size=6):
    """ Make a grid of images
    """
    nrows = nplots / ncols
    if nrows * ncols != nplots:
        nrows += 1
    fig = matplotlib.pyplot.figure(figsize=(ncols * size, nrows * size))
    axeses = [matplotlib.pyplot.subplot(nrows, ncols, i+1) 
              for i in range(nplots)]
    return fig, axeses

def plot_variable(axes, variable, cmap=None):
    """ Generate a single image of a wavelet transform
    """
    if cmap is None:
        cmap = matplotlib.cm.get_cmap('Paired')
    axes.imshow(variable.T, cmap=cmap, interpolation='nearest')
    axes.set_aspect(variable.shape[0] / float(variable.shape[1]))
    axes.set_xlabel(r"Fourier Scale $\lambda_{i}$")
    axes.set_xticklabels([''])
    axes.set_xticks([])
    axes.set_ylabel(r"Domain $x_{i}$")
    axes.set_yticklabels([''])
    axes.set_yticks([])

def plot_difference(axes, domain, observed_value, expected_value, 
    colors=('red', 'blue'), orientation='horizontal'):
    """ Plots the difference between two series.

        This plot also includes a set of lines in the shading to indicate the sample spacing. You can set the colors that you want to use to highlight differences between the two series.

        :param axee: The axes to plot in
        :type axes: `matplotlib.pyplot.axes`
        :param domain: The domain variable
        :type domain: `numpy.ndarray`
        :param observed_value: The actual value given as a numpy array. Must be the same length as the domain vector.
        :type observed_value: `numpy.ndarray`
        :param expected_value: The expected value. Can be a constant, in which case the value will be constant, or an array of the same size as the domain.
        :type expected_value: `numpy.ndarray` or number
        :param colors: A tuple of colors. The fill and lines will be shaded `color[0]` when `observed_value` < `expected_value` and `color[1]` when `observed_value` >= `expected_value`. Any color accepted by matplotlib is allowed.
        :type colors: Tuple
        :param orientation: The orientation of the plot, one of 'horizontal', or 'vertical'.
        :type orientation: str
    """
    # Expand the expected value if required
    if type(expected_value) is not numpy.ndarray:
        expected_value = expected_value * numpy.ones_like(domain)

    # Helper functions for plotting the lines
    pos_diff = lambda a, b: a + numpy.maximum(b-a, 0)
    neg_diff = lambda a, b: a + numpy.minimum(b-a, 0)

    # Generate plot
    if orientation is 'horizontal':
        # Plot the two signals
        axes.plot(domain, observed_value, color='black', linewidth=1)
        axes.plot(domain, expected_value, 'k--', linewidth=1)

        # Generate fills
        axes.vlines(domain, expected_value, 
            pos_diff(expected_value, observed_value), color=colors[1])
        axes.vlines(domain, neg_diff(expected_value, observed_value), 
            expected_value, color=colors[0])
        axes.fill_between(domain, expected_value, observed_value, 
            where=(observed_value >= expected_value), 
            alpha=0.1, facecolor=colors[1])
        axes.fill_between(domain, expected_value, observed_value, 
            where=(observed_value <  expected_value), 
            alpha=0.1, facecolor=colors[0])
    elif orientation is 'vertical':
        # Plot the two signals
        axes.plot(observed_value, domain, color='black', linewidth=2)
        axes.plot(expected_value, domain, 'k--', linewidth=2)

        # Generate fills
        axes.hlines(domain, expected_value, 
            pos_diff(expected_value, observed_value), color=colors[1])
        axes.hlines(domain, neg_diff(expected_value, observed_value), 
            expected_value, color=colors[0])
        axes.fill_betweenx(domain, expected_value, observed_value, 
            where=(observed_value >= expected_value), 
            alpha=0.1, facecolor=colors[1])
        axes.fill_betweenx(domain, expected_value, observed_value, 
            where=(observed_value <  expected_value), 
            alpha=0.1, facecolor=colors[0])
    else:
        raise ValueError('Argument `orientation` must be "horizontal" or '
            'vertical"')

def plot_signal(axes, domain, signal, orientation='horizontal'):
    """ Plots a one-dimensional signal against some domain.

        This assumes that you're plotting a detrended signal, so it fills in red for negative anomalies and blue for positive anomalies, so that you can compare the deviation from the trend.

        :param axes: The axes instance in which to plot the signal
        :type axes: `matplotlib.axes`
        :param domain: An array of domain locations
        :type domain: `numpy.ndarray`
        :param signal: An array of signal values. Must be the same length as `domain` or an error will be raised.
        :type signal: `numpy.ndarray`
        :param orientation: One of `'horizontal'` or `'vertical'`
        :type orientation: `str`
    """
    # Generate plot
    plot_difference(axes, domain, signal, signal.mean(), 
        colors=('red', 'blue'),
        orientation=orientation)
    if orientation is 'horizontal':
        axes.set_xlabel('Domain $x$')
        axes.set_ylabel(r'Signal $f(x)$', 
            rotation=0,
            horizontalalignment='right',
            verticalalignment='center')
        axes.set_xlim(domain[0], domain[-1])
        axes.set_ylim(numpy.min(signal), numpy.max(signal))
    elif orientation is 'vertical':
        axes.set_ylabel('Domain $x$')
        axes.set_xlabel('Signal $f(x)$')
        axes.set_xlim(numpy.min(signal), numpy.max(signal))
        axes.set_ylim(domain[-1], domain[0])
    else:
        raise ValueError('Argument `orientation` must be "horizontal" or '
            'vertical"')

def plot_borehole_data(borehole, keys_to_plot):
    """ Plot the data stored in a borehole object

        :returns: handles to the figure and axes
    """
    # Get data from borehole
    domain = borehole.get_domain()
    signals = borehole.get_signal(*keys_to_plot)
    domain_bounds = (borehole.domain.min(), borehole.domain.max())

    # Plot data
    fig = matplotlib.pyplot.figure(figsize=(20, 1*len(keys_to_plot)))
    for i, key in enumerate(keys_to_plot):
        axes = matplotlib.pyplot.subplot(1, len(keys_to_plot), i+1)
        plot_signal(axes, signal=signals[key], domain=domain,
            orientation='vertical')
        axes.set_xlabel("")
        if i == 0:
            axes.set_ylabel('Depth (m)')
        else:
            axes.set_ylabel("")
            axes.set_yticklabels("")
        axes.set_ylim(domain_bounds)
        axes.set_title(borehole.labels[key][1])
    fig.tight_layout()
    return fig, axes