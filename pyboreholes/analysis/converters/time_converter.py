""" file:   time_converter.py (pyboreholes.analysis.time_conversion)
    author: Jess Robertson
            CSIRO Earth Science and Resource Engineering
    email:  jesse.robertson@csiro.au
    date:   Wednesday May 1, 2013

    description: Initialisation of the pyboreholes.analysis.time_conversion
        module.
"""

from ...datasets import TimeDataSet, TimeIntervalDataSet, PointDataSet, \
    IntervalDataSet
from ...utilities import integrate
import numpy
from scipy.interpolate import InterpolatedUnivariateSpline as Spline
from scipy.optimize import brentq as brent

## Todo: this needs to go somewhere else I think
HOLE_GEOMETRY = {
    'AQ': dict(outer_diameter=44.5e-3,
               inner_diameter=34.9e-3,
               hole_diameter=48.0e-3),
    'NQ': dict(outer_diameter=69.9e-3,
               inner_diameter=60.3e-3,
               hole_diameter=75.7e-3),
    'HQ': dict(outer_diameter=88.9e-3,
               inner_diameter=77.8e-3,
               hole_diameter=96.0e-3),
    'PQ': dict(outer_diameter=114.3e-3,
               inner_diameter=101.6e-3,
               hole_diameter=122.6e-3)
}


