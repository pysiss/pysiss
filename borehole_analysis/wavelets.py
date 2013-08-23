#!/usr/bin/env python
""" file:   wavelets.py (borehole_analysis)
    author: Jess Robertson
            CSIRO Earth Science and Resource Engineering
    email:  jesse.robertson@csiro.au
    date:   Wednesday May 1, 2013

    description: Domaining module of the borehole_analysis module.
"""

import numpy
import cwavelets
import scipy.ndimage
from collections import defaultdict
from scipy.ndimage.measurements import maximum_position, minimum_position
from borehole_analysis.domains import SamplingDomain, PropertyType

class WaveletDomain(SamplingDomain):

    """ Domain class to store continuous wavelet transform data.

        Arguments:
            wavelet - a `cwavelets.CWTransform` subclass
            domain - a `borehole_analysis.SamplingDomain` instance which contains
    """

    def __init__(self, name, sampling_domain, wavelet=None,
        wav_properties=None):
        super(WaveletDomain, self).__init__(name, sampling_domain.depths)
        self.sampling_domain = sampling_domain
        self.wavelet_type = wavelet or cwavelets.Hermitian
        self.wav_properties = cwavelets.WaveletProperties()
        if wav_properties is not None:
            self.wav_properties.update(wav_properties)
        self._dummy_wav = self.wavelet_type(
            signal=numpy.ones_like(self.depths),
            domain=self.depths,
            properties=self.wav_properties)
        self.scales = self._dummy_wav.get_scales(fourier=False)
        tau_e = self._dummy_wav.properties['efolding_time']

        # Check that we have identified gaps in the domain
        if sampling_domain.gaps is None:
            raise AttributeError("You need to identify gaps in your domain "
                "first - try calling the split_at_gaps method")
        else:
            self.gaps = sampling_domain.gaps
            self.subdomains = sampling_domain.subdomains

        # Calculate COI and gap regions
        depths_grid, scales_grid = numpy.meshgrid(self.depths, self.scales)

        # Define gap masks
        self.gap_mask = numpy.zeros(depths_grid.shape, dtype=bool)
        for gap in self.gaps:
            self.gap_mask = numpy.logical_or(
                self.gap_mask,
                numpy.logical_and(
                    (depths_grid - gap[0]) / (scales_grid * tau_e) >= 1,
                    (gap[1] - depths_grid) / (scales_grid * tau_e) >= 1))
        self.gap_cones = numpy.ma.masked_array(
            numpy.ones_like(depths_grid),
            mask=numpy.logical_not(self.gap_mask)).transpose()

        # Define COI masks
        coi_mask = numpy.zeros(depths_grid.shape, dtype=bool)
        for sub in self.subdomains:
            coi_mask = numpy.logical_or(
                coi_mask,
                numpy.logical_not(numpy.logical_or(
                    (depths_grid - sub[0]) / (scales_grid * tau_e) < 1,
                    (sub[1] - depths_grid) / (scales_grid * tau_e) < 1)))
        self.cone_of_influence = numpy.ma.masked_array(
            numpy.ones_like(depths_grid),
            mask=coi_mask).transpose()

        # Placeholders for other datasets
        self.wavelets = {}
        self.labels = {}

    def add_transform(self, prop):
        """ Add transforms to domain from a given sampling_domain instance
        """
        assert len(prop.values) == len(self.depths), \
            "Length of WaveletDomain and SamplingDomain must be the same"
        wav = self.wavelets[prop.name] = self.wavelet_type(
            signal=prop.values,
            domain=self.depths,
            properties=self.wav_properties)
        masked_transform = numpy.ma.masked_array(
            wav.get_transform(),
            mask=self.gap_mask)
        self.add_property(prop.property_type,
            masked_transform.transpose())

    def label_domains(self, property_name, sort_by_size=False):
        """ Label domains within a CWT
        """
        # Generate thresholded masks
        transform = self.properties[property_name].values.real
        pos = numpy.zeros_like(transform)
        neg = numpy.zeros_like(transform)
        pos[transform >= 0] = 1
        neg[transform < 0] = 1

        # Generate & combine labels
        pos_labs, npos_labs = scipy.ndimage.label(pos)
        neg_labs, nneg_labs = scipy.ndimage.label(neg)
        labelled_array = (pos * pos_labs \
            - neg * (neg_labs - 1) + nneg_labs - 1).astype(int)
        labels = self.labels[property_name] = \
            numpy.arange(nneg_labs + npos_labs, dtype=numpy.int)

        if sort_by_size:
            # We'll use tallies to add up how big a region is
            nscales = len(self.wavelets[property_name].get_scales())
            label_tallies = numpy.zeros_like(labels, dtype=numpy.int)
            for i in range(nscales):
                vals = numpy.unique(labelled_array[i])
                label_tallies[vals] += 1

            # Sort by size - larger labels show up in more decomps
            # We use negative integers in loop to avoid clobbering labels we
            # haven't used yet
            sort_idx = numpy.argsort(label_tallies)[::-1]
            for i, j in enumerate(labels[sort_idx]):
                labelled_array[labelled_array == j] = -(i+1)

            # Undo the negative, reset first label to zero
            labelled_array *= -1
            labelled_array -= 1

        ptype = self.properties[property_name].property_type
        labelled_array = \
            numpy.ma.masked_array(labelled_array, mask=self.gap_mask.T)
        self.add_property(
            PropertyType(name=ptype.name + ' domains',
                long_name=ptype.long_name + ' domains', units=None),
            labelled_array)
        return labelled_array, labels


