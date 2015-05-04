""" file: coverageservice.py
    author: Jess Robertson
            CSIRO Minerals Resources Flagship
    date:   January 2015

    description: Class to handle WCS endpoints
"""

from __future__ import print_function, division

from ...utilities import accumulator
from ...metadata import Metadata, unmarshal_all, ObjectWithMetadata
from .service import OGCService
from ...geospatial import Coverage

import requests
from lxml import etree
import logging
import os

LOGGER = logging.getLogger('pysiss')


class CoverageService(ObjectWithMetadata):

    """ Gets access to a OGC Web Coverage Service

        Parameters:
            endpoint - a URL pointing to the WCS endpoint

        Relevant attributes:
            version - the OGC version number for the endpoint
            capabilities - a Metadata instance containing the capabilities of
                the endpoint
            layers - a list of layer names served by the endpoint
            descriptions - a dictionary keyed by layer name describing each
                coverage
    """

    def __init__(self, endpoint):
        # Initialize version using get_capabilities call
        super(CoverageService, self).__init__(ident=endpoint)
        self.service = OGCService(endpoint=endpoint,
                                  service_type='wcs')
        self.capabilities = self.service.capabilities
        self.version = self.service.version

    @property
    def layers(self):
        """ The layers available from the WCS
        """
        return self.service.layers

    @property
    def descriptions(self):
        return self.describe_coverage()

    def _check(self, function, key, value, allowed):
        """ Check whether a parameter value is ok
        """
        if value not in allowed:
            raise ValueError(('Unknown argument {0}={1} passed to {3}, '
                              'allowed values are {2}').format(key, value,
                                                               allowed,
                                                               function))

    def describe_coverage(self, layer_id, update=False):
        # Check whether we already have a description for the given coverage
        if self._descriptions is not None and not update:
            description = self._descriptions.get(layer_id)
            if description:
                return self._descriptions


    def get_coverage(self, layer_id, bounds, update=False):
        # Check whether we already have data for the given coverage
        if self._coverage[layer_id] is not None and not update:
            return self._coverage[layer_id]

