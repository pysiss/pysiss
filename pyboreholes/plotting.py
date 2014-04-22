""" file:   plotting.py (pyboreholes)
    author: Jess Robertson
            CSIRO Earth Science and Resource Engineering
    email:  jesse.robertson@csiro.au
    date:   Wednesday May 1, 2013

    description: Plotting for the pyboreholes module.
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


def wavelet_plot(wavelet_dataset, property_name):
    """ Plot a CWT decomposition for a given dataset
    """
    # Set up figure
    fig = matplotlib.pyplot.figure(figsize=(8, 12))
    grid = matplotlib.gridspec.GridSpec(1, 2, width_ratios=[0.1, 1])
    trace_ax = matplotlib.pyplot.subplot(grid[0])
    transform_ax = matplotlib.pyplot.subplot(grid[1])

    # Get info from wavelet dataset
    depths = wavelet_dataset.depths
    data = wavelet_dataset.signals[property_name].values
    scales = wavelet_dataset.scales * \
        wavelet_dataset.wav_properties['equivalent_fourier_period']
    transform = wavelet_dataset.properties[property_name].values.real
    depths_grid, scales_grid = numpy.meshgrid(depths, scales)
    coi = wavelet_dataset.cone_of_influence
    gap = wavelet_dataset.gap_cones

    # Make borehole trace plot
    xlim = int(numpy.min(data)), int(numpy.max(data))
    trace_ax.plot(data, depths, 'k')
    trace_ax.set_ylim(depths[-1], depths[0])
    for subdataset in wavelet_dataset.subdatasets:
        trace_ax.fill_between(xlim, subdataset[0], subdataset[1],
                              color='yellow',
                              alpha=0.2)
    for dgap in wavelet_dataset.gaps:
        trace_ax.fill_between(xlim, dgap[0], dgap[1], color='black', alpha=0.1)
    trace_ax.set_ylabel('Depth')
    trace_ax.set_xticks([xlim[0], 0, xlim[1]])
    trace_ax.set_xticklabels([xlim[0], 0, xlim[1]], rotation='vertical')

    # Make transform plot
    transform_ax.contour(scales_grid.T, depths_grid.T, coi.mask, [1e-6],
                         colors='white')
    transform_ax.contour(scales_grid.T, depths_grid.T, gap.mask, [1 - 1e-6],
                         colors='black',
                         alpha=0.4)
    transform_ax.contourf(scales_grid.T, depths_grid.T, gap, 1,
                          colors='black',
                          alpha=0.1)
    transform_ax.contourf(scales_grid.T, depths_grid.T, transform, 40,
                          cmap=matplotlib.pyplot.get_cmap('RdYlBu_r'))
    transform_ax.contourf(scales_grid.T, depths_grid.T, coi, 1,
                          colors='white',
                          alpha=0.3)
    transform_ax.set_xscale('log')
    transform_ax.set_xlabel(r'Wavelength $\lambda$')
    transform_ax.set_yticklabels('')
    transform_ax.set_ylim(depths[-1], depths[0])
    fig.tight_layout()
    return fig, trace_ax, transform_ax


def wavelet_label_plot(wavelet_dataset, property_name):
    """ Plot a CWT decomposition for a given dataset
    """
    # Set up figure
    fig = matplotlib.pyplot.figure(figsize=(8, 12))
    grid = matplotlib.gridspec.GridSpec(1, 2, width_ratios=[0.1, 1])
    trace_ax = matplotlib.pyplot.subplot(grid[0])
    transform_ax = matplotlib.pyplot.subplot(grid[1])

    # Get info from wavelet dataset
    depths = wavelet_dataset.depths
    data = wavelet_dataset.signals[property_name].values
    scales = wavelet_dataset.scales * \
        wavelet_dataset.wav_properties['equivalent_fourier_period']
    label_array = wavelet_dataset.domains[property_name]
    nlabels = len(wavelet_dataset.labels[property_name])
    depths_grid, scales_grid = numpy.meshgrid(depths, scales)
    coi = wavelet_dataset.cone_of_influence
    gap = wavelet_dataset.gap_cones

    # Make borehole trace plot
    xlim = int(numpy.min(data)), int(numpy.max(data))
    trace_ax.plot(data, depths, 'k')
    trace_ax.set_ylim(depths[-1], depths[0])
    for subdataset in wavelet_dataset.subdatasets:
        trace_ax.fill_between(xlim, subdataset[0], subdataset[1],
                              color='red', alpha=0.2)
    for dgap in wavelet_dataset.gaps:
        trace_ax.fill_between(xlim, dgap[0], dgap[1], color='black', alpha=0.1)
    trace_ax.set_ylabel('Depth')
    trace_ax.set_xticks([xlim[0], 0, xlim[1]])
    trace_ax.set_xticklabels([xlim[0], 0, xlim[1]], rotation='vertical')

    # Make transform plot
    transform_ax.contour(scales_grid.T, depths_grid.T, coi.mask, [1e-6],
                         colors='white')
    transform_ax.contour(scales_grid.T, depths_grid.T, gap.mask, [1 - 1e-6],
                         colors='black', alpha=0.4)
    transform_ax.contourf(scales_grid.T, depths_grid.T, gap, 1,
                          colors='black', alpha=0.1)
    transform_ax.contourf(scales_grid.T, depths_grid.T, label_array,
                          nlabels, cmap=matplotlib.pyplot.get_cmap('RdGy'))
    transform_ax.contourf(scales_grid.T, depths_grid.T, coi, 1,
                          colors='white', alpha=0.3)
    transform_ax.set_xscale('log')
    transform_ax.set_xlabel(r'Wavelength $\lambda$')
    transform_ax.set_yticklabels('')
    transform_ax.set_ylim(depths[-1], depths[0])
    fig.tight_layout()
    return fig, trace_ax, transform_ax


def plot_all_wavelets(wavelet_dataset, properties=None):
    """ Plot all the wavelets in a WaveletDataSet

        :param wavelet_dataset: The wavelet dataset to pull data from
        :type wavelet_dataset: pyboreholes.datasets.WaveletDataSet
        :param properties: A list of property names to plot. Defaults to None
            if not specified, in which case all properties are plotted.
        :type properties: list of strings
        :returns: the current matplotlib.pyplot.Figure instance and a list of
            matplotlib.pyplot.Axes instances corresponding to each wavelet plot
    """
    # Check whether we've specified keys to plot
    all_prop_names = wavelet_dataset.properties.keys()
    if properties is None:
        props_to_plot = all_prop_names
    else:
        props_to_plot = properties

    # Get figure infomation
    props = [wavelet_dataset.properties[prop] for prop in props_to_plot]
    gaps = wavelet_dataset.gap_cones
    coi = wavelet_dataset.cone_of_influence
    nplots = len(props)
    grid = gen_axes_grid(nplots, 5)
    geom = grid.get_geometry()

    # Plot each property
    fig = matplotlib.pyplot.figure(figsize=(11, 7 * geom[1]))
    axes = []
    for idx, prop in enumerate(props):
        axe = matplotlib.pyplot.subplot(grid[idx])
        axes.append(axe)
        axe.set_xticks([])
        axe.set_yticks([])
        axe.contourf(prop.values.real[::-1], 5,
                     cmap=matplotlib.pyplot.get_cmap('RdYlBu_r'))
        axe.contourf(coi[::-1], 1, colors=['white'], alpha=0.5)
        axe.contourf(gaps[::-1], 1, colors=['black'], alpha=0.2)
        axe.set_title(prop.property_type.long_name)
    fig.tight_layout()
    return fig, axes


def plot_all_label_arrays(wavelet_dataset):
    """ Plot all the label arrays in a WaveletDataSet
    """
    # Generate figure
    fig = matplotlib.pyplot.figure(figsize=(11, 20))
    dataset_keys = wavelet_dataset.datasets.keys()
    gaps = wavelet_dataset.gap_cones
    coi = wavelet_dataset.cone_of_influence
    nplots = len(dataset_keys)
    grid = gen_axes_grid(nplots, 5)

    # Plot each property
    for idx, key in enumerate(dataset_keys):
        domains = wavelet_dataset.domains[key].real
        ndomains = len(wavelet_dataset.labels[key])
        axe = matplotlib.pyplot.subplot(grid[idx])
        axe.set_xticks([])
        axe.set_yticks([])
        axe.contourf(datasets[::-1], ndomains,
                     cmap=matplotlib.pyplot.get_cmap('RdGy'))
        axe.contourf(coi[::-1], 1, colors=['white'], alpha=0.5)
        axe.contourf(gaps[::-1], 1, colors=['black'], alpha=0.2)
        axe.set_title(wavelet_dataset.properties[key].property_type.long_name)
    fig.tight_layout()
    return fig, axe


def plot_label_tree(tree):
    """ Plot up a LabelTree instance
    """
    # Plot up boundaries using a linecollection
    fig = matplotlib.pyplot.figure(figsize=(12, 8))
    axe = fig.gca()
    cmap = matplotlib.pyplot.get_cmap('RdGy')
    colors = cmap(numpy.linspace(0, 1, len(tree.labels)))

    # Add connections
    intervals = numpy.asarray(tree.intervals)
    mid_dataset = (intervals[:, 0] + intervals[:, 1]) / 2.
    connect_midpoints = lambda p, c: \
        [[tree.max_scales[0][p], mid_dataset[p]],
         [tree.max_scales[0][c], mid_dataset[c]]]
    for index in range(len(mid_dataset)):
        parent, children = (index, tree.connections[index])
        if parent is 'root':
            continue
        segments = [connect_midpoints(parent, child) for child in children]
        color = colors[parent]
        axe.add_collection(matplotlib.collections.LineCollection(segments,
                           linewidths=(0.5,),
                           linestyle='solid',
                           colors=[color]))
    for label, point in enumerate(zip(tree.max_scales[0], mid_dataset)):
        matplotlib.pyplot.text(point[0], point[1], str(label))

    segments = zip(
        numpy.vstack(numpy.transpose(
            [tree.max_scales[:][0], tree.min_dataset])),
        numpy.vstack(numpy.transpose(
            [tree.max_scales[:][0], tree.max_dataset])))
    axe.add_collection(matplotlib.collections.LineCollection(segments,
                       linewidths=(3,),
                       linestyle='solid',
                       colors=colors))

    # Plot boundaries
    axe.set_ylim(tree.depths[-1], tree.depths[0])
    axe.set_xscale('log')
    axe.set_xlabel(r'Wavelength $\lambda$')
    axe.set_ylabel(r'Depth')
    axe.set_xlim(numpy.min(tree.max_scales), numpy.max(tree.max_scales))


def plot_time_dataset(dataset):
    """ Generate a timeseries plot of what's going in a given TimeDataSet
        instance
    """
    nplots = 3
    fig = matplotlib.pyplot.figure(figsize=(11, 2.5 * nplots))
    gspec = matplotlib.pyplot.GridSpec(
        nplots, 1,
        height_ratios=([1] + (nplots - 1) * [0.3]))
    axes_list = []

    # Get some data from the TimeDataSet
    times = dataset.times

    # Bit depth plot
    axes = matplotlib.pyplot.subplot(gspec[0])

    # Plot ROP=0 zones as they are advected through the system
    for bstart, bend in dataset.break_intervals:
        # Generate traces for the start and end fluid samples
        bstart_trace = dataset.sample_trace(
            initial_time=bstart, initial_depth=dataset.bit_depth(bstart))(times)
        bend_trace = dataset.sample_trace(
            initial_time=bend, initial_depth=dataset.bit_depth(bstart))(times)
        bend_trace[times < bstart] = numpy.nan
        bstart_trace[times < bstart] = numpy.nan

        # Shade between the traces in gray
        axes.fill_between(times, bend_trace, bstart_trace,
                          color='gray', alpha=0.5)

        # Plot the traces without the extensions
        axes.plot(times, bstart_trace, color='gray', linewidth=2, alpha=0.8)
        axes.plot(times, bend_trace, color='gray', linewidth=2, alpha=0.8)
    axes.plot(times, dataset.bit_depth(times),
              color='black',
              marker=None,
              linewidth=2,
              alpha=0.7,
              label='bit depth')
    axes.set_xticklabels('')
    axes.set_ylabel('Depth (m)')
    axes.set_xlim(times[0], times[-1])
    axes.set_ylim(dataset.bit_depth(times[-1]), 0)
    axes_list.append(axes)

    # ROP plot
    axes = matplotlib.pyplot.subplot(gspec[1])
    axes.plot(times, dataset.rop(times),
              color='black',
              marker=None,
              linewidth=2,
              alpha=0.7)
    axes.set_ylabel('ROP (m / min)')
    axes.set_xlim(times[0], times[-1])
    axes.set_ylim(-0.01, None)
    axes_list.append(axes)

    # Flow rate plot
    axes = matplotlib.pyplot.subplot(gspec[2])
    axes.plot(times, dataset.flow_rate(times),
              color='black',
              marker=None,
              linewidth=2,
              alpha=0.7)
    axes.set_ylabel('Flow rate (cu. m / min)')
    axes.set_xlim(times[0], times[-1])
    axes.set_ylim(-0.01, None)
    axes.set_xlabel('Time (min)')
    axes_list.append(axes)

    fig.tight_layout()
    return fig, axes_list
