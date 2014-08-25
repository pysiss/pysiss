""" file:   unmarshallers.py (pysiss.vocabulary.gml)
    author: Jess Robertson
            CSIRO Mineral Resources Flagship
    date:   Monday 25 August, 2014

    description: Unmarshalling functions for GeoSciML/GML objects
"""

from ..utilities import xml_namespaces
from ..gml.unmarshallers import UNMARSHALLERS as GML_UNMARSHALLERS

NAMESPACES = xml_namespaces.NamespaceRegistry()


def shape(elem):
    """ Unmarshal a gsml:shape element

        Here we just pass through to underlying gml shape data
    """
    child = elem[0]
    unmarshal = GML_UNMARSHALLERS[xml_namespaces.shorten_namespace(child.tag)]
    return unmarshal(child)


def get_value(elem):
    """ Unmashall an element containing a gsml:value element somewhere in its
        descendents.

        Returns the text value for a given element, stripping out children of
        the given element
    """
    result = elem.xpath('.//gsml:value/text()',
                        namespaces=NAMESPACES)
    if result:
        return result[0]
    else:
        return None


def cgi_termrange(elem):
    """ Unmarshal a gsml:CGI_TermRange element

        Return the value range for a given element
    """
    return map(get_value,
               elem.xpath('.//gsml:CGI_TermValue',
                          namespaces=NAMESPACES))


def sampling_frame(elem):
    """ Unmarshal a gsml:samplingFrame element
    """
    return elem.get(xml_namespaces.expand_namespace('xlink:href'))


UNMARSHALLERS = {
    'gsml:shape': shape,
    'gsml:value': get_value,
    'gsml:CGI_TermValue': get_value,
    'gsml:CGI_TermRange': cgi_termrange,
    'gsml:preferredAge': get_value,
    'gsml:observationMethod': get_value,
    'gsml:positionalAccuracy': get_value,
    'gsml:samplingFrame': sampling_frame
}

__all__ = (UNMARSHALLERS,)
