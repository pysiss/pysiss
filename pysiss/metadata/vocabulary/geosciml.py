""" file:   unmarshallers.py (pysiss.vocabulary.gml)
    author: Jess Robertson
            CSIRO Mineral Resources Flagship
    date:   Monday 25 August, 2014

    description: Unmarshalling functions for GeoSciML/GML objects
"""

from ...geospatial.feature import Feature
from ..metadata import Metadata
from .gml import UNMARSHALLERS as GML_UNMARSHALLERS


def mapped_feature(elem):
    """ Unmarshal a geosciml:mappedfeature element
    """
    # Shape and projection data
    shape_elem = elem.find('./geosciml:shape')
    shape_data = shape(shape_elem)
    shape_elem.clear()  # Remove shape element from metadata

    # Identifier
    ident = elem.get(expand_namespace('gml:id')) or None

    # Get specification metadata records
    spec_elem = elem.find('./geosciml:specification')
    spec = specification(spec_elem)

    return Feature(ident=ident, shape=shape_data['shape'],
                   projection=shape_data['projection'],
                   specification=spec)


def specification(elem):
    """ Unmarshall a geosciml:specification element
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
                         dtype=shorten_namespace(spec_elem.tag),
                         tree=spec_elem)
        return mdata.ident


def shape(elem):
    """ Unmarshal a geosciml:shape element

        Here we just pass through to underlying gml shape data
    """
    child = elem[0]
    unmarshal = GML_UNMARSHALLERS[shorten_namespace(child.tag)]
    return unmarshal(child)


def get_value(elem):
    """ Unmashall an element containing a geosciml:value element somewhere in its
        descendents.

        Returns the text value for a given element, stripping out children of
        the given element
    """
    return elem.find('.//geosciml:value/text()')


def cgi_termrange(elem):
    """ Unmarshal a geosciml:cgi_termrange element

        Return the value range for a given element
    """
    return map(get_value,
               elem.xpath('.//geosciml:cgi_termvalue'))


def sampling_frame(elem):
    """ Unmarshal a geosciml:samplingframe element
    """
    return elem.get(expand_namespace('xlink:href'))


UNMARSHALLERS = {
    'geosciml:shape': shape,
    'geosciml:value': get_value,
    'geosciml:cgi_termvalue': get_value,
    'geosciml:cgi_termrange': cgi_termrange,
    'geosciml:preferredAge': get_value,
    'geosciml:observationmethod': get_value,
    'geosciml:positionalaccuracy': get_value,
    'geosciml:samplingframe': sampling_frame,
    'geosciml:mappedfeature': mapped_feature,
    'geosciml:specification': specification
}

__all__ = ['UNMARSHALLERS']
