""" file: featureservice.py
    author: Jess Robertson
            CSIRO Mineral Resources Flagship
    date:   somehting

    decsription: Implementation of simple FeatureService class
"""

from __future__ import print_function, division

from ...metadata import Metadata
from .service import OGCService

import requests
import logging

LOGGER = logging.getLogger('pysiss')


class FeatureService(object):

    """ Handles calls to an OGC Web Feature Service

        Parameters:
            endpoint - a URL pointing to the WCS endpoint

        Relevant attributes:
            version - the OGC version number for the endpoint
            capabilities - a Metadata instance containing the capabilities of
                the endpoint
    """

    def __init__(self, endpoint):
        super(FeatureService, self).__init__(ident=endpoint)

        # Set up mapping to OGC webservices
        self.service = OGCService(endpoint=endpoint,
                                  service_type='wfs')
        self.version = self.service.version
        self.capabilities = self.get_capabilities()

    def get_capabilities(self, update=False):
        """ Get the capabilities from the feature service
        """
        response = self.service.request(request='getcapabilities',
                                         method='get')
        cap = self._capabilities = Metadata(
            response.content, dtype='wfs:wfs_capabilities')

