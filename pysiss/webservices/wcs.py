""" file: wcs.py
    author: Jess Robertson
            CSIRO Minerals Resources Flagship
    date:   January 2015

    description: Class to handle WCS endpoints
"""

from ..utilities import id_object
from ..metadata import Metadata
from ..metadata.namespaces import NamespaceRegistry, shorten_namespace

import requests
from lxml import etree
from shapely.geometry import box

NAMESPACES = NamespaceRegistry()


def url_info(tree, tag, namespaces=None):
    """ Parse information about an OGC endpoint from getCapabilities request
    """
    if namespaces is None:
        namespaces = NAMESPACES
    return {
        'url': tree.xpath(
            '//{0}//wcs:OnlineResource/@*'.format(tag),
            namespaces=namespaces)[0],
        'method': shorten_namespace(tree.xpath(
            '//{0}//wcs:HTTP/*'.format(tag),
            namespaces=namespaces)[0].tag
        ).split(':')[1].lower()
    }


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
        self._capabilities, self._description = None, None
        self.get_capabilities(update=True)
        self.get_description(update=True)

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
    def description(self):
        if self._description is None:
            self.get_description(update=True)
        return self._description

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
                type='wcs:WCS_Capabilities')
            self.version = cap.xpath('@version')[0]
            self.describe_endpoint = url_info(cap, 'wcs:DescribeCoverage')
            self.coverage_endpoint = url_info(cap, 'wcs:GetCoverage')

            # Get available datasets
            self.layers = cap.xpath(
                'wcs:ContentMetadata/wcs:CoverageOfferingBrief/wcs:name/text()',
                namespaces=self.namespaces)

        else:
            raise IOError("Can't access endpoint {0}, "
                          "server returned {1}".format(response.url, response.status_code))

    def get_description(self, update=False):
        """ Get a description of the coverage from the service
        """
        if self._description is not None and not update:
            return

        # Update description from server
        self.get_capabilities()
        self._description = dict()
        for layer in self.layers:
            payload = dict(
                service='wcs',
                request='describecoverage',
                version=self.version,
                ident=layer)
            response = requests.request(params=payload,
                                        **self.describe_endpoint)
            if response.ok:
                desc = self._description[layer] = Metadata(
                    tree=etree.fromstring(response.content),
                    type='wcs:CoverageDescription')

                # Get bounding box and grid information
                envelope = desc.xpath(
                    '//wcs:spatialDomain//wcs:Envelope',
                    namespaces=self.namespaces)[0]
                self.projection = envelope.attrib['srsName']
                lower_left, upper_right = \
                    [map(float, e.text.split())
                     for e in envelope.xpath('gml:pos',
                                             namespaces=self.namespaces)]
                self.bounding_box = box(lower_left[0], lower_left[1],
                                        upper_right[0], upper_right[1])
                self.offset_vectors = \
                    [map(float, e.text.split())
                     for e in envelope.xpath('gml:pos',
                                             namespaces=self.namespaces)]

            else:
                raise IOError("Can't access endpoint {0}, "
                              "server returned {1}".format(response.url, 
                                                           response.status_code))

    def get_coverage(self, bounds):
        """ Get coverage data for the given bounding box
        """
        raise NotImplementedError()
