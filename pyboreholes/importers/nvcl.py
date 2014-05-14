#!/usr/bin/env python
""" file: nvcl.py
    author: Josh Vote and Jess Robertson
            CSIRO Earth Science and Resource Engineering
    date: 23 December 2013

    description: Importer for NVCL data services
"""

from owslib.wfs import WebFeatureService
from .. import PropertyType, SISSBoreholeGenerator
from ..utilities import Singleton
import numpy
import pandas
import urllib
import xml.etree.ElementTree


NVCL_DEFAULT_ENDPOINTS = {
    'CSIRO': {
        'wfsurl': 'http://nvclwebservices.vm.csiro.au/geoserverBH/wfs',
        'dataurl': 'http://nvclwebservices.vm.csiro.au/NVCLDataServices/',
        'downloadurl':
        'http://nvclwebservices.vm.csiro.au/NVCLDownloadServices/'
    },
    'GSWA': {
        'wfsurl': 'http://geossdi.dmp.wa.gov.au/services/wfs',
        'dataurl': 'http://geossdi.dmp.wa.gov.au/NVCLDataServices/',
        'downloadurl': 'http://geossdi.dmp.wa.gov.au/NVCLDownloadServices/'
    },
    'MRT': {
        'wfsurl': 'http://www.mrt.tas.gov.au/web-services/wfs',
        'dataurl': 'http://www.mrt.tas.gov.au/NVCLDataServices/',
        'downloadurl': None
    },
    'NTGS': {
        'wfsurl': 'http://geology.data.nt.gov.au/nvcl/wfs',
        'dataurl': 'http://geology.data.nt.gov.au/NVCLDataServices/',
        'downloadurl': 'http://geology.data.nt.gov.au/NVCLDownloadServices/'
    },
    'PIRSA': {
        'wfsurl': 'https://egate.pir.sa.gov.au/nvcl/geoserver/wfs',
        'dataurl': 'https://egate.pir.sa.gov.au/nvcl/NVCLDataServices/',
        'downloadurl': 'https://egate.pir.sa.gov.au/nvcl/NVCLDownloadServices/'
    },
    'DPINSW': {
        'wfsurl': 'http://auscope.dpi.nsw.gov.au/geoserver/wfs',
        'dataurl': 'http://auscope.dpi.nsw.gov.au/NVCLDataServices/',
        'downloadurl': 'http://auscope.dpi.nsw.gov.au/NVCLDownloadServices/'
    }
}


class NVCLEndpointRegistry(dict):

    """ Registry to manage information about NVCL endpoints

        Each endpoint stores a WFS URL, a data URL for queries about available
        data, and a download URL for getting analyte data. New endpoints can be
        registered using `NVCLEndpointRegistry.register`
    """

    __metaclass__ = Singleton

    def __init__(self):
        for endpoint, urls in NVCL_DEFAULT_ENDPOINTS.items():
            self.register(endpoint, **urls)

    def register(self, endpoint, wfsurl=None, dataurl=None, downloadurl=None,
                 update=False):
        """ Register an NVCL endpoint in the registry.

            This avoids clobbering existing endpoints.

            :param endpoint: A unique identifier for the endpoint
            :type endpoint: string

        """
        # Check that we don't already have this endpoint registered
        if endpoint in self.keys() and not(update):
            raise KeyError("Endpoint {0} is already in the registry and you "
                           "don't want to update it".format(endpoint))

        # Add the endpoint to the registry
        self[endpoint] = {
            'wfsurl': wfsurl,
            'dataurl': dataurl,
            'downloadurl': downloadurl
        }


