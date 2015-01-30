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
import simplejson
import pkg_resources


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

    # Load request mappings from .json
    request_mappings = simplejson.load(
        pkg_resources.resource_stream(
            "pysiss.webservices", "coverageservice_mapping.json"))

    def __init__(self, endpoint):
        super(CoverageService, self).__init__(ident=endpoint)
        self.ident = self.endpoint = endpoint.split('?')[0]

        # Update metadata
        self._capabilities, self._descriptions = None, None
        self._version = '1.0.0' # Dummy for now, will get replaced

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
        if self._version is None:
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
        params = self._make_payload(request='getcapabilities')
        response = requests.get(self.endpoint, params=params)

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
            params = self._make_payload(request='describecoverage',
                                        ident=layer)
            response = requests.request(params=params,
                                        **self._describe_endpoint)
            if response.ok:
                desc = self._descriptions[layer] = Metadata(
                    tree=etree.fromstring(response.content),
                    mdatatype='wcs:describecoverage')

                # Get bounding box and grid information
                self.envelopes[layer] = \
                    unmarshal_all(desc.tree,
                                  '//wcs:spatialdomain//wcs:envelope')

            else:
                raise IOError("Can't access endpoint {0}, "
                              "server returned {1}".format(
                                  response.url, response.status_code))

    def get_coverage(self, bounds):
        """ Get coverage data for the given bounding box
        """
        pass

    def _make_payload(self, request, **kwargs):
        """ Generate a WCS payload for a request

            Params:
                request - the request type to make. One of
                    'getcapabilities', 'describecoverage',
                    'getcoverage'

            Other parameters get passed in as keyword arguments
        """
        # Get the payload from the mappings
        payload = self.request_mappings[self.version][request]

        # Check that we have all the required keyword arguments
        # for this mapping
        required_keywords = [v.lstrip('@') for v in payload.values()
                             if v.startswith('@')]
        missing = [k for k in required_keywords
                   if k not in kwargs.keys()]
        if missing:
            print 'Bailing on {0} request'.format(request)
            raise KeyError(("Missing keyword(s) {0} required to construct "
                            "payload for WCS request").format(
                                map(lambda s: s.lstrip('@'), missing)))

        # Generate the parameter dictionary for the call
        for key, value in payload.items():
            if value.startswith('@'):
                payload[key] = kwargs[value.lstrip('@')]
        return payload
