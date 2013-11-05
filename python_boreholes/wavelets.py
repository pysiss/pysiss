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
from borehole_analysis.domains import SamplingDomain
import borehole_analysis.metrics as metrics
from itertools import product, repeat

__all__ = ['WaveletDomain', 'LabelTree', 'metrics']

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
            domain_axes=[self.depths],
            properties=self.wav_properties)
        self._dummy_wav.generate_domains()
        self.scales = self._dummy_wav.scales
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
        self.domains = {}
        self.labels = {}
        self.label_trees = {}
        self.label_weights = {}

    def add_transform(self, prop):
        """ Add transforms to domain from a given sampling_domain instance
        """
        assert len(prop.values) == len(self.depths), \
            "Length of WaveletDomain and SamplingDomain must be the same"
        wav = self.wavelets[prop.name] = self.wavelet_type(
            signal=prop.values,
            domain_axes=[self.depths],
            properties=self.wav_properties)
        wav.calculate_transform()
        masked_transform = numpy.ma.masked_array(
            wav.transform,
            mask=self.gap_mask)
        self.add_property(prop.property_type,
            masked_transform.transpose())

    def label_domains(self, property_name):
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
        labelled_array = (pos * pos_labs
            - neg * (neg_labs - 1) + nneg_labs - 1).astype(int)
        self.labels[property_name] = \
            numpy.arange(nneg_labs + npos_labs, dtype=numpy.int)
        labelled_array = \
            numpy.ma.masked_array(labelled_array, mask=self.gap_mask.T)

        # Add labelled array to properties
        self.domains[property_name] = labelled_array

        # Generate a LabelTree instance to order labels in scale space
        if len(self.labels[property_name]) is not 0:
            self.label_trees[property_name] = LabelTree(self, property_name)

    def rank_labels(self, property_name, sort_by=metrics.thickness):
        """ Relabel domains so that labels are sorted by some metric
        """
        # Determine importance order
        weights = sort_by(self, property_name)
        sort_idx = numpy.argsort(-weights)
        self.label_weights[property_name] = weights[sort_idx]
        labels = self.labels[property_name]
        mapping = dict(zip(sort_idx, labels))

        # Update label array
        labelled_array = self.domains[property_name]
        sorted_labels = numpy.empty(labelled_array.shape, dtype=int)
        for old_label, new_label in mapping.items():
            sorted_labels[labelled_array == old_label] = new_label
        self.domains[property_name] = \
            numpy.ma.masked_array(sorted_labels, mask=self.gap_mask.T)

        # Update LabelTree attributes
        self.label_trees[property_name].update_labels(sort_idx)


class LabelTree(object):

    """ Tree class which generates label enclosures and intervals from a
        labelled array.
    """

    def __init__(self, wavelet_domain, property_name):
        super(LabelTree, self).__init__()
        self.wavelet_domain = wavelet_domain
        self.property_name = property_name
        self.scales = self.wavelet_domain.scales
        self.depths = self.wavelet_domain.depths
        self.labelled_array = \
            self.wavelet_domain.domains[property_name][:, 0, :]
        self.labels = self.wavelet_domain.labels[self.property_name]
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

    def update_labels(self, sort_idx):
        """ Update the labels in the tree after a resort
        """
        # Update label array
        self.labelled_array = \
            self.wavelet_domain.domains[self.property_name][:, 0, :]

        # Sort label properties
        to_sort = ['thicknesses', 'min_domain', 'max_domain', 'intervals']
        for attr in to_sort:
            self.__dict__[attr] = self.__dict__[attr][sort_idx]
        to_sort_pairs = ['max_scales', 'min_scales']
        for attr in to_sort_pairs:
            self.__dict__[attr] = self.__dict__[attr][:, sort_idx]

        # Update connection tree with new labels
        new_connections = {}
        mapping = dict(zip(sort_idx, self.labels))
        mapping['root'] = 'root'
        for parent, children in self.connections.items():
            new_connections[mapping[parent]] = \
                [mapping[c] for c in children]
        self.connections = new_connections

def get_matches(*wav_domains):
    """ Return the matches between different subdomains withing the given
        wavelet domain.

        All wavelet domains must be pre-labelled.
    """
    # We need the superset of all properties in the wavelet domains
    property_names = list()
    wavelet = dict()
    for domain in wav_domains:
        props = domain.properties.keys()
        property_names.extend(props)
        wavelet.update(zip(props, repeat(domain)))

    # Set up data structures
    all_matches = dict()
    for name in property_names:
        nlabels = len(wavelet[name].labels[name])
        all_matches[name] = []
        for _ in range(nlabels):
            all_matches[name].append(dict(zip(property_names, repeat(None))))
            all_matches[name][-1]['nmatches'] = 0 # Init counter for matches
    domain_metrics = dict()

    # For each label, pull statistics from tree: (lmax, dmax, dmin)
    for name in property_names:
        tree = wavelet[name].label_trees[name]
        domain_metrics[name] = numpy.vstack([tree.max_scales[0],
            tree.max_domain, tree.min_domain]).transpose()

    # Determine cross-domain metrics, select best matches
    already_checked = []
    for name1, name2 in product(property_names, property_names):
        # Check that we actually need to do the work
        if name1 == name2 or (name1, name2) in already_checked:
            continue
        else:
            # Append this one to avoid doing work in future (we only need to
            # each pair once since the results are symmetric)
            already_checked.append((name2, name1))

        # Work out cross-correlation between domains
        metric1 = domain_metrics[name1]
        metric2 = domain_metrics[name2]
        metric_cross = numpy.sum(
            2 * numpy.abs(metric1 - metric2[:, numpy.newaxis])
                / (metric1 + metric2[:, numpy.newaxis]),
            axis=-1)

        # Determine matches as local minima - we only keep matches which are
        # the minimum in both row and column
        best_matches_row = set(zip(
            numpy.arange(metric_cross.shape[1]),
            numpy.argmin(metric_cross, axis=0)))
        best_matches_col = set(zip(
            numpy.argmin(metric_cross, axis=1),
            numpy.arange(metric_cross.shape[0])))
        agreeing_matches = [m for m in best_matches_row
            if m in best_matches_col]

        # For each match, add the relevant matching domain in the matches list
        # of dicts
        for match_dom1, match_dom2 in agreeing_matches:
            all_matches[name1][match_dom1][name2] = match_dom2
            all_matches[name1][match_dom1]['nmatches'] += 1
            all_matches[name2][match_dom2][name1] = match_dom1
            all_matches[name2][match_dom2]['nmatches'] += 1

    return all_matches