class NVCLImporter(object):

    """ Import boreholes by consuming NVCL services

        :param endpoint: An endpoint identifier. To get a list of currently
            registered endpoints, call `NVCLEndpointRegistry().keys()`. A
            KeyError is raised if an unknown endpoint is used.
        :type endpoint: string
    """

    def __init__(self, endpoint='CSIRO'):
        super(NVCLImporter, self).__init__()
        self.endpoint = endpoint

        # Get URL data associated with endpoint
        registry = NVCLEndpointRegistry()
        try:
            self.urls = registry[endpoint]
        except KeyError:
            raise KeyError('Unknown NVCL Endpoint {0}.'.format(endpoint) +
                           'Registered endpoints: {0}'.format(registry.keys()))

        # Set up SISSBoreholeGenerator instance
        self.generator = SISSBoreholeGenerator()

    def __repr__(self):
        """ String representation
        """
        str = 'NVCLImporter(endpoint={0})'.format(self.endpoint)
        return str

    def get_borehole_ids(self, maxids=None):
        """ Generates an array of tuples representing
            The boreholes with NVCL scanned data at a given WFS endpoint

            returns an array of (href, title) tuples

            :param wfsurl: The web feature service URL to request data from
            :type wfsurl: string
            :param maxids: The maximum number of boreholes to request or
                None for no limit
            :type maxids: integer
        """
        wfs = WebFeatureService(self.urls['wfsurl'], version="1.1.0")
        wfsresponse = wfs.getfeature(
            typename="nvcl:ScannedBoreholeCollection",
            maxfeatures=maxids)
        xmltree = xml.etree.ElementTree.parse(wfsresponse)

        idents = []
        bhstring = ".//{http://www.auscope.org/nvcl}scannedBorehole"
        for match in xmltree.findall(bhstring):
            href = match.get('{http://www.w3.org/1999/xlink}href')
            title = match.get('{http://www.w3.org/1999/xlink}title')
            idents.append((href, title))
        return idents

    def get_borehole_datasets(self, holeident):
        """ Generates an array of tuples representing all the NVCL datasets
            associated with this particular borehole

            :param dataurl: The NVCL dataservice URL to request data from
            :type dataurl: string
            :param holeident: The GUID for a borehole available at dataurl
            :type holeident: string
            :returns: an array of (id, name, omUrl) tuples
        """
        xmltree = None
        holeurl = \
            'getDatasetCollection.html?holeidentifier={0}'.format(holeident)
        url_handle = urllib.urlopen(self.urls['dataurl'] + holeurl)
        try:
            xmltree = xml.etree.ElementTree.parse(url_handle)
        finally:
            url_handle.close()

        datasets = []
        for dset in xmltree.findall(".//Dataset"):
            ident = dset.find('DatasetID').text
            name = dset.find('DatasetName').text
            omurl = dset.find('OmUrl').text
            datasets.append((ident, name, omurl))
        return datasets

    def get_logged_analytes(self, datasetid):
        """ Generates an array of tuples representing all the NVCL analytes for
            a given dataset.

            :param dataurl: The NVCL dataservice URL to request data from
            :type dataurl: string
            :param datasetid: The GUID for a dataset available at dataurl
            :type datasetid: string
            :returns: an array of (logid, analytename) tuples
        """
        xmltree = None
        dseturl = 'getLogCollection.html?mosaicsvc=no&datasetid={0}'
        url_handle = urllib.urlopen(self.urls['dataurl']
                                    + dseturl.format(datasetid))
        try:
            xmltree = xml.etree.ElementTree.parse(url_handle)
        finally:
            url_handle.close()

        analytes = []
        for anlyt in xmltree.findall(".//Log"):
            logid = anlyt.find("LogID").text
            name = anlyt.find("logName").text
            analytes.append((logid, name))

        return analytes

    def get_analytes_as_borehole(self, scanned_borehole_url, name=None,
                                 *scalarids):
        """ Requests a CSV in the form of (startDepth, endDepth, analyteValue1,
            ..., analyteValueN) before parsing the analyte data into a
            pyboreholes.Borehole with a set of a sampling domains representing
            each of the analytes.

            :param scanned_borehole_url: The NVCL scanned borehole URL
            :type scanned_borehole_url: string
            :param name: Descriptive name for this borehole. Optional, if not
                specified this will default to the NVCL borehole id.
            :type name: string
            :param scalarids: A variable number of strings, each representing
                the GUID for scalars available at dataurl
            :type scalarids: string
            :returns: a `pyboreholes.Borehole` object
        """
        url = self.urls['dataurl'] + 'downloadscalars.html?'
        for ident in scalarids:
            url += '&logid={0}'.format(ident)

        siss_bhl_generator = SISSBoreholeGenerator()
        bhl = siss_bhl_generator.geosciml_to_borehole(
            name, urllib.urlopen(scanned_borehole_url))

        fhandle = urllib.urlopen(url)
        try:
            analytedata = pandas.read_csv(fhandle)
            startcol = 'STARTDEPTH'
            endcol = 'ENDDEPTH'
            analytecols = [k for k in analytedata.keys()
                           if k not in (startcol, endcol)]

            # NVCL data results in start depths == end depths.
            # Ranges aren't really appropriate. Better to use sampling domain
            analytedata = analytedata.drop_duplicates(startcol)
            startdepths = numpy.asarray(analytedata[startcol])
            domain = bhl.add_sampling_domain('nvcl', startdepths)

            # Make a property for each analyte in the borehole
            #
            # TODO: What to do with this? Despite now having borehole details,
            #       we still need to make a correspondence between analyte data
            #       and the borehole. Is what follows still valid?
            #
            for analyte in analytecols:
                property_type = PropertyType(
                    name=analyte,
                    long_name=analyte,
                    units=None,
                    description=None,
                    isnumeric=False)
                domain.add_property(property_type,
                                    numpy.asarray(analytedata[analyte]))
        finally:
            fhandle.close

        return bhl
