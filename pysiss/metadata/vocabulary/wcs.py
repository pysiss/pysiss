""" file:   wcs.py (pysiss.metadata)
    author: Jess Robertson
            CSIRO Mineral Resources Flagship
    date:   Monday 25 August, 2014

    description: Unmarshalling functions for WCS metadata
"""

from ..namespaces import NamespaceRegistry, shorten_namespace
from .gml import position
from ..regularize import regularize

from shapely.geometry import box
from lxml import etree

NSP = {'namespaces': NamespaceRegistry()}

def envelope(elem):
    """ Unmarshal an envelope element
    """
    projection = elem.attrib['srsName']
    lower_left, upper_right = \
        map(position, elem.findall('gml:pos', **NSP))
    bounding_box = box(lower_left[0], lower_left[1],
                       upper_right[0], upper_right[1])
    return {'bounding_box': bounding_box,
            'lower_left': lower_left,
            'upper_right': upper_right,
            'projection': projection}

def text(elem):
    """ Unmarshall an element containing a string
    """
    return elem.text

def number(elem):
    """ Unmarshal an element containing a number
    """
    return float(elem.text)

def formats(elem):
    """ Unmarshal an element contatining supported formats
    """
    return [e.text for e in elem.findall('wcs:formats', **NSP)]

def url_info(tag):
    """ Parse information about an OGC endpoint from getCapabilities request
    """
    rtag = regularize(tag)
    return lambda elem: {
        'url': elem.xpath(
            '//{0}//wcs:onlineresource/@*'.format(rtag), **NSP)[0],
        'method': shorten_namespace(
            elem.xpath('//{0}//wcs:http/*'.format(rtag), **NSP)[0].tag
        ).split(':')[1].lower()
    }

UNMARSHALLERS = {
    'wcs:envelope': envelope,
    'wcs:lonlatenvelope': envelope,
    'wcs:name': text,
    'wcs:description': text,
    'wcs:label': text,
    'wcs:requestcrss': text,
    'wcs:formats': text,
    'wcs:singlevalue': number,
    'wcs:supportedformats': formats,
    'wcs:getcapabilities': url_info('wcs:getcapabilities'),
    'wcs:describecoverage': url_info('wcs:describecoverage'),
    'wcs:getcoverage': url_info('wcs:getcoverage'),
}



__all__ = ['UNMARSHALLERS']