class LabelTree(object):

    """ Tree class which generates label enclosures and intervals from a
        labelled array.
    """

    def __init__(self, depths, scales, labelled_array, labels):
        super(LabelTree, self).__init__()
        self.scales = scales
        self.depths = depths
        self.labelled_array = labelled_array
        self.labels = labels
        self.intervals = None

        # Get labels, then use measurements.maximum with a list of scales to
        # generate the maximum scales per domain
        scale_array = numpy.tile(self.scales,
            (self.labelled_array.shape[0], 1))
        maxima = numpy.asarray(maximum_position(scale_array,
                labels=self.labelled_array,
                index=self.labels),
            dtype=numpy.int)
        minima = numpy.asarray(minimum_position(scale_array,
                labels=self.labelled_array,
                index=self.labels),
            dtype=numpy.int)
        self.max_scales = numpy.asarray(
            [self.scales[maxima[:, 1]], self.depths[maxima[:, 0]]])
        self.min_scales = numpy.asarray(
            [self.scales[minima[:, 1]], self.depths[minima[:, 0]]])

        # Get the bounds on each domain in the domain space
        min_index = numpy.asarray(minimum_position(self.depths,
            labels=self.labelled_array[:, 0],
            index=self.labels), dtype=numpy.int).T
        max_index = numpy.asarray(maximum_position(self.depths,
            labels=self.labelled_array[:, 0],
            index=self.labels), dtype=numpy.int).T
        self.min_domain = self.depths[min_index][0]
        self.max_domain = self.depths[max_index][0]

        # Build a tree of parent-child relationships. We use a dict for rapid
        # lookup from base to root
        self.connections = defaultdict(list)
        for maxm in maxima:
            try:
                # If we have a parent, add this
                parent = self.labelled_array[maxm[0], maxm[1]+1]
                current = self.labelled_array[maxm[0], maxm[1]]
                if current is not numpy.ma.masked:
                    # We need to make sure that we're not including masked
                    # values. This is because the ndimage measurements include
                    # masked regions as labels!!
                    self.connections[parent].append(current)
            except IndexError:
                # We have a root domain so there is no parent (i.e. no pixel
                # at next largest scale)
                self.connections['root'].append(
                    self.labelled_array[maxm[0], maxm[1]])

        # Use tree to find bounding locations for a given domain
        self.intervals = [None] * len(self.labels)
        for label in self.labels:
            mindom = self.min_domain[label] = self.reduce(label,
                function=lambda n: self.min_domain[n],
                compare=lambda a, b: a > b)
            maxdom = self.max_domain[label] = self.reduce(label,
                function=lambda n: self.max_domain[n],
                compare=lambda a, b: a < b)
            self.intervals[label] = (mindom, maxdom)
        self.intervals = numpy.asarray(self.intervals)

        # Calculate layer thicknesses
        spacing = self.depths[1] - self.depths[0]
        self.thicknesses = numpy.maximum(spacing,
            self.intervals[:, 1] - self.intervals[:, 0])

    def reduce(self, root, function, compare):
        """ Reduce a tree to a single value using a function and a comparison.

            Walks over the tree structure, applying the function to each node.
            Then applies the comparison, returning the larger value relative to
            the ordering supplied.
        """
        # Calculate function on own values
        result = function(root)

        # Recursively compare on children
        for child in self.connections[root]:
            if child in self.connections.keys():
                # Child has own children, call recursively
                child_value = self.reduce(child, function, compare)
            else:
                # Child is a leaf node
                child_value = function(child)
            if compare(result, child_value):
                result = child_value
        return result