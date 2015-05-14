""" file:   geology.py
    author: Jess Robertson
            CSIRO Earth Science and Resource Engineering
    date:   Monday March 17, 2014

    description: Implementation of spectrum samplers to simulate measurements
        based on Poisson arrival processes.
"""

from __future__ import print_function, division

from pysiss import borehole

import numpy
import scipy.stats


def clr(xs, axis=0):
    """ Returns the centered log ratio of the given composition vector xs
    """
    xs = numpy.asarray(xs)
    geometric_mean = numpy.product(xs, axis=axis) ** (1. / float(xs.shape[axis]))
    return numpy.log(xs / geometric_mean)


def invclr(cs, axis=0):
    """ Returns the inverse centered log ratio for the given CLR transformed vector cs
    """
    cs = numpy.asarray(cs)
    ratio = numpy.exp(cs)
    return ratio / ratio.sum(axis=axis)


class RockType():

    """ A synthetic rock generator
    """

    def __init__(self, composition, noise=0.1):
        self.composition = numpy.asarray(composition)
        self.noise = noise

        # Generate normalised composition and clr transformed version
        self.composition /= self.composition.sum()
        self.clr_composition = clr(self.composition)

        # Make generators for random data
        self.generators = [scipy.stats.norm(c, noise)
                           for c in self.clr_composition]

    def sample(self, nsamples=1):
        """ Generate a set of measurements from this rock type
        """
        return invclr([g.rvs(size=nsamples) for g in self.generators])


def synthetic_borehole():
    """ Make a synthetic borehole with three compositional values and some gaps
    """
    # Make some synthetic rock types
    rock_types = [
        RockType([0.2, 0.3, 0.5], noise=0.3),
        RockType([0.6, 0.1, 0.3], noise=0.3),
        RockType([0.1, 0.7, 0.3], noise=0.8),
        RockType([0.01, 0.05, 0.95], noise=1)
    ]
    component_labels = ['foo', 'bar', 'baz']

    # Make a synthetic rock column
    # Specify our rock column labels using a list of (nsamples, rocktype) tuples
    rock_column_spec = [
        (10, 0),
        (50,  2),
        (5,   3),
        (11,  2),
        (5,   3),
        (9,   2),
        (50,  1),
        (26,  3),
        (37,  0),
        (89,  2),
        (52,  1),
        (10,  0),
        (19,  0),
        (25,  2),
        (5,   3),
        (11,  2),
        (5,   3),
        (9,   2),
        (10,  1)]
    rock_column_samples = numpy.hstack([rock_types[i].sample(n)
                                        for n, i in rock_column_spec])

    # Generate some random depths with some gaps
    depth_differences = \
        abs(numpy.random.normal(scale=3,
                                size=rock_column_samples.shape[1] + 1))
    depth_differences[100] = 50
    depth_differences[197] = 24
    depths = numpy.cumsum(depth_differences)
    from_depths = depths[:-1]
    to_depths = numpy.minimum(depths[:-1] + 10, depths[1:])
    import ipdb; ipdb.set_trace()

    # Wrap it up into a borehole object
    bh = borehole.Borehole()
    dataset = bh.add_interval_dataset('geochemistry', from_depths, to_depths)
    for ident, values in zip(component_labels, rock_column_samples):
        dataset.add_property(ident=ident, 
                             values=values,
                             status='synthetic')
    return bh
