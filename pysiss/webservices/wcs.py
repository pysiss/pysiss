""" file: wcs.py
    author: Jess Robertson
            CSIRO Minerals Resources Flagship
    date:   January 2015

    description: Class to handle WCS endpoints
"""

from ..utilities import id_object

import requests


class CoverageService(id_object):

    """ Gets access to a OGC Web Coverage Service

        Parameters:
            endpoint - a URL pointing to the WCS endpoint
            version - an OGC WCS version string (optional, defaults to '1.1.0')

    """

    def __init__(self, endpoint, version=None):
        super(CoverageService, self).__init__(ident='coverage_service')
        self.version = version or '1.1.0'
        self.endpoint = endpoint.split('?')[0]

    def get_capabilities(self):
        """ Get the capabilities from the coverage service
        """
        payload = dict(
            service='WCS',
            version=self.version,
            request='getCapabilities')
        response = requests.get(self.endpoint, params=payload)
        

