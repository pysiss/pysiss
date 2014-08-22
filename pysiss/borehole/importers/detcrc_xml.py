""" file: detcrc_xml.py (pysiss.borehole.importers)
    author: Jess Robertson
            CSIRO Earth Science and Resource Engineering
    date: Tuesday 21 May, 2013

    description: Utilities for munging XML data returned from MUCL calls to
        the DET-CRC portal.
"""

import urllib2 as urllib
import xml
import numpy
import xml.etree.ElementTree
import cPickle as pickle
from ...utilities import try_float

# The URL for the data request
DATA_URL = "http://det-crc.csiro.au/open-data/wfs?version=2.0.0" + \
    "&request=GetFeature&typenames=mscl:scanned_data&sortby=mscl:depth"

# The tag of the data element which holds a single record
DATA_TAG = '{http://example.org/mscl}scanned_data'

# A way of decrufting the keys to get rid of the url in brackets
GET_KEY = lambda elem: elem.tag.split('}')[1]


def add_detcrc_xml(borehole, points=None):
    """ Import from XML data downloaded from the DET-CRC portal
    """
    xmltree = get_xml_data(npoints=points)
    xmldata = extract_all(xmltree)

    # Things to ignore
    for key in ['id', 'diameter', 'borehole_header_id']:
        del xmldata[key]

    # Get dataset data
    dataset_data = xmldata['depth']
    del xmldata['depth']

    # We need to denoise the data, so remove outliers
    thresholds = {'resistivity': 1, 'default': 3}  # in std values
    for key in xmldata.keys():
        try:
            threshold = thresholds[key]
        except KeyError:
            threshold = thresholds['default']
        vals = xmldata[key]
        vals[(vals - vals.mean()) ** 2 > (threshold * vals.std()) ** 2] \
            = vals.mean()
        xmldata[key] = vals

    # Add the datasets that need adding
    for key, dataset in xmldata.items():
        borehole.add_datum(
            dataset_axes=[dataset_data],
            signal=dataset,
            key=key,
            label=key.replace('_', ' '))


def get_xml_data(npoints=None):
    """ Get data from the DETCRC portal
    """
    # Info about the data
    data_url = DATA_URL
    if npoints is not None:
        data_url += '&count={0}'.format(npoints)

    # Try and load data from pickled file first
    xmlfilename = 'detcrc_xmltree.pkl'
    try:
        with open(xmlfilename, 'rb') as fhandle:
            xmltree = pickle.load(fhandle)
    except IOError:
        xmltree = xml.etree.ElementTree.parse(urllib.urlopen(data_url))
        with open(xmlfilename, 'wb') as fhandle:
            pickle.dump(xmltree, fhandle)
    return xmltree


def extract(xmltree, *keys):
    """ Makes lists of data out of an xml tree from DETCRC schema.

        Only adds an item to the lists if values for all keys are present in a
        data element.
    """
    # Loop through tree and collect matches
    lists = dict((k, []) for k in keys)
    for child in xmltree.findall('.//{0}'.format(DATA_TAG)):
        # Make a new temporary dictionary to hold values
        tempdict = dict.fromkeys(keys)
        for grandchild in child:
            key = GET_KEY(grandchild)
            if key in keys:
                tempdict[key] = try_float(grandchild.text)

        # Check that we have all values, otherwise don't add any at all
        if all([v is not None for v in tempdict.values()]):
            for key, value in tempdict.items():
                lists[key].append(try_float(value))
        else:
            continue

    # Convert to numpy arrays
    lists = dict((k, numpy.asarray(l)) for k, l in lists.items())
    return lists


def extract_all(xmltree):
    """ Extracts all data series into a Python dictionary of vectors
    """
    keys = get_data_keys(xmltree)
    return extract(xmltree, *keys)


def get_data_keys(xmltree):
    """ Returns the keys associated with the data in an XML tree.
    """
    # Loop through tree and collect matches
    keys = set([])
    for child in xmltree.findall('.//{0}'.format(DATA_TAG)):
        for grandchild in child:
            keys.add(GET_KEY(grandchild))

    return keys
