""" file: parse.py (pysiss.webservices.ogc.interfaces.wcs.2_0_0)

    description: Parsing functions for information from a WCS2.0.0
        webservice
"""

from __future__ import print_function, division

from ......metadata import Metadata

from lxml import etree

def get_capabilities(response):
    """ Parse a get_capabilities response from a WCS 2.0.0 webservice
    """
    # Parse XML response
    capabilities = Metadata(response.text,
                            dtype='ows:capabilities')
    version = capabilities.xpath('@version')[0]

    # Get operations
    operations = []
    for op_elem in capabilities.xpath('//ows:operation'):
        try:
            # Get operation name
            operation_name = op_elem.xpath('@name')

            # Get the HTTP stuff about the operation
            method_elem = op_elem.xpath('.//ows:http/*')[0]
            http_method = etree.QName(method_elem.tag).localname.lower()
            endpoint = method_elem.xpath('.//@xlink:href')[0]

            # Get parameters & allowed values, if any
            parameters = {}
            for param in op_elem.xpath('.//ows:parameter'):
                pname = param.attrib['name']
                values = [v.text() for v in
                          param.xpath('.//ows:allowedvalues/ows:value')]
                parameters[pname] = values
            if len(parameters) == 0:
                parameters = None

            # Append all this to the operations data
            operations.append({
                'name': operation_name,
                'http_method': http_method,
                'endpoint': endpoint,
                'parameters': parameters
            })

        except IndexError:
            continue

    # Get available layers
    layers = [e.text() for e in capabilities.xpath('//wcs:coverageid')]

    # Get endpoints for describing coverages and getting data
    return {
        'capabilities': capabilities,
        'version': version,
        'operations': operations,
        'layers': layers
    }

def describe_coverage(response):
    """ Parse a describeCoverage response from a WCS 2.0.0 webservice
    """
    # Parse XML response
    capabilities = Metadata(response.text,
                            dtype='wcs:describe_coverage')

def get_coverage(response):
    """ Parse an XML response from a WCS 2.0.0 webservice
    """
    # Parse XML response
    capabilities = Metadata(response.text,
                            dtype='wcs:get_coverage')
