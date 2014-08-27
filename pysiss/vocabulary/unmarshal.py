""" file:   unmarshal.py (pysiss.vocabulary)
    author: Jess Robertson
            CSIRO Minerals Resources Flagship
    date:   Monday 25 August, 2014

    description: Wrapper functionality for unmarshalling XML elements
"""

from .namespaces import shorten_namespace, expand_namespace
from .gml import unmarshallers as gml
from .gsml import unmarshallers as gsml
from .erml import unmarshallers as erml

from lxml import etree

UNMARSHALLERS = {}
UNMARSHALLERS.update(gml.UNMARSHALLERS)
UNMARSHALLERS.update(gsml.UNMARSHALLERS)
UNMARSHALLERS.update(erml.UNMARSHALLERS)


def unmarshal(elem):
    """ Unmarshal an lxml.etree.Element element

        If there is no unmarshalling function available, this just returns the
        lxml.etree element.
    """
    tag = shorten_namespace(elem.tag)
    unmarshal = UNMARSHALLERS.get(tag)
    if unmarshal:
        return unmarshal(elem)
    else:
        return None


def unmarshal_all(filename, tag='gsml:MappedFeature'):
    """ Unmarshall all instances of a tag from an xml file
        and return them as a list of objects
    """
    tag = expand_namespace(tag)
    results = []
    with open(filename, 'rb') as fhandle:
        try:
            context = iter(etree.iterparse(fhandle, events=('end',), tag=tag))
            for event, elem in context:
                results.append(unmarshal(elem))
        except etree.XMLSyntaxError:
            pass
    return results
