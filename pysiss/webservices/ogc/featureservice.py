""" file: featureservice.py
    author: Jess Robertson
            CSIRO Mineral Resources Flagship
    date:   somehting

    decsription: Implementation of simple FeatureService class
"""

from ...utilities import id_object
from ...metadata import Metadata, NamespaceRegistry, unmarshal_all
from .mapping import OGCServiceMapping, accumulator
from ...geospatial import Coverage

import requests
from lxml import etree
import logging

LOGGER = logging.getLogger('pysiss')


class FeatureService(id_object):

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
        self.ident = self.endpoint = endpoint.split('?')[0]

        # Initialize metadata slows
        self._capabilities = None
        self._version = '1.0.0'  # Dummy for now, replaced on \
                                 # first getcapabilities request

        # Set up mapping to OGC webservices
        self.mappings = OGCServiceMapping(version=self._version,
                                          service='wfs')

    @property
    def capabilities(self):
        """ The capabilities of the WFS
        """
        if self._capabilities is None:
            self.get_capabilities(update=True)
        return self._capabilities

    def get_capabilities(self, update=False):
        """ Get the capabilities from the feature service
        """
        if self._capabilities is not None and not update:
            return
        query_string = self.mappings.request(request='getcapabilities',
                                             method='get')
        response = requests.get(self.endpoint + query_string)

        # Parse metadata
        if response.ok:
            cap = self._capabilities = Metadata(
                tree=etree.fromstring(response.content),
                mdatatype='wfs:wfs_capabilities')

            # Update version number and mappings
            self._version = cap.xpath('@version')[0]
            self.mappings = OGCServiceMapping(version=self._version,
                                              service='wfs')
        else:
            raise IOError("Can't get capabilities from endpoint {0}, "
                          "server returned {1}, content was:\n\n{2}".format(
                                response.url, response.status_code,
                                response.content))

