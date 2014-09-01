""" file:   geoscience_australia.py (pysiss.webservices)
    author: Jess Robertson
            CSIRO Mineral Resources National Research Flagship
    date:   2 September 2014

    description: Importer for NVCL data services
"""

# Add 2.5M geology
wfsurl_template = ()

# Add WA faults
wfsurl_template = "http://www.ga.gov.au/geows/{0}/oneg_wa_1m/wfs"
geologic_objects = ('contacts', 'faults', 'geologicunits')


DEFAULT_ENDPOINTS = {
    'wa_faults_1m': 
}