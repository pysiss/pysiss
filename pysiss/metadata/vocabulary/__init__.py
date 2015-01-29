""" file:   __init__.py (pysiss.vocabulary)
    author: Jess Robertson
            Mineral Resources Flagship, CSIRO
    date:   something

    description: init file
"""

from .unmarshal import unmarshal, unmarshal_all
import .namespaces

__all__ = ['unmarshal', 'unmarshal_all', 'namespaces']
