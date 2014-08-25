""" file:   unmarshallers.py (pysiss.vocabulary.gml)
    author: Jess Robertson
            CSIRO Mineral Resources Flagship
    date:   Monday 25 August, 2014

    description: Unmarshalling functions for GeoSciML/GML objects
"""

from ..utilities import xml_namespaces, shorten_namespace, expand_namespace
from ..gml.unmarshallers import UNMARSHALLERS as GML_UNMARSHALLERS

NAMESPACES = xml_namespaces.NamespaceRegistry()


def shape(elem):
    """ Unmarshall a gsml:shape element

        Here we just pass through to underlying gml shape data
    """
    child = elem[0]
    return GML_UNMARSHALLERS[shorten_namespace(child.tag)](child)


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
    """ Unmarshall a gsml:CGI_TermRange element

        Return the value range for a given element
    """
    return map(get_value,
               elem.xpath('.//gsml:CGI_TermValue',
                          namespaces=NAMESPACES))


def sampling_frame(elem):
    """ Unmarshall a gsml:samplingFrame element
    """
    return elem.get(expand_namespace('xlink:href'))


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
