""" file: wcs.py
    author: Jess Robertson
            CSIRO Minerals Resources Flagship
    date:   January 2015

    description: Class to handle WCS endpoints
"""

from ..utilities import id_object
from ..metadata import Metadata
from ..metadata.namespaces import NamespaceRegistry, shorten_namespace
from ..vocabulary.unmarshal import unmarshal

import requests
from lxml import etree
from shapely.geometry import box

NAMESPACES = NamespaceRegistry()


class CoverageService(id_object):

    """ Gets access to a OGC Web Coverage Service

        Parameters:
            endpoint - a URL pointing to the WCS endpoint
            version - an OGC WCS version string (optional, defaults to '1.1.0')

    """

    namespaces = NamespaceRegistry()

    def __init__(self, endpoint):
        super(CoverageService, self).__init__(ident=endpoint)
        self.ident = self.endpoint = endpoint.split('?')[0]

        # Update metadata
        self._capabilities, self._descriptions = None, None
        self.get_capabilities(update=True)
        self.get_descriptions(update=True)

    def make_payload(self, ident, bbox,
                     tbox=None, projection=None):
        """ Generate a WCS payload for a request
        """
        pass

    @property
    def capabilities(self):
        """ The capabilities of the WCS
        """
        if self._capabilities is None:
            self.get_capabilities(update=True)
        return self._capabilities

    @property
    def descriptions(self):
        if self._descriptions is None:
            self.get_descriptions(update=True)
        return self._descriptions

    def get_capabilities(self, update=False):
        """ Get the capabilities from the coverage service
        """
        if self._capabilities is not None and not update:
            return

        # Update capabilities from server
        payload = dict(
            service='wcs',
            request='getcapabilities')
        response = requests.get(self.endpoint, params=payload)

        # Parse metadata
        if response.ok:
            cap = self._capabilities = Metadata(
                tree=etree.fromstring(response.content),
                mdatatype='wcs:wcs_capabilities')
            self.version = cap.xpath('@version')[0]
            self.describe_endpoint = \
                unmarshall_all(cap, 'wcs:describecoverage')[0]
            self.coverage_endpoint = unmarshall_all(cap, 'wcs:getcoverage')[0]

            # Get available datasets
            self.layers = cap.xpath(
                'wcs:contentmetadata/wcs:coverageofferingbrief'
                '/wcs:name/text()',
                namespaces=self.namespaces)

        else:
            raise IOError("Can't access endpoint {0}, "
                          "server returned {1}".format(response.url,
                                                       response.status_code))

    def get_descriptions(self, update=False):
        """ Get a description of the coverage from the service
        """
        if self._descriptions is not None and not update:
            return

        # Update description from server
        self.get_capabilities()
        self._descriptions = dict()
        for layer in self.layers:
            payload = dict(
                service='wcs',
                request='describecoverage',
                version=self.version,
                ident=layer)
            response = requests.request(params=payload,
                                        **self.describe_endpoint)
            if response.ok:
                desc = self._descriptions[layer] = Metadata(
                    tree=etree.fromstring(response.content),
                    mdatatype='wcs:coveragedescription')

                # Get bounding box and grid information
                envelope = unmarshall_all('//wcs:spatialDomain//wcs:Envelope')

            else:
                raise IOError("Can't access endpoint {0}, "
                              "server returned {1}".format(
                                  response.url, response.status_code))

    def get_coverage(self, bounds):
        """ Get coverage data for the given bounding box
        """
        raise NotImplementedError()
