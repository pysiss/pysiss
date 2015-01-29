""" file:   unmarshallers.py (pysiss.vocabulary.wcs)
    author: Jess Robertson
            CSIRO Mineral Resources Flagship
    date:   Monday 25 August, 2014

    description: Unmarshalling functions for WCS metadata
"""

from .namespaces import NamespaceRegistry
from .gml.unmarshallers import position

from shapely.geometry import box

NAMESPACES = NamespaceRegistry()

def envelope(elem):
    """ Unmarshal an envelope element
    """
    projection = elem.attrib['srsName']
    lower_left, upper_right = \
        [position(e) for e in elem.xpath('gml:pos', namespaces=NAMESPACES)]
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

def formats(elem):
    """ Unmarshal an element contatining supported formats
    """
    return [e.text for e in elem.xpath('//wcs:formats/')]

def url_info(tag):
    """ Parse information about an OGC endpoint from getCapabilities request
    """
    return lambda elem: {
        'url': elem.xpath(
            '//{0}//wcs:OnlineResource/@*'.format(tag),
            namespaces=NAMESPACES)[0],
        'method': shorten_namespace(elem.xpath(
            '//{0}//wcs:HTTP/*'.format(tag),
            namespaces=NAMESPACES)[0].tag
        ).split(':')[1].lower()
    }

UNMARSHALLERS = {
    'wcs:envelope': envelope,
    'wcs:lonlatenvelope': envelope,
    'wcs:name': text,
    'wcs:description': text,
    'wcs:label': text,
    'wcs:supportedformats': formats,
    'wcs:getcapabilities': url_info('wcs:getcapabilities'),
    'wcs:describecoverage': url_info('wcs:describecoverage'),
    'wcs:getcoverage': url_info('wcs:getcoverage'),
}

__all__ = ['UNMARSHALLERS']
