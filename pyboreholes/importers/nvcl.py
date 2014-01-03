#!/usr/bin/env python

from owslib.wfs import WebFeatureService
import pyboreholes
import urllib, xml, numpy, pandas
import xml.etree.ElementTree

# Various NVCL providers keyed by a short abbreviation
NVCL_ENDPOINTS = {
    'CSIRO' : {
        'wfsurl' : 'http://nvclwebservices.vm.csiro.au/geoserverBH/wfs',
        'dataurl' : 'http://nvclwebservices.vm.csiro.au/NVCLDataServices/',
        'downloadurl' : 'http://nvclwebservices.vm.csiro.au/NVCLDownloadServices/'
    },
    'GSWA' : {
        'wfsurl' : 'http://geossdi.dmp.wa.gov.au/services/wfs',
        'dataurl' : 'http://geossdi.dmp.wa.gov.au/NVCLDataServices/',
        'downloadurl' : 'http://geossdi.dmp.wa.gov.au/NVCLDownloadServices/'
    },
    'MRT' : {
        'wfsurl' : 'http://www.mrt.tas.gov.au/web-services/wfs',
        'dataurl' : 'http://www.mrt.tas.gov.au/NVCLDataServices/',
        'downloadurl' : None
    },
    'NTGS' : {
        'wfsurl' : 'http://geology.data.nt.gov.au/nvcl/wfs',
        'dataurl' : 'http://geology.data.nt.gov.au/NVCLDataServices/',
        'downloadurl' : 'http://geology.data.nt.gov.au/NVCLDownloadServices/'
    },
    'PIRSA' : {
        'wfsurl' : 'https://egate.pir.sa.gov.au/nvcl/geoserver/wfs',
        'dataurl' : 'https://egate.pir.sa.gov.au/nvcl/NVCLDataServices/',
        'downloadurl' : 'https://egate.pir.sa.gov.au/nvcl/NVCLDownloadServices/'
    },
    'DPINSW' : {
        'wfsurl' : 'http://auscope.dpi.nsw.gov.au/geoserver/wfs',
        'dataurl' : 'http://auscope.dpi.nsw.gov.au/NVCLDataServices/',
        'downloadurl' : 'http://auscope.dpi.nsw.gov.au/NVCLDownloadServices/'
    }
}

def nvcl_get_borehole_ids(wfsurl, maxids=None):    
    """ Generates an array of tuples representing
        The boreholes with NVCL scanned data at a given WFS endpoint
        
        returns an array of (href, title) tuples

        :param wfsurl: The web feature service URL to request data from
        :type wfsurl: string
        :param maxids: The maximum number of boreholes to request or None for no limit
        :type maxids: integer
    """
    wfs = WebFeatureService(wfsurl, version="1.1.0")
    wfsresponse = wfs.getfeature(typename="nvcl:ScannedBoreholeCollection", maxfeatures=maxids)
    xmltree = xml.etree.ElementTree.parse(wfsresponse)
    
    ids = []
    for sb in xmltree.findall(".//{http://www.auscope.org/nvcl}scannedBorehole"):
        href = sb.get('{http://www.w3.org/1999/xlink}href')
        title = sb.get('{http://www.w3.org/1999/xlink}title')
        ids.append((href, title))
    return ids

def nvcl_get_borehole_datasets(dataurl, holeidentifier):
    """ Generates an array of tuples representing
        All the NVCL datasets associated with this particular borehole
        
        returns an array of (id, name, omUrl) tuples

        :param dataurl: The NVCL dataservice URL to request data from
        :type dataurl: string
        :param holeidentifier: The GUID for a borehole available at dataurl
        :type holeidentifier: string
    """
    xmltree = None
    fp = urllib.urlopen(dataurl + 'getDatasetCollection.html?holeidentifier={0}'.format(holeidentifier))
    try:
        xmltree = xml.etree.ElementTree.parse(fp)
    finally:
        fp.close()
    
    datasets = []
    for ds in xmltree.findall(".//Dataset"):
        id = ds.find('DatasetID').text
        name = ds.find('DatasetName').text
        omurl = ds.find('OmUrl').text
        datasets.append((id, name, omurl))
    return datasets

def nvcl_get_logged_analytes(dataurl, datasetid):
    """ Generates an array of tuples representing
        all the NVCL analytes for a given dataset
        
        returns an array of (logid, analytename) tuples

        :param dataurl: The NVCL dataservice URL to request data from
        :type dataurl: string
        :param datasetid: The GUID for a dataset available at dataurl
        :type datasetid: string
    """
    xmltree = None
    fp = urllib.urlopen(dataurl + 'getLogCollection.html?mosaicsvc=no&datasetid={0}'.format(datasetid))
    try:
        xmltree = xml.etree.ElementTree.parse(fp)
    finally:
        fp.close()

    analytes = []
    for an in xmltree.findall(".//Log"):
        logid = an.find("LogID").text
        name = an.find("logName").text
        analytes.append((logid, name))
        
    return analytes

def nvcl_get_analytes_as_borehole(dataurl, name, *scalarids):
    """ Requests a CSV in the form of (startDepth, endDepth, analyteValue1, ... , analyteValueN)
        before parsing the analyte data into a pyboreholes.borehole with a set of a sampling domains 
        representing each of the analytes.
        
        returns a pyboreholes.Borehole object

        :param dataurl: The NVCL dataservice URL to request data from
        :type dataurl: string
        :param name: Descriptive name for this borehole
        :type name: string
        :param scalarids: A variable number of strings, each representing the GUID for scalars available at dataurl
        :type scalarids: string
    """
    url = dataurl + 'downloadscalars.html?'
    for id in scalarids:
        url += '&logid={0}'.format(id)
    
    bh = pyboreholes.Borehole(name)
    
    fp = urllib.urlopen(url)
    try:
        analytedata = pandas.read_csv(fp, header=0)
        
        startcol = 'STARTDEPTH'
        endcol = 'ENDDEPTH'
        analytecols = [k for k in analytedata.keys() if k not in (startcol, endcol)]
        
        # NVCL data results in start depths == end depths.  
        # Ranges aren't really appropriate. Better to use sampling domain
        analytedata = analytedata.drop_duplicates(startcol)
        startdepths = numpy.asarray(analytedata[startcol])
        
        for analyte in analytecols:
            domain = bh.add_sampling_domain(analyte, startdepths)
            propertyType = pyboreholes.PropertyType(
               name=analyte,
               long_name=analyte,
               units=None,
               description=None,
               isnumeric=False
            )
            
            domain.add_property(propertyType, numpy.asarray(analytedata[analyte]))
    finally:
        fp.close()
        
    return bh

    

