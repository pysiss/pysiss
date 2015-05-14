""" file: pysiss_namespace.py (pysiss.metadata)
    author: Jess Robertson
            CSIRO Mineral Resources Flagship
    date: Monday May 2, 2015

    description: Defines a namespace for pysiss metadata
"""

from .._version import __version__

# Namespace for pysiss objects in XML
PYSISS_NAMESPACE = \
	'{{http://geoanalytics.csiro.au/pysiss/{0}}}'.format(__version__)
