""" file: wcs.py
    author: Jess Robertson
            CSIRO Minerals Resources Flagship
    date:   January 2015

    description: Class to handle WCS endpoints
"""

from ..utilities import id_object
from ..metadata import Metadata
from ..metadata.namespaces import NamespaceRegistry

import requests
from lxml import etree


class CoverageService(id_object):

    """ Gets access to a OGC Web Coverage Service

        Parameters:
            endpoint - a URL pointing to the WCS endpoint
            version - an OGC WCS version string (optional, defaults to '1.1.0')

    """

    namespaces = NamespaceRegistry()

    def __init__(self, endpoint):
        super(CoverageService, self).__init__(ident='coverage_service')
        self.endpoint = endpoint.split('?')[0]
        self.get_capabilities()

    def get_capabilities(self):
        """ Get the capabilities from the coverage service
        """
        payload = dict(
            service='WCS',
            request='getCapabilities')
        response = requests.get(self.endpoint, params=payload)

        if response.ok:
            # Parse metadata
            metadata = etree.fromstring(response.content)
            cs = self.capabilities = Metadata(tree=metadata,
                                              type='coverage')

            # Pull out some useful information
            self.version = cs.xpath('@version')[0]
            self.describe_url = cs.xpath(
                '//wcs:DescribeCoverage//wcs:OnlineResource/@*',
                namespaces=self.namespaces)[0]
            self.get_url = cs.xpath(
                '//wcs:GetCoverage//wcs:OnlineResource/@*',
                namespaces=NamespaceRegistry())[0]
            return cs

        else:
            raise IOError("Can't access endpoint, "
                          "server returned {0}".format(response.code))
