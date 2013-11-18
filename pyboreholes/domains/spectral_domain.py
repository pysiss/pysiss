#!/usr/bin/env python
""" file: spectral_domain.py (pyboreholes.domains)
    author: Jess Robertson
            CSIRO Earth Science and Resource Engineering
    date: Sunday November 10, 2013

    description: Domain for spectral data
"""

from .sampling_domain import SamplingDomain
import pywt

class SpectralDomain(SamplingDomain):
    
    """ Domain to store spectral data
    """
    
    def __init__(self):
        super(SpectralDomain, self).__init__()
