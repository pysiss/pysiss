""" file:   unmarshallers.py (pysiss.vocabulary.gml)
    author: Jess Robertson
            CSIRO Mineral Resources Flagship
    date:   Monday 25 August, 2014

    description: Unmarshalling functions for GeoSciML/GML objects
"""

from ...coverage.vector import MappedFeature
from ...metadata import Metadata
from ..namespaces import NamespaceRegistry, expand_namespace, shorten_namespace
from ..gml.unmarshallers import UNMARSHALLERS as GML_UNMARSHALLERS

NAMESPACES = NamespaceRegistry()


def mapped_feature(elem):
    """ Unmarshal a gsml:MappedFeature element
    """
    # Shape and projection data
    shape_elem = elem.find('./gsml:shape', namespaces=NAMESPACES)
    shape_data = shape(shape_elem)
    shape_elem.clear()  # Remove shape element from metadata

    # Identifier
    ident = elem.get(expand_namespace('gml:id')) or None

    # Get specification metadata records
    spec_elem = elem.find('./gsml:specification', namespaces=NAMESPACES)
    spec = specification(spec_elem)

    return MappedFeature(ident=ident, shape=shape_data['shape'],
                         projection=shape_data['projection'],
                         specification=spec)


def specification(elem):
    """ Unmarshall a gsml:specification element
    """
    # If we only have an xlink, this is just a pointer to another record
    xlink = elem.get(expand_namespace('xlink:href'))
    if xlink:
        # Just return the metadata key
        # We need to strip out the # from the link
        return xlink.lstrip('#')

    # Otherwise we need to create a new metadata record, then return the
    # relevant key
    else:
        spec_elem = elem.iterchildren().next()
        ident = spec_elem.get(expand_namespace('gml:id'))
        mdata = Metadata(ident=ident,
                         type=shorten_namespace(spec_elem.tag),
                         tree=spec_elem)
        return mdata.ident


def shape(elem):
    """ Unmarshal a gsml:shape element

        Here we just pass through to underlying gml shape data
    """
    child = elem[0]
    unmarshal = GML_UNMARSHALLERS[shorten_namespace(child.tag)]
    return unmarshal(child)


def get_value(elem):
    """ Unmashall an element containing a gsml:value element somewhere in its
        descendents.

        Returns the text value for a given element, stripping out children of
        the given element
    """
    return elem.find('.//gsml:value/text()', namespaces=NAMESPACES)


def cgi_termrange(elem):
    """ Unmarshal a gsml:CGI_TermRange element

        Return the value range for a given element
    """
    return map(get_value,
               elem.xpath('.//gsml:CGI_TermValue', namespaces=NAMESPACES))


def sampling_frame(elem):
    """ Unmarshal a gsml:samplingFrame element
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
    'gsml:samplingFrame': sampling_frame,
    'gsml:MappedFeature': mapped_feature,
    'gsml:specification': specification
}

__all__ = (UNMARSHALLERS,)
