#!/usr/bin/env python
""" file:   nvcl.py
    author: Josh Vote and Jess Robertson
            CSIRO Earth Science and Resource Engineering
    date:   23 December 2013

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
        data, and a download URL for getting analyte data. URLS are retrieved
        using standard dictionary syntax:

            registry = NVCLEndpointRegistry()
            url = registry['CSIRO']['wfsurl']  # Get the WFS URL for the CSIRO
                                               # NVCL endpoint

        New endpoints can be registered using `NVCLEndpointRegistry.register`.
    """

    __metaclass__ = Singleton

    def __init__(self):
        for endpoint, urls in NVCL_DEFAULT_ENDPOINTS.items():
            self.register(endpoint, **urls)

    def register(self, endpoint, wfsurl=None, dataurl=None, downloadurl=None,
                 update=False):
        """ Register an NVCL endpoint in the registry.

            This method avoids clobbering existing endpoints. If you want to
            update an existing endpoint, set the update flag to True.

            :param endpoint: A unique identifier for the endpoint
            :type endpoint: string
            :param wfsurl: The URL pointing to the web feature service for the
                NVCL endpoint.
            :type wfsurl: string
            :param dataurl: The URL pointing to the data query service for the
                NVCL endpoint.
            :type dataurl: string
            :param downloadurl: The URL pointing to the data download service
                for the NVCL endpoint.
            :type downloadurl: string

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

    def get_borehole_idents_and_urls(self, maxids=None):
        """ Generates a dictionary containing identifiers and urls for
            boreholes with NVCL scanned data at this endpoint

            :param maxids: The maximum number of boreholes to request or
                None for no limit
            :type maxids: integer
            :returns: an dictionary of urls keyed by borehole identifiers
        """
        wfs = WebFeatureService(self.urls['wfsurl'], version="1.1.0")
        wfsresponse = wfs.getfeature(
            typename="nvcl:ScannedBoreholeCollection",
            maxfeatures=maxids)
        xmltree = xml.etree.ElementTree.parse(wfsresponse)

        idents = {}
        bhstring = ".//{http://www.auscope.org/nvcl}scannedBorehole"
        for match in xmltree.findall(bhstring):
            idents[match.get('{http://www.w3.org/1999/xlink}title')] = \
                match.get('{http://www.w3.org/1999/xlink}href')
        return idents

    def get_borehole_idents(self, maxids=None):
        """ Returns the identifiers of boreholes with NVCL scanned data

            :param maxids: The maximum number of boreholes to request or
                None for no limit
            :type maxids: integer
            :returns: a list borehole identifiers
        """
        return self.get_borehole_idents_and_urls(maxids).keys()

    def get_borehole_datasets(self, hole_ident):
        """ Generates a dictionary of tuples representing all the NVCL datasets
            associated with this particular borehole

            :param hole_ident: The GUID for a borehole available at dataurl
            :type hole_ident: string
            :returns: a dictionary keyed by dataset name, where each dictionary
                value is the GUID of the dataset.
        """
        xmltree = None
        holeurl = \
            'getDatasetCollection.html?holeidentifier={0}'.format(hole_ident)
        url_handle = urllib.urlopen(self.urls['dataurl'] + holeurl)
        try:
            xmltree = xml.etree.ElementTree.parse(url_handle)
        finally:
            url_handle.close()

        datasets = {}
        for dset in xmltree.findall(".//Dataset"):
            datasets[dset.find('DatasetName').text] = \
                dset.find('DatasetID').text
        return datasets

    def get_logged_analytes(self, hole_ident, dataset_ident):
        """ Generates a dictionary mapping all NVCL analytes for a given
            borehole dataset to their GUIDs.

            Returns None if the XML fails to parse.

            :param hole_ident: The GUID for a borehole available at dataurl
            :type hole_ident: string
            :param dataset_ident: The GUID for a dataset available at dataurl
            :type dataset_ident: string
            :returns: a dictionary keyed by analyte name, where each value is
                the GUID for a given analyte.
        """
        analytes = None
        dseturl = 'getLogCollection.html?mosaicsvc=no&datasetid={0}'
        url_handle = urllib.urlopen(self.urls['dataurl']
                                    + dseturl.format(dataset_ident))

        # Parse XML tree to return analytes
        try:
            xmltree = xml.etree.ElementTree.parse(url_handle)
            analytes = {}
            for anlyte in xmltree.findall(".//Log"):
                log_ident = anlyte.find("LogID").text
                name = anlyte.find("logName").text
                analytes[name] = log_ident

        finally:
            url_handle.close()

        return analytes

    def get_borehole(self, hole_ident, name=None):
        """ Requests a CSV in the form of (startDepth, endDepth, analyteValue1,
            ..., analyteValueN) before parsing the analyte data into a
            pyboreholes.Borehole with a set of a sampling domains representing
            each of the analytes.

            :param name: Descriptive name for this borehole. Optional, if not
                specified this will default to the NVCL borehole id.
            :type name: string
            :returns: a `pyboreholes.Borehole` object
        """
        if name is None:
            name = hole_ident

        for dataset_guid in self.get_borehole_datasets(hole_ident).values():
            # Get all scalarids
            analyte_guids = self.get_logged_analytes(hole_ident, dataset_guid)

            # Generate request URL
            url = self.urls['dataurl'] + 'downloadscalars.html?'
            for ident in analyte_guids:
                url += '&logid={0}'.format(ident)

            siss_bhl_generator = SISSBoreholeGenerator()
            bh_url = self.get_borehole_idents_and_urls()[hole_ident]
            bhl = siss_bhl_generator.geosciml_to_borehole(
                name, urllib.urlopen(bh_url))

            print bhl

            fhandle = urllib.urlopen(url)
            try:
                analytedata = pandas.read_csv(fhandle)
                startcol = 'STARTDEPTH'
                endcol = 'ENDDEPTH'
                analytecols = [k for k in analytedata.keys()
                               if k not in (startcol, endcol)]

                # NVCL data results in start depths == end depths.
                # Ranges aren't really appropriate. Better to use sampling
                # domain
                analytedata = analytedata.drop_duplicates(startcol)
                startdepths = numpy.asarray(analytedata[startcol])
                domain = bhl.add_sampling_domain('nvcl', startdepths)

                # Make a property for each analyte in the borehole
                #
                # TODO: What to do with this? Despite now having borehole
                #       details, we still need to make a correspondence
                #       between analyte data and the borehole. Is what
                #       follows still valid?
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
