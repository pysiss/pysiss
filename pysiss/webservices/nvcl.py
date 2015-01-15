""" file: nvcl.py (pysiss.borehole.importers)
    author: Josh Vote and Jess Robertson
            CSIRO Earth Science and Resource Engineering
    date:   23 December 2013

    description: Importer for NVCL data services
"""

from ..borehole import PropertyType, SISSBoreholeGenerator
from ..borehole.datasets import PointDataSet  # , IntervalDataSet
from ..utilities import Singleton

from owslib.wfs import WebFeatureService
import numpy
import pandas
import requests
from lxml import etree
from StringIO import StringIO


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
        # TODO: use this in get_borehole() instead of creating another
        # instance?
        self.generator = SISSBoreholeGenerator()

    def __repr__(self):
        """ String representation
        """
        str = 'NVCLImporter(endpoint="{0}")'.format(self.endpoint)
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
        xmltree = etree.parse(wfsresponse)

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

    def get_dataset_idents(self, hole_ident):
        """ Generates a dictionary of tuples representing all the NVCL datasets
            associated with this particular borehole

            :param hole_ident: The GUID for a borehole available at dataurl
            :type hole_ident: string
            :returns: a dictionary keyed by dataset name, where each dictionary
                value is the GUID of the dataset.
        """
        xmltree = None
        holeurl = (self.urls['dataurl'] + 'getDatasetCollection.html?'
                   'holeidentifier={0}').format(hole_ident)
        response = requests.get(holeurl)
        if response:
            xmltree = etree.fromstring(response.content)

            datasets = {}
            for dset in xmltree.findall(".//Dataset"):
                datasets[dset.find('DatasetName').text] = \
                    dset.find('DatasetID').text
            return datasets

    def get_analyte_idents(self, hole_ident, dataset_ident):
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
        analyte_idents = None
        dseturl = 'getLogCollection.html?mosaicsvc=no&datasetid={0}'
        response = requests.get(self.urls['dataurl']
                                + dseturl.format(dataset_ident))

        # Parse XML tree to return analytes
        if response:
            xmltree = etree.fromstring(response.content)
            analyte_idents = {}
            for analyte in xmltree.findall(".//Log"):
                log_ident = analyte.find("LogID").text
                name = analyte.find("logName").text
                # sample_count = analyte.find('SampleCount').text
                analyte_idents[name] = log_ident
            return analyte_idents
        else:
            raise Exception(
                'Request for data returned {0}'.format(response.code))

    def get_analytes(self, hole_ident, dataset_name, dataset_ident,
                     analyte_idents=None,
                     from_depth=None, to_depth=None,):
        """ Get the analytes from the given borehole and dataset

            :param hole_ident: The identifier for a borehole
            :type hole_ident: string
            :param dataset_name: An identifier for the generated dataset
            :type dataset_name: string
            :param dataset_ident: The identifier for the dataset
            :type dataset_ident: string
            :param analyte_idents: The identifers of the analytes to download.
                Optional, if None then all analytes in the given dataset are
                downloaded.
            :type analyte_idents: list of str
            :param from_depth/to_depth: The depth range included in the
                dataset. Optional, defaults to the entire depths defined in
                the NVCL.
            :type from_depth/to_depth: float
        """
        # Get analyte data
        analyte_ident_dict = self.get_analyte_idents(hole_ident, dataset_ident)
        if len(analyte_ident_dict) == 0:
            # This dataset has no analytes
            print 'Warning, dataset {0} has no analytes'.format(dataset_ident)
            return None

        # Generate request URL
        if analyte_idents is None:
            analyte_idents = analyte_ident_dict.values()
        url = self.urls['dataurl'] + 'downloadscalars.html?'
        for ident in analyte_idents:
            url += '&logid={0}'.format(ident)

        # We'll use pandas to slurp the csv direct from the web service
        analytedata = pandas.read_csv(url)
        startcol = 'StartDepth'
        endcol = 'EndDepth'
        analytecols = [k for k in analytedata.keys()
                       if k not in (startcol, endcol)]

        # NVCL data results in start depths == end depths.
        # Ranges aren't really appropriate. Better to use sampling
        # dataset
        analytedata = analytedata.drop_duplicates(startcol)
        startdepths = numpy.asarray(analytedata[startcol])
        dataset = PointDataSet(dataset_name, startdepths)

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
            dataset.add_property(
                property_type=property_type,
                values=numpy.asarray(analytedata[analyte]))

        return dataset

    def get_mosaic(self, hole_ident, from_depth=None, to_depth=None):
        """ Requests a mosaic from the NVCL data portal

            The mosaic is a low-resolution composite of the image data
            associated with a given borehole, so is suitable for large
            borehole ranges
        """
        raise NotImplemented

    def get_images(self, hole_ident, from_depth=None, to_depth=None):
        """ Requests high-resolution images from the NVCL data portal

            These images are high-resolution and represent slices of the
            core sitting in the core tray.
        """
        raise NotImplemented

    def get_borehole(self, hole_ident, name=None, get_analytes=True,
                     raise_error=True):
        """ Generates a pysiss.borehole.Borehole instance containing the data
            from the given borehole.

            Each dataset defined on the borehole is downloaded down into a
            seperate Dataset instance

            :param hole_ident: The hole identifier
            :type hole_ident: string
            :param name: Descriptive name for this borehole. Optional, if not
                specified this will default to the NVCL borehole id.
            :type name: string
            :param get_analytes: If True, the analytes will also be downloaded
            :type get_analytes: bool
            :param raise_error: Whether to raise an exception on an HTTP error
                (e.g. 404'd). If false, get_borehole returns None.
            :returns: a `pysiss.borehole.Borehole` object
        """
        try:
            # Generate pysiss.borehole.Borehole instance to hold the data
            if name is None:
                name = hole_ident
            siss_bhl_generator = SISSBoreholeGenerator()
            bh_url = self.get_borehole_idents_and_urls()[hole_ident]
            response = requests.get(bh_url)

            # Break out now if the request fails
            if not response:
                return None
            bhl = siss_bhl_generator.geosciml_to_borehole(
                name, StringIO(response.content))

            # For each dataset in the NVCL we want to add a dataset and store
            # the dataset information in the DatasetDetails
            if get_analytes:
                datasets = self.get_dataset_idents(hole_ident)
                for dataset_name, dataset_guid in datasets.items():
                    dataset = self.get_analytes(hole_ident=hole_ident,
                                                dataset_name=dataset_name,
                                                dataset_ident=dataset_guid)
                    if dataset is not None:
                        bhl.add_dataset(dataset)

            return bhl

        except Exception, err:
            if raise_error:
                raise err
            else:
                return None
