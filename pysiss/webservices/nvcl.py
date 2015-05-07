""" file: nvcl.py (pysiss.borehole.importers)
    author: Josh Vote and Jess Robertson
            CSIRO Earth Science and Resource Engineering
    date:   23 December 2013

    description: Importer for NVCL data services
"""

from __future__ import print_function, division

from ..borehole import Borehole, Collar
from ..borehole.datasets import PointDataset
from ..utilities import singleton
from ..metadata import Metadata, xml_to_metadata

import numpy
import pandas
import requests
from lxml import etree
import io
import logging


LOGGER = logging.getLogger('pysiss')

DEFAULT_ENDPOINTS = {
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
        'wfsurl': 'https://sarigdata.pir.sa.gov.au/nvcl/geoserver/wfs',
        'dataurl': 'https://sarigdata.pir.sa.gov.au/nvcl/NVCLDataServices/',
        'downloadurl': 'https://sarigdata.pir.sa.gov.au/nvcl/NVCLDownloadServices/'
    },
    'DPINSW': {
        'wfsurl': 'http://auscope.dpi.nsw.gov.au/geoserver/wfs',
        'dataurl': 'http://auscope.dpi.nsw.gov.au/NVCLDataServices/',
        'downloadurl': 'http://auscope.dpi.nsw.gov.au/NVCLDownloadServices/'
    }
}


