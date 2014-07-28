""" file:   plotting.py (pysiss.borehole)
    author: Jess Robertson
            CSIRO Earth Science and Resource Engineering
    email:  jesse.robertson@csiro.au
    date:   Wednesday May 1, 2013

    description: Plotting for the pysiss.borehole module.
"""

import matplotlib.pyplot
import matplotlib.cm
import matplotlib.collections
import numpy


def make_figure_grid(nplots, ncols=3, size=6):
    """ Make a grid of images
    """
    nrows = nplots / ncols
    if nrows * ncols != nplots:
        nrows += 1
    fig = matplotlib.pyplot.figure(figsize=(ncols * size, nrows * size))
    axeses = [matplotlib.pyplot.subplot(nrows, ncols, i + 1)
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
    axes.set_ylabel(r"DataSet $x_{i}$")
    axes.set_yticklabels([''])
    axes.set_yticks([])


def plot_difference(axes, dataset, observed_value, expected_value,
                    colors=('red', 'blue'), orientation='horizontal'):
    """ Plots the difference between two series.

        This plot also includes a set of lines in the shading to indicate the
        sample spacing. You can set the colors that you want to use to
        highlight differences between the two series.

        :param axee: The axes to plot in
        :type axes: `matplotlib.pyplot.axes`
        :param dataset: The dataset variable
        :type dataset: `numpy.ndarray`
        :param observed_value: The actual value given as a numpy array. Must
            be the same length as the dataset vector.
        :type observed_value: `numpy.ndarray`
        :param expected_value: The expected value. Can be a constant, in which
            case the value will be constant, or an array of the same size as
            the dataset.
        :type expected_value: `numpy.ndarray` or number
        :param colors: A tuple of colors. The fill and lines will be shaded
            `color[0]` when `observed_value` < `expected_value` and `color[1]`
            when `observed_value` >= `expected_value`. Any color accepted by
            matplotlib is allowed.
        :type colors: Tuple
        :param orientation: The orientation of the plot, one of 'horizontal',
            or 'vertical'.
        :type orientation: str
    """
    # Expand the expected value if required
    if type(expected_value) is not numpy.ndarray:
        expected_value = expected_value * numpy.ones_like(dataset)

    # Helper functions for plotting the lines
    pos_diff = lambda a, b: a + numpy.maximum(b - a, 0)
    neg_diff = lambda a, b: a + numpy.minimum(b - a, 0)

    # Generate plot
    if orientation is 'horizontal':
        # Plot the two signals
        axes.plot(dataset, observed_value, color='black', linewidth=1)
        axes.plot(dataset, expected_value, 'k--', linewidth=1)

        # Generate fills
        axes.vlines(dataset, expected_value,
                    pos_diff(expected_value, observed_value),
                    color=colors[1])
        axes.vlines(dataset, neg_diff(expected_value, observed_value),
                    expected_value, color=colors[0])
        axes.fill_between(dataset, expected_value, observed_value,
                          where=(observed_value >= expected_value),
                          alpha=0.1,
                          facecolor=colors[1])
        axes.fill_between(dataset, expected_value, observed_value,
                          where=(observed_value < expected_value),
                          alpha=0.1,
                          facecolor=colors[0])
    elif orientation is 'vertical':
        # Plot the two signals
        axes.plot(observed_value, dataset, color='black', linewidth=2)
        axes.plot(expected_value, dataset, 'k--', linewidth=2)

        # Generate fills
        axes.hlines(dataset, expected_value,
                    pos_diff(expected_value, observed_value),
                    color=colors[1])
        axes.hlines(dataset, neg_diff(expected_value, observed_value),
                    expected_value, color=colors[0])
        axes.fill_betweenx(dataset, expected_value, observed_value,
                           where=(observed_value >= expected_value),
                           alpha=0.1,
                           facecolor=colors[1])
        axes.fill_betweenx(dataset, expected_value, observed_value,
                           where=(observed_value < expected_value),
                           alpha=0.1,
                           facecolor=colors[0])
    else:
        raise ValueError('Argument `orientation` must be "horizontal" or '
                         'vertical"')


def plot_signal(axes, dataset, signal, orientation='horizontal'):
    """ Plots a one-dimensional signal against some dataset.

        This assumes that you're plotting a detrended signal, so it fills in
        red for negative anomalies and blue for positive anomalies, so that
        you can compare the deviation from the trend.

        :param axes: The axes instance in which to plot the signal
        :type axes: `matplotlib.axes`
        :param dataset: An array of dataset locations
        :type dataset: `numpy.ndarray`
        :param signal: An array of signal values. Must be the same length as
            `dataset` or an error will be raised.
        :type signal: `numpy.ndarray`
        :param orientation: One of `'horizontal'` or `'vertical'`
        :type orientation: `str`
    """
    # Generate plot
    plot_difference(axes, dataset, signal, signal.mean(),
                    colors=('red', 'blue'),
                    orientation=orientation)
    if orientation is 'horizontal':
        axes.set_xlabel('DataSet $x$')
        axes.set_ylabel(r'Signal $f(x)$',
                        rotation=0,
                        horizontalalignment='right',
                        verticalalignment='center')
        axes.set_xlim(dataset[0], dataset[-1])
        axes.set_ylim(numpy.min(signal), numpy.max(signal))
    elif orientation is 'vertical':
        axes.set_ylabel('DataSet $x$')
        axes.set_xlabel('Signal $f(x)$')
        axes.set_xlim(numpy.min(signal), numpy.max(signal))
        axes.set_ylim(dataset[-1], dataset[0])
    else:
        raise ValueError('Argument `orientation` must be "horizontal" or '
                         'vertical"')


def plot_connection_graph(embedding, correlations, names, cluster_labels):
    """ Plots a connection graph in 2D given an embedding and a correlation
        matrix.
    """
    # Plot the nodes using the coordinates of our embedding
    axes = matplotlib.pyplot.gca()
    axes.scatter(embedding[0], embedding[1],
                 c=cluster_labels,
                 cmap=matplotlib.cm.get_cmap('Spectral'))

    # Plot the edges - a sequence of (*line0*, *line1*, *line2*), where
    #            linen = (x0, y0), (x1, y1), ... (xm, ym)
    non_zero = numpy.logical_not(correlations.mask)
    start_idx, end_idx = numpy.where(non_zero)
    segments = [[embedding[:, start], embedding[:, stop]]
                for start, stop in zip(start_idx, end_idx)]
    values = correlations[non_zero]
    lines = matplotlib.collections.LineCollection(
        segments,
        zorder=0,
        cmap=matplotlib.cm.get_cmap('RdBu'),
        norm=matplotlib.pylab.Normalize(.7 * values.min(), .7 * values.max()))
    lines.set_array(values)
    lines.set_linewidths(15 * numpy.abs(values))
    axes.add_collection(lines)

    # Add a label to each node
    label_info = zip(names, cluster_labels, embedding.T)
    for index, (name, label, (xloc, yloc)) in enumerate(label_info):
        (xloc, yloc), alignment = float_label(index, (xloc, yloc), embedding)
        point_color = matplotlib.cm.get_cmap('Spectral')(
            label / float(max(cluster_labels)))
        matplotlib.pylab.text(
            xloc, yloc, name, size=10,
            horizontalalignment=alignment[0],
            verticalalignment=alignment[1],
            bbox=dict(facecolor=point_color,
                      edgecolor=point_color,
                      alpha=.3))

    # Adjust axes limits
    axes.set_xlim(embedding[0].min() - .15 * embedding[0].ptp(),
                  embedding[0].max() + .10 * embedding[0].ptp(),)
    axes.set_ylim(embedding[1].min() - .03 * embedding[1].ptp(),
                  embedding[1].max() + .03 * embedding[1].ptp())


def float_label(index, position, embedding):
    """ Floating labels for plot so that they avoid one another.

        The challenge here is that we want to position the labels to avoid
        overlap with other labels. We use the neighbour data in the embedding
        to juggle the label positions to avoid collisions.
    """
    xloc, yloc = position
    dxloc = xloc - embedding[0]
    dxloc[index] = 1
    dyloc = yloc - embedding[1]
    dyloc[index] = 1
    this_dxloc = dxloc[numpy.argmin(numpy.abs(dyloc))]
    this_dyloc = dyloc[numpy.argmin(numpy.abs(dxloc))]
    if this_dxloc > 0:
        horizontalalignment = 'left'
        xloc += .002
        yloc += .001
    else:
        horizontalalignment = 'right'
        xloc -= .002
        yloc -= .001
    if this_dyloc > 0:
        verticalalignment = 'bottom'
        yloc += .002
        xloc += .001
    else:
        verticalalignment = 'top'
        yloc -= .002
        xloc -= .001

    return (xloc, yloc), (horizontalalignment, verticalalignment)


## Borehole plotting
def plot_point_dataset_data(point_dataset, keys_to_plot=None):
    """ Plot the data stored in the current node object

        :returns: handles to the figure and axes
    """
    if keys_to_plot is None:
        keys_to_plot = [
            k for k in point_dataset.properties.keys()
            if point_dataset.properties[k].property_type.isnumeric]

    # Plot data
    fig = matplotlib.pyplot.figure(figsize=(1 * len(keys_to_plot), 20))
    dataset_bounds = (point_dataset.depths.max(),
                      point_dataset.depths.min())
    for i, key in enumerate(keys_to_plot):
        axes = matplotlib.pyplot.subplot(1, len(keys_to_plot), i + 1)
        try:
            plot_signal(axes,
                        signal=point_dataset.properties[key].values,
                        dataset=point_dataset.depths,
                        orientation='vertical')
        except TypeError:
            print key
        axes.set_xlabel("")
        if i == 0:
            axes.set_ylabel('Depth (m)')
        else:
            axes.set_ylabel("")
            axes.set_yticklabels("")
        axes.set_ylim(dataset_bounds)
        axes.xaxis.set_major_locator(matplotlib.pyplot.MaxNLocator(3))
        axes.set_title(point_dataset.properties[key].property_type.long_name,
                       rotation=90,
                       verticalalignment='bottom',
                       horizontalalignment='center')
    fig.tight_layout()
    return fig, axes


def gen_axes_grid(nplots, ncols):
    """ Make an axes grid with the given number of columns and plots
    """
    nrows = nplots // ncols
    if nrows * ncols != nplots:
        nrows += 1
    return matplotlib.gridspec.GridSpec(nrows, ncols)
