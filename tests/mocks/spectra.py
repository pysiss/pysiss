""" file:   spectra.py
    author: Jess Robertson
            CSIRO Earth Science and Resource Engineering
    date:   Monday March 17, 2014

    description: Implementation of spectrum samplers to simulate measurements
        based on Poisson arrival processes.
"""

from __future__ import print_function, division

import numpy
import scipy.interpolate


class Spectrum(object):

    """ Spectrum class

        :param name: an identifier string
        :type name: string
        :param values: a vector of spectrum values
        :type values: iterable of numerical values
        :param wavelengths: a vector of wavelengths for the spectrum values
        :type wavelengths: an ordered iterable of numerical values
        :param wavelet_type: a pywavelets wavelet type specifier
        :type wavelet_type: string
    """

    def __init__(self, name, values, wavelengths=None, wavelet_type='db6'):
        # Slurp in data
        self.name = name
        self.values = numpy.asarray(values)
        self.wavelet_type = wavelet_type
        if wavelengths is not None:
            self.wavelengths = numpy.asarray(wavelengths)
        else:
            self.wavelengths = numpy.arange(len(self.values))
        self.domain = self.wavelengths[0], self.wavelengths[-1]

    def __len__(self):
        """ Return the length of the spectrum array
        """
        return len(self.values)

    def __add__(self, other):
        """ Add spectra
        """
        return self.values + other.values

    def __sub__(self, other):
        """ Subtract spectra
        """
        return self.values - other.values


class SynthSpectrum(Spectrum):

    """ A noisy spectrum generator
    """

    def __init__(self, spectrum):
        # Initialise class using supplied spectrum values
        super(SynthSpectrum, self).__init__(
            name=spectrum.name + ' synthetic',
            values=spectrum.values,
            wavelengths=spectrum.wavelengths)

        # Initialise underlying spectrum
        self.model = self.values.copy()

        # We need to make sure that our spectrum values are >= 0
        self.model[self.model < 0] = 0

        # Generate random processes conditioned on spectrum
        self.rates = self.model / max(self.model)

    def __call__(self, count_time=1):
        """ Return samples from the Poisson processes

            Also updates the values and dwtransform attributes with the newest
            realisation of the random processes, so you can access the wavelet
            transform easily.
        """
        # Calculate new realisation for values
        rvs = numpy.random.poisson(
            lam=self.rates,
            size=(count_time, len(self.rates))
        )
        self.values = rvs.sum(axis=0)

        # Return values
        return self.values


# Add some random peaks around the place
def add_peak(spectrum, loc, amplitude, width):
    """ Add a Gaussian shaped peak with the given amplitude and width
    """
    # Get parameters from spectrum
    wavelengths = spectrum.wavelengths
    values = spectrum.values

    # Calculate the peak shape using the norm PDF
    peak = amplitude * numpy.asarray(
        [numpy.exp(x) for x in (-(wavelengths - loc) ** 2) / (2. * width)])
    spectrum.values = values + peak


# Make a combined spectrum as well
def mixture(spectra, weights):
    """ Makes a combined spectrum from the clean spectrum and the
        bogus spectrum according to the given weights.

        The weights must sum to unity
    """
    # Ensure that weights normalise to unity
    weights = numpy.asarray(weights)
    weights /= sum(weights)

    # Check that all spectra have the same wavelengths available
    wavelengths = numpy.asarray(spectra[0].wavelengths)
    values = numpy.zeros_like(spectra[0].values)
    for weight, spectrum in zip(weights, spectra):
        spline = scipy.interpolate.InterpolatedUnivariateSpline(
            spectra.wavelengths, spectra.values)
        values += weight * spline(wavelengths)

    values = sum([w * spec.values for w, spec in zip(weights, spectra)])
    name = sum(['{0}: {1}'.format(w, s.name)
                for w, s in zip(weights, spectra)])
    return Spectrum(
        name='mixture ({0})'.format(name),
        wavelengths=wavelengths,
        values=values)


def make_bogospectra():
    """ Make some made up spectra data
    """
    wavelengths = numpy.linspace(1, 30, 100)
    background = numpy.sin(wavelengths / 5.) / wavelengths + 0.05
    bogo = Spectrum(
        name='bogonium',
        wavelengths=wavelengths,
        values=background)
    foo = Spectrum(
        name='footonium',
        wavelengths=wavelengths,
        values=background)

    # Generate peaks in spectrum, make Spectrum class
    max_value = 1
    bparams = [
        {'loc': 10, 'amplitude': 0.5 * max_value, 'width': 0.2},
        {'loc': 12, 'amplitude': max_value, 'width': 0.1},
        {'loc': 15, 'amplitude': 0.75 * max_value, 'width': 0.05},
        {'loc': 16, 'amplitude': 0.2 * max_value, 'width': 0.05},
        {'loc': 20, 'amplitude': 0.3 * max_value, 'width': 0.03323},
        {'loc': 25, 'amplitude': 0.3 * max_value, 'width': 0.3},
        {'loc': 30, 'amplitude': 0.05 * max_value, 'width': 0.1},
        {'loc': 31, 'amplitude': 0.1 * max_value, 'width': 0.1}
    ]
    fparams = [
        {'loc': 10, 'amplitude': 0.5 * max_value, 'width': 0.2},
        {'loc': 22, 'amplitude': 0.8 * max_value, 'width': 0.1},
        {'loc': 23, 'amplitude': 0.5 * max_value, 'width': 0.05},
        {'loc': 28, 'amplitude': 0.2 * max_value, 'width': 0.05},
        {'loc': 13, 'amplitude': 0.3 * max_value, 'width': 0.03323},
        {'loc': 28, 'amplitude': 0.3 * max_value, 'width': 0.3},
        {'loc': 4, 'amplitude': max_value, 'width': 0.1},
        {'loc': 11, 'amplitude': 0.1 * max_value, 'width': 0.1}
    ]
    for spec, peaks in ((bogo, bparams), (foo, fparams)):
        for params in peaks:
            add_peak(spec, **params)
    return bogo, foo