class NVCLEndpointRegistry(dict, metaclass=singleton):

    """ Registry to manage information about NVCL endpoints

        Each endpoint stores a WFS URL, a data URL for queries about available
        data, and a download URL for getting analyte data. URLS are retrieved
        using standard dictionary syntax:

            registry = NVCLEndpointRegistry()
            url = registry['CSIRO']['wfsurl']  # Get the WFS URL for the CSIRO
                                               # NVCL endpoint

        New endpoints can be registered using `NVCLEndpointRegistry.register`.
    """

    def __init__(self):
        for endpoint, urls in DEFAULT_ENDPOINTS.items():
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
        if endpoint in set(self.keys()) and not(update):
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
            epts = list(registry.keys())
            raise KeyError('Unknown NVCL Endpoint {0}.'.format(endpoint) +
                           'Registered endpoints: {0}'.format(epts))

        # Invalidate cache
        self._cached = False

    def __repr__(self):
        """ String representation
        """
        string = 'NVCLImporter(endpoint="{0}")'.format(self.endpoint)
        return string

    @property
    def borehole_idents(self):
        """ Generates a list containing identifiers for
            boreholes with NVCL scanned data at this endpoint
        """
        self._get_borehole_idents_and_urls()
        return self._borehole_idents
    
    @property
    def borehole_data_endpoints(self):
        """ Get a list of data enpoints for the boreholes from the service
        """
        self._get_borehole_idents_and_urls()
        return self._borehole_urls
    
    def _get_borehole_idents_and_urls(self):
        """ Get info on the available boreholes

            # Todo: Use pysiss.webservices.FeatureService rather than
            #       raw requests call
        """
        if self._cached:
            return 

        # Make a request to the wfs
        payload = {
            'version': '1.1.0',
            'service': 'wfs',
            'request': 'getfeature',
            'typename': 'nvcl:ScannedBoreholeCollection'
        }
        response = requests.get(self.urls['wfsurl'], params=payload)
        response.raise_for_status()

        # Parse response
        mdata = xml_to_metadata(response.content)
        self._borehole_idents = mdata.xpath(".//nvcl:scannedBorehole/@xlink:title")
        self._borehole_urls = mdata.xpath(".//nvcl:scannedBorehole/@xlink:href")
        self.borehole_url_dict = \
            dict(zip(self._borehole_idents, self._borehole_urls))
        self._cached = True

    def get_dataset_idents(self, hole_ident):
        """ Generates a dictionary of tuples representing all the NVCL datasets
            associated with this particular borehole

            :param hole_ident: The GUID for a borehole available at dataurl
            :type hole_ident: string
            :returns: a dictionary keyed by dataset name, where each dictionary
                value is the GUID of the dataset.
        """
        mdata = None
        holeurl = (self.urls['dataurl'] + 'getDatasetCollection.html?'
                   'holeidentifier={0}').format(hole_ident)
        response = requests.get(holeurl)
        response.raise_for_status()

        # Parse results
        mdata = xml_to_metadata(response.content)
        datasets = {}
        for dset in mdata.findall(".//dataset"):
            datasets[dset.find('datasetname').text] = \
                dset.find('datasetid').text
        return datasets

    def get_analyte_idents(self, dataset_ident):
        """ Generates a dictionary mapping all NVCL analytes for a given
            borehole dataset to their GUIDs.

            Returns None if the XML fails to parse.

            :param dataset_ident: The GUID for a dataset available at dataurl
            :type dataset_ident: string
            :returns: a dictionary keyed by analyte name, where each value is
                the GUID for a given analyte.
        """
        analyte_idents = None
        dseturl = 'getLogCollection.html?mosaicsvc=no&datasetid={0}'
        response = requests.get(self.urls['dataurl']
                                + dseturl.format(dataset_ident))
        response.raise_for_status()

        # Parse XML tree to return analytes
        if response:
            mdata = xml_to_metadata(response.content)
            analyte_idents = {}
            for analyte in mdata.findall(".//log"):
                log_ident = analyte.find("logid").text
                name = analyte.find("logname").text
                # sample_count = analyte.find('SampleCount').text
                analyte_idents[name] = log_ident
            return analyte_idents
        else:
            raise Exception(
                'Request for NVCL data returned {0}'.format(
                    response.status_code))

    def get_analytes(self, hole_ident, dataset_name, dataset_ident,
                     analyte_idents=None):
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
        """
        # Get analyte data
        analyte_ident_dict = self.get_analyte_idents(dataset_ident)
        if len(analyte_ident_dict) == 0:
            # This dataset has no analytes
            LOGGER.warn('Dataset {0} has no analytes'.format(dataset_ident))
            return None

        # Generate request URL
        if analyte_idents is None:
            analyte_idents = analyte_ident_dict.values()
        url = self.urls['dataurl'] + 'downloadscalars.html?'
        url += '&'.join(['logid={0}'.format(i) for i in analyte_idents])
        response = requests.get(url)
        if not response.ok:
            raise IOError("Can't get analytes for borehole {0}, dataset {1}; "
                          "server returned {2}".format(hole_ident,
                                                       dataset_ident,
                                                       response.status_code))

        # We'll use pandas to slurp the csv direct from the web service
        analytedata = pandas.read_csv(io.StringIO(response.content))
        startcol = 'StartDepth'
        endcol = 'EndDepth'
        analytecols = [k for k in analytedata.keys()
                       if k not in (startcol, endcol)]

        # NVCL data results in start depths == end depths.
        # Ranges aren't really appropriate. Better to use sampling
        # dataset
        analytedata = analytedata.drop_duplicates(startcol)
        startdepths = numpy.asarray(analytedata[startcol])
        dataset = PointDataset(dataset_name, startdepths)

        # Make a property for each analyte in the borehole
        #
        # TODO: What to do with this? Despite now having borehole
        #       details, we still need to make a correspondence
        #       between analyte data and the borehole. Is what
        #       follows still valid?
        #
        for analyte in analytecols:
            property_type = PropertyType(
                ident=analyte,
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
        raise NotImplementedError

    def get_images(self, hole_ident, from_depth=None, to_depth=None):
        """ Requests high-resolution images from the NVCL data portal

            These images are high-resolution and represent slices of the
            core sitting in the core tray.
        """
        raise NotImplementedError

    def get_borehole(self, hole_ident, ident=None, get_analytes=True):
        """ Generates a pysiss.borehole.Borehole instance containing the data
            from the given borehole.

            Each dataset defined on the borehole is downloaded down into a
            seperate Dataset instance

            :param hole_ident: The hole identifier
            :type hole_ident: string
            :param ident: Descriptive ident for this borehole. Optional, if not
                specified this will default to the NVCL borehole id.
            :type ident: string
            :param get_analytes: If True, the analytes will also be downloaded
            :type get_analytes: bool
            :returns: a `pysiss.borehole.Borehole` object
        """
        # Get data
        if ident is None:
            ident = hole_ident
        self._get_borehole_idents_and_urls()
        response = requests.get(self.borehole_url_dict[hole_ident])
        response.raise_for_status()

        # Construct borehole collar instance
        mdata = xml_to_metadata(response.content)
        collar_elem = mdata['.//geosciml:BoreholeCollar']
        if collar_elem is not None:
            loc_elem = collar_elem['.//geosciml:location//gml:pos']
            latitude, longitude = (float(f) for f in loc_elem.text.split())
            elevation = float(collar_elem['.//geosciml:elevation'].text)
            collar = Collar(latitude, longitude)
        else:
            collar = None

        # Construct Borehole instance
        bhl = Borehole(ident=ident, collar=collar, metadata=mdata)

        # For each dataset in the NVCL we want to add a dataset and store
        # the dataset information in the DatasetDetails
        if get_analytes:
            datasets = self.get_dataset_idents(hole_ident)
            for dataset_ident, dataset_guid in datasets.items():
                dataset = self.get_analytes(hole_ident=hole_ident,
                                            dataset_name=dataset_ident,
                                            dataset_ident=dataset_guid)
                if dataset is not None:
                    bhl.add_dataset(dataset)

        return bhl
    