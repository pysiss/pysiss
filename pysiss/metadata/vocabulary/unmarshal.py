""" file:   unmarshal.py (pysiss.vocabulary)
    author: Jess Robertson
            CSIRO Minerals Resources Flagship
    date:   Monday 25 August, 2014

    description: Wrapper functionality for unmarshalling XML elements
"""

from . import gml, geosciml, erml, wcs, wfs, csw

from lxml.etree import iterparse, XMLSyntaxError

UNMARSHALLERS = {}
UNMARSHALLERS.update(gml.UNMARSHALLERS)
UNMARSHALLERS.update(geosciml.UNMARSHALLERS)
UNMARSHALLERS.update(erml.UNMARSHALLERS)
UNMARSHALLERS.update(wcs.UNMARSHALLERS)
UNMARSHALLERS.update(wfs.UNMARSHALLERS)
UNMARSHALLERS.update(csw.UNMARSHALLERS)


def unmarshal(metadata):
    """ Unmarshal a Metadata element

        If there is no unmarshalling function available, this just returns the
        lxml.etree element.
    """
    # Sort out what we've been given.
    tag = metadata.namespaces.regularize(metadata.tag)
    if tag.namespace not in (None, 'None'):
        tag = '{0.namespace}:{0.localname}'.format(tag)
    else:
        tag = '{0.localname}'.format(tag)

    # Find an unmarshaller
    unmarshal = UNMARSHALLERS.get(tag)

    # Unmarshal it!
    if unmarshal:
        return unmarshal(metadata)
    else:
        print "Can't unmarshal {0}".format(tag)
        return None


def unmarshal_all(metadata, query):
    """ Unmarshal all instances returned by xpath query

        Parameters:
            metadata - a Metadata instance to search over
            query - an xpath query to select elements
    """
    results = []
    for elem in metadata.xpath(query):
        results.append(unmarshal(elem))
    return results
