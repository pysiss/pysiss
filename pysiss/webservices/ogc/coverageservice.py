""" file: coverageservice.py
    author: Jess Robertson
            CSIRO Minerals Resources Flagship
    date:   January 2015

    description: Class to handle WCS endpoints
"""

from ...utilities import id_object
from ...metadata import Metadata, NamespaceRegistry, unmarshal_all, unmarshal
from .mapping import OGCServiceMapping
from ...geospatial import Coverage

import requests
from lxml import etree
import simplejson
import pkg_resources
import logging
from collections import defaultdict, Iterable
import os

LOGGER = logging.getLogger('pysiss')


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

        # Initialize metadata slots
        self._capabilities, self._descriptions = None, None
        self._version = '1.0.0' # Dummy for now, will get replaced

        # Set up mapping to OGC webservices
        self.mappings = OGCServiceMapping(version=self._version,
                                          service='wcs')

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
        if self._capabilities is None:
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
        query_string = self.mappings.request(request='getcapabilities',
                                             method='get')
        response = requests.get(self.endpoint + query_string)

        # Parse metadata
        if response.ok:
            cap = self._capabilities = Metadata(
                tree=etree.fromstring(response.content),
                mdatatype='wcs:wcs_capabilities')

            # Update version number
            self._version = cap.xpath('@version')[0]
            self.mappings = OGCServiceMapping(version=self.version,
                                              service='wcs')

            # Update endpoints
            self._describe_endpoint = \
                unmarshal_all(cap.tree, '//wcs:describecoverage')[0]
            self._coverage_endpoint = \
                unmarshal_all(cap.tree, '//wcs:getcoverage')[0]

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
            # Construct and get data
            endpoint = self._describe_endpoint['url']
            method = self._describe_endpoint['method']
            query = self.mappings.request(request='describecoverage',
                                          ident=layer,
                                          **self._describe_endpoint)
            response = requests.request(url=endpoint + query,
                                        method=method)

            if response.ok:
                desc = self._descriptions[layer] = Metadata(
                    tree=etree.fromstring(response.content),
                    mdatatype='wcs:describecoverage')

                # Get bounding box and grid information
                self.envelopes[layer] = \
                    unmarshal_all(desc.tree,
                                  '//wcs:spatialdomain/wcs:envelope')

            else:
                raise IOError("Can't access endpoint {0}, "
                              "server returned {1}".format(
                                  response.url, response.status_code))

    def get_coverage(self, ident, bounds=None, time_bounds=None,
                     projection=None, output_format=None,
                     latitude=None, longitude=None, time=None):
        """ Get coverage data for the given bounding box

            Parameters are checked against the capabilities of the WCS endpoint
            and ValueErrors are raised if a parameter is not allowed.

            Parameters:
                ident - an identifier for the layer you want to get a coverage
                    from (see CoverageService.layers for valid value). Invalid
                    values will raise a ValueError
                bounds - the bounding box of the coverage, given as a
                    (min_x, min_y, max_x, max_y) tuple. Setting any of these
                    values to None will default to the value for the coverage.
                time_bounds - the time bounds of the coverage, given as a
                    (min_t, max_t) tuple, Optional, if not specified defaults
                    to entire time bounds.
                projection - the projection of the bounding box. Optional,
                    defaults to the same projection as the coverage
                latitude - a single latitude if you only want one
                    pixel wide coverage back. Optional, if specified,
                    max_latitude and min_latitude in bounds should be None.
                longitude - a single longitude value if you only want one
                    pixel wide coverage back. Optional, if specified,
                    max_longitude and min_longitude in bounds should be None.
                time - a single time if you only want one time back. Optional,
                    only one of time or time_bounds should be specified.
                output_format - the output format for the data from the server.
                    Optional, defaults to geoTIFF, or the first format
                    specified in `self.formats` if geoTIFF is not available.

            Returns:
                a pysiss.geospatial.Coverage object with the requested data
        """
        # Ensure we have the latest info from the server
        self.get_capabilities()
        self.get_descriptions()
        self._check('get_coverage', 'ident', ident, self.layers)
        metadata = self._descriptions[ident].tree

        # Check requested projection
        if projection is not None:
            allowed_proj = unmarshal_all(
                metadata, '//wcs:supportedcrss/wcs:requestcrss')
            self._check('get_coverage', 'projection', projection, allowed_proj)

        # Check requested output format
        allowed_formats = unmarshal_all(
                metadata, '//wcs:supportedformats/wcs:formats')
        if output_format is not None:
            self._check('get_coverage', 'output_format', output_format,
                        allowed_formats)
        else:
            output_format = allowed_formats[0]

        # Construct request
        params = dict(ident=ident,
                      minlongitude=bounds[0], maxlongitude=bounds[2],
                      minlatitude=bounds[1], maxlatitude=bounds[3],
                      format=output_format)
        if projection:
            params.update({'projection': projection})
        if time_bounds:
            params.update({'mintime': time_bounds[0],
                           'maxtime': time_bounds[1]})

        # Construct and get data
        endpoint = self._describe_endpoint['url']
        method = self._describe_endpoint['method']
        query = self.mappings.request(request='getcoverage',
                                      method=method,
                                      **params)
        response = requests.request(url=endpoint + query,
                                    method=method)
        if response.ok:
            # Stream response to file
            if not os.path.exists('coverages'):
                os.mkdir('coverages')
            filename = 'coverages/{0}.{1}'.format(ident, output_format)
            with open(filename, 'wb') as fhandle:
                fhandle.write(response.content)

            # Write metadata to file
            md_filename = 'coverages/{0}_metadata.xml'.format(ident)
            with open(md_filename, 'wb') as fhandle:
                fhandle.write(etree.tostring(
                                self.descriptions[ident].tree))

            return Coverage(filename,
                            ident=ident,
                            metadata=self.descriptions[ident])
        else:
            raise IOError(("Couldn't get coverage {0}, server "
                          "returned {1}").format(ident, response.status_code))

    def _check(self, function, key, value, allowed):
        """ Check whether a parameter value is ok
        """
        if value not in allowed:
            raise ValueError(('Unknown argument {0}={1} passed to {3}, '
                              'allowed values are {2}').format(key, value,
                                                               allowed,
                                                               function))