class TimeConverter(object):

    """ Converts timestamped data into depthstamped data
    """

    def __init__(self, borehole):
        super(TimeConverter, self).__init__()

        # Check that we can access the relevant data from the borehole
        self.borehole = borehole
        self.details = borehole.details
        try:
            flow_rate_times, flow_rate = \
                map(numpy.asarray,
                    self.details['flow_rate'].values)
            rop_times, rop = \
                map(numpy.asarray,
                    self.details['rate_of_penetration'].values)
            break_intervals = numpy.asarray(self.details['break_intervals'])
        except KeyError:
            raise ValueError(
                'Cannot generate a TimeConverter for a borehole '
                'unless it has data for "flow_rate", "rate_of_penetration" '
                'and "break_intervals" in the details attribute.')

        # Calculate borehole flow area
        try:
            geom = HOLE_GEOMETRY[self.details['borehole_type'].values]
            flow_area = numpy.pi * (geom['hole_diameter'] ** 2
                                    - geom['outer_diameter'] ** 2)
        except KeyError:
            raise ValueError(
                'Borehole type needs to be specified in the'
                'details attribute of borehole. Allowed values are '
                'borehole_type=<{0}>.'.format(HOLE_GEOMETRY.keys()))

        # Generate bounds on the time we can convert over
        self.time_bounds = (min(flow_rate_times[0], rop_times[0]),
                            max(flow_rate_times[-1], rop_times[-1]))
        break_data = numpy.sort(self.details['break_intervals'].values, axis=0)
        break_intervals = TimeIntervalDataSet('break_intervals',
                                             from_times=break_data[:, 0],
                                             to_times=break_data[:, 1])
        self.borehole.add_dataset(break_intervals)

        # Generate driving spline fits
        self.flow_rate = Spline(flow_rate_times, flow_rate, k=1)
        self.rop = Spline(rop_times, rop, k=1)
        self.details.add_detail('bit_depth', integrate(rop_times, rop), None)
        self.bit_depth = Spline(
            rop_times, self.details['bit_depth'].values, k=1)
        self.distance = Spline(
            flow_rate_times,
            integrate(flow_rate_times, flow_rate) / flow_area, k=1)

    def get_advection_trace(self, initial_time, initial_depth):
        """ Return the advection trace from the given sample starting
            depth h and time t.

            Note that this doesn't take into account whether the sample
            has been drilled or not. If you want to get a full trace for
            a given sample use `TimeDataSet.sample_trace`.
        """
        return lambda t: \
            self.distance(initial_time) + initial_depth - self.distance(t)

    def sample_trace(self, initial_time, initial_depth):
        """ Return the sample trace of a sample starting at depth h and time t

            If the initial depth/time position is such that the sample hasn't
            been drilled yet, then the trace is projected through until the
            sample is drilled, and then advected up the hole. If the sample
            is already drilled then we need to project back to the time that
            it was drilled.

            Both the time and depth have to be stated because of the fact that
            the bit may not be moving, so there are multiple samples which
            can come from the same depth but at different times.
        """
        # Determine when the drill bit reaches the sample and at what depth
        if initial_depth > self.bit_depth(initial_time):
            # This sample hasn't been drilled yet, we need to project
            # forwards through time to find when it will be first drilled
            time_at_drill = brent(
                lambda t: self.bit_depth(t) - initial_depth,
                *self.time_bounds)
            drill_depth = initial_depth

        else:
            # This sample has already been drilled but needs to be projected
            # both back and forwards to determine the sample trace
            advection = self.get_advection_trace(initial_time, initial_depth)
            time_at_drill = brent(lambda t: self.bit_depth(t) - advection(t),
                                  *self.time_bounds)
            drill_depth = self.bit_depth(time_at_drill)

        # Generate a trace based on the time & depth that the sample
        # was drilled at
        advection = self.get_advection_trace(time_at_drill, drill_depth)
        trace = lambda time: \
            numpy.maximum(0, numpy.minimum(drill_depth, advection(time)))

        return trace

    def arrival_times_from_depths(self, depths):
        """ Calculate the arrival times for samples from a given depth.

            If there isn't enough flow rate data to fully calculate the
            arrival time of a given sample, then the arrival_time will
            be set to `numpy.nan`.
        """
        arrival_times = numpy.empty_like(depths)
        for idx, depth in enumerate(depths):
            # Work out when the given depth gets drilled
            time_at_drill = brent(
                lambda t: self.bit_depth(t) - depth,
                *self.time_bounds)

            # Work out when the advected sample reaches the surface
            advection = self.get_advection_trace(time_at_drill, depth)
            try:
                arrival_times[idx] = brent(advection, *self.time_bounds)
            except ValueError:
                # We don't have enough flow rate data to calculate arrival time
                arrival_times[idx] = numpy.nan

        return arrival_times

    def depths_from_arrival_times(self, arrival_times):
        """ Calculate the arrival times for samples from a given depth.

            If there isn't enough flow rate data to fully calculate the
            arrival time of a given sample, or the given arrival time is
            within a break period for drilling, then the arrival_time will
            be set to `numpy.nan`.
        """
        depths = numpy.empty_like(arrival_times)
        for idx, arrival_time in enumerate(arrival_times):
            if self.arrival_time_in_break_period(arrival_time):
                depths[idx] = numpy.nan
            else:
                advection = self.get_advection_trace(arrival_time, 0)
                time_at_drill = brent(
                    lambda t: self.bit_depth(t) - advection(t),
                    *self.time_bounds)
                depths[idx] = self.bit_depth(time_at_drill)
        return depths

    def _calculate_break_arrival_times(self):
        """ Calculate when the breaks arrive at the surface
        """
        arrival_times = numpy.empty_like(self.break_intervals)

        # Loop through, determine drilling depth and advect to surface
        for iidx, interval in enumerate(self.break_intervals):
            start, end = interval
            break_depth = self.bit_depth(interval[0])
            for jidx, time in enumerate(interval):
                advection = self.get_advection_trace(time, break_depth)
                try:
                    arrival_times[iidx, jidx] = brent(advection,
                                                      *self.time_bounds)
                except ValueError:
                    # We don't have enough flow rate data to calculate an
                    # arrival time
                    arrival_times[iidx, jidx] = numpy.nan

        return arrival_times

    def arrival_time_in_break_period(self, arrival_time):
        """ Returns whether a sample arrival_time is within a break arrival
            time interval
        """
        intervals = self.break_arrival_intervals
        in_interval = lambda a, b, x: x >= a and x <= b
        return any(map(lambda i: in_interval(*i, x=arrival_time), intervals))
