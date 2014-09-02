""" file:   geoscience_australia.py (pysiss.webservices)
    author: Jess Robertson
            CSIRO Mineral Resources National Research Flagship
    date:   2 September 2014

    description: Importer for Geoscience Australia data services
"""

# Add 2.5M geology
DEFAULT_ENDPOINTS = {
    'wa1m': dict(
        url_template="http://www.ga.gov.au/geows/{0}/oneg_wa_1m/wfs",
        geologic_objects=('contacts', 'faults', 'geologicunits')
    ),
    'aus2.5m': dict(
        url_template="http://www.ga.gov.au/geows/{0}/oneg_aus_2_5m/wfs",
        geologic_objects=('contacts', 'faults', 'geologicunits', 'shearzones')
    )
}
