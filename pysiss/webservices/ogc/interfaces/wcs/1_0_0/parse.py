""" file: parse.py (pysiss.webservices.ogc.interfaces.wcs.1_0_0)

    description: Parsing functions for information from a WCS1.0.0
        webservice
"""

from __future__ import print_function, division

from .....metadata import Metadata

from lxml import etree

def get_capabilities(response):
    """ Parse a get_capabilities response from a WCS 1.0.0 webservice
    """
    # Parse XML response
    capabilities = Metadata(response.text,
                            dtype='wfs:wfs_capabilities')
    version = capabilities.xpath('@version')[0]

    # # Get operations
    operations = []
    for op_elem in capabilities.xpath('//ows:operation'):
        try:
            method_elem = op_elem.xpath('.//ows:http/*')[0]
            operations.append({
                'operation': op_elem.xpath('@name'),
                'method':  etree.QName(method_elem.tag).localname.lower(),
                'url': method_elem.xpath('.//@xlink:href')[0]
            })
        except IndexError:
            continue

    # # Get available layers
    layers = []
    # layers = [e.text() for e in capabilities.xpath('//wcs:coverageid')]

    # Get endpoints for describing coverages and getting data
    return {
        'capabilities': capabilities,
        'version': version,
        'operations': operations,
        'layers': layers
    }

def describe_coverage(response):
    """ Parse a describeCoverage response from a WCS 1.0.0 webservice
    """
    pass

def get_coverage(response):
    """ Parse an XML response from a WCS 1.0.0 webservice
    """
    pass
