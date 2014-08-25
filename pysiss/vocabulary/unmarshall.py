""" file:   unmarshall.py (pysiss.vocabulary)
    author: Jess Robertson
            CSIRO Minerals Resources Flagship
    date:   Monday 25 August, 2014

    description: Wrapper functionality for unmarshalling XML elements
"""

from .utilities import xml_namespaces
from .gml import unmarshallers as gml
from .gsml import unmarshallers as gsml
from .erml import unmarshallers as erml

UNMARSHALLERS = {}
UNMARSHALLERS.update(gml.UNMARSHALLERS)
UNMARSHALLERS.update(gsml.UNMARSHALLERS)
UNMARSHALLERS.update(erml.UNMARSHALLERS)


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
        return elem


def process_element(elem):
    """ Process one XML etree element and return a dictionary of metadata

        If the child can be unmarshalled, then we unmarshal it and return the
        data. Otherwise, if the child has children of its own which have data,
        we return a dictionary of that data. If neither of these is true, we
        just skip the element altogether
    """
    # If we can unmarshall this directly, then lets do so
    return unmarshall(elem)

    # # If we can't then unmarshall will return None, so lets just return the
    # # element
    # if data:
    #     return data

    # elif len(elem) == 1:
    #     return process_element(elem.iterchildren().next())

    # else:
    #     # If we have attributes, get them
    #     data = {}
    #     for attrib, value in elem.items():
    #         if attrib.startswith('{'):
    #             data[xml_namespaces.shorten_namespace(attrib)] = value
    #         else:
    #             data[attrib] = value

    #     # If we have children, get their data
    #     for child in elem.iterchildren():
    #         child_data = process_element(child)
    #         if child_data:
    #             data[xml_namespaces.shorten_namespace(child.tag)] = child_data

    #     return data
