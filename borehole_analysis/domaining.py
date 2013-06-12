#!/usr/bin/env python
""" file:   domaining.py (borehole_analysis)
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

def tree_reduce(connections, root, function, compare):
    """ Reduce a tree to a single value using a function and a comparison.

        Walks over the tree structure, applying the function to each node. 
        Then applies the comparison, returning the larger value relative to 
        the ordering supplied. 
    """
    # Calculate function on own values
    result = function(root)
    
    # Recursively compare on children
    for child in connections[root]:
        if child in connections.keys():
            # Child has own children, call recursively
            child_value = tree_reduce(connections, child, function, compare)
        else:
            # Child is a leaf node
            child_value = function(child)
        if compare(result, child_value):
            result = child_value
    return result

class WaveletLabeller(object):
    
    """ Class to label wavelet transforms by region
    """
    
    def __init__(self, node, key, wavelet_properties=None, 
        sort_regions_by_size=False):
        self.node = node
        self.domain = node.get_domain()
        
        # Generate wavelet transform from node data
        properties = cwavelets.WaveletProperties(order=1)
        if wavelet_properties is not None:
            properties.update(wavelet_properties)
        self.wavelet = cwavelets.Hermitian(
            signal=self.node.get_signal(key)[key], 
            domain=self.domain,
            properties=properties)
        
        # Make references
        self.labelled_array, self.labels = None, None
        self.min_domain, self.max_domain, self.max_scales = None, None, None
        self.connections = None
        
        # Generate wavelet transform data
        self.__label_regions()
        if sort_regions_by_size:
            self.__sort_by_size()
        self.__generate_enclosures()
    
    def __label_regions(self):
        """ Split a wavelet transform into regions based on sign
        """
        # Generate thresholded masks
        array = self.wavelet.get_transform().real
        pos, neg = numpy.zeros_like(array), numpy.zeros_like(array)
        pos[array >= 0] = 1
        neg[array < 0] = 1
       
        # Generate & combine labels
        pos_labs, npos_labs = scipy.ndimage.label(pos)
        neg_labs, nneg_labs = scipy.ndimage.label(neg)
        self.labelled_array = (neg * (neg_labs - 1) \
            + pos * (pos_labs + nneg_labs - 1)).astype(int)
        self.labels = numpy.arange(nneg_labs + npos_labs, dtype=numpy.int)

    def __generate_enclosures(self):
        """ Generate enclosure relationships
        """
        # Check that we have already labelled arrays
        if self.labelled_array is None:
            self.__label_regions()
        
        # Get labels, then use measurements.maximum with a list of scales to 
        #generate the maximum scales per domain
        scales = self.wavelet.get_scales(fourier=True)
        scale_array = numpy.tile(scales, (self.labelled_array.shape[1], 1)).T
        maxima = numpy.asarray(maximum_position(scale_array, 
                labels=self.labelled_array, 
                index=self.labels),
            dtype=numpy.int)
        self.max_scales = numpy.asarray(
            [scales[maxima.T[0]], self.domain[maxima.T[1]]])
        
        # Get the bounds on each domain in the domain space
        min_index = numpy.asarray(minimum_position(self.domain, 
            labels=self.labelled_array[0], 
            index=self.labels), dtype=numpy.int).T
        max_index = numpy.asarray(maximum_position(self.domain, 
            labels=self.labelled_array[0], 
            index=self.labels), dtype=numpy.int).T
        self.min_domain = self.domain[min_index][0]
        self.max_domain = self.domain[max_index][0]
        
        # Build a tree of parent-child relationships. We use a dict for rapid 
        # lookup from base to root
        self.connections = defaultdict(list)
        for maxm in maxima:
            try:
                # If we have a parent, add this 
                parent = self.labelled_array[maxm[0]+1, maxm[1]]
                self.connections[parent].append(
                    self.labelled_array[maxm[0], maxm[1]])
            except IndexError:
                # We have a root domain so there is no parent (i.e. no pixel 
                # at next largest scale)
                self.connections['root'].append(
                    self.labelled_array[maxm[0], maxm[1]])
        
        # Use tree to find bounding locations for a given domain
        for label in self.labels:
            self.min_domain[label] = tree_reduce(self.connections, label, 
                function=lambda n: self.min_domain[n], 
                compare=lambda a, b: a > b)
            self.max_domain[label] = tree_reduce(self.connections, label, 
                function=lambda n: self.max_domain[n], 
                compare=lambda a, b: a < b)
    
    def __sort_by_size(self):
        """ Sort labels by region size
        """
        # Check that we have already labelled arrays
        if self.labelled_array is None:
            self.__label_regions()
            
        # We'll use tallies to add up how big a region is
        nscales = len(self.wavelet.get_scales())
        label_tallies = numpy.zeros_like(self.labels, dtype=numpy.int)
        for i in range(nscales):
            vals = numpy.unique(self.labelled_array[i])
            label_tallies[vals] += 1

        # Sort by size - larger labels show up in more decomps
        # We use negative integers in loop to avoid clobbering labels we 
        # haven't used yet
        sort_idx = numpy.argsort(label_tallies)[::-1]
        for i, j in enumerate(self.labels[sort_idx]):
            self.labelled_array[self.labelled_array == j] = -(i+1)
           
        # Undo the negative, reset first label to zero
        self.labelled_array *= -1
        self.labelled_array -= 1


