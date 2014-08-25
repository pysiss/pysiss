""" file:   unmarshall.py (pysiss.vocabulary)
    author: Jess Robertson
            CSIRO Minerals Resources Flagship
    date:   Monday 25 August, 2014

    description: Wrapper functionality for unmarshalling XML elements
"""

from .utilities import xml_namespaces, shorten_namespace
from .gml import unmarshallers as gml
from .gsml import unmarshallers as gsml
from .erml import unmarshallers as erml
from .lithology.composition import unmarshallers as comp

UNMARSHALLERS = {}
UNMARSHALLERS.update(gml.UNMARSHALLERS)
UNMARSHALLERS.update(gsml.UNMARSHALLERS)
UNMARSHALLERS.update(erml.UNMARSHALLERS)
UNMARSHALLERS.update(comp.UNMARSHALLERS)


def unmarshall(elem):
    """ Unmarshall an lxml.etree.Element element

        If there is no unmarshalling function available, this just returns the
        lxml.etree element.
    """
    tag = xml_namespaces.shorten_namespace(elem.tag)
    unmarshall = UNMARSHALLERS.get(tag)
    if unmarshall:
        return unmarshall(elem)
    else:
        return None


def process_element(elem):
    """ Process one XML etree element and return a dictionary of metadata

        If the child can be unmarshalled, then we unmarshal it and return the
        data. Otherwise, if the child has children of its own which have data,
        we return a dictionary of that data. If neither of these is true, we
        just skip the element altogether
    """
    # If we can unmarshall this directly, then lets do so
    data = unmarshall(elem.tag)

    # If we can't then unmarshall will return None, so lets just return the
    # element
    if data:

        return unmarshall(elem)

    elif len(elem) == 1:
        return process_element(elem.iterchildren().next())

    else:
        # If we have attributes, get them
        data = {}
        for attrib, value in elem.items():
            if attrib.startswith('{'):
                data[shorten_namespace(attrib)] = value
            else:
                data[attrib] = value

        # If we have children, get their data
        for child in elem.iterchildren():
            child_data = process_element(child)
            if child_data:
                data[shorten_namespace(child.tag)] = child_data

        return data
