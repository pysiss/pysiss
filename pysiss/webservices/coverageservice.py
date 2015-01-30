""" file: coverageservice.py
    author: Jess Robertson
            CSIRO Minerals Resources Flagship
    date:   January 2015

    description: Class to handle WCS endpoints
"""

from ..utilities import id_object
from ..metadata import Metadata, NamespaceRegistry, unmarshal_all, unmarshal

import requests
from lxml import etree


class CoverageService(id_object):

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

    namespaces = NamespaceRegistry()

    def __init__(self, endpoint):
        super(CoverageService, self).__init__(ident=endpoint)
        self.ident = self.endpoint = endpoint.split('?')[0]

        # Update metadata
        self._capabilities, self._descriptions = None, None

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
    def layers(self):
        """ The layers available from the WCS
        """
        self.get_capabilities()
        return self._layers

    @property
    def version(self):
        """ The version of the WCS endpoint
        """
        self.get_capabilities()
        return self._version

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
            self._version = cap.xpath('@version')[0]
            self._describe_endpoint = \
                unmarshal_all(cap.tree, 'wcs:describecoverage')[0]
            self._coverage_endpoint = \
                unmarshal_all(cap.tree, 'wcs:getcoverage')[0]

            # Get available datasets
            self._layers = cap.xpath(
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
        self.envelopes = dict()
        for layer in self.layers:
            payload = dict(
                service='wcs',
                request='describecoverage',
                version=self.version,
                ident=layer)
            response = requests.request(params=payload,
                                        **self._describe_endpoint)
            if response.ok:
                desc = self._descriptions[layer] = etree.fromstring(response.content),

                # # Get bounding box and grid information
                # self.envelopes[layer] = \
                #     unmarshal_all(desc.tree,
                #                   '//wcs:spatialdomain//wcs:envelope')

            else:
                raise IOError("Can't access endpoint {0}, "
                              "server returned {1}".format(
                                  response.url, response.status_code))

    def get_coverage(self, bounds):
        """ Get coverage data for the given bounding box
        """
        pass
