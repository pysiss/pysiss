""" file:   __init__.py (pysiss.borehole tests)
    author: Jess Robertson
            CSIRO Earth Science and Resource Engineering
    email:  jesse.robertson@csiro.au
    date:   Wednesday May 1, 2013

    description: Initialisation of tests.
"""

import pkgutil
import inspect

__all__ = []

# Discover all test files in test directory, and inject their
# global namespaces into the current global namespace. This
# lets unittest discover the tests nicely
for loader, name, is_pkg in pkgutil.walk_packages(__path__):
    module = loader.find_module(name).load_module(name)

    for name, value in inspect.getmembers(module):
        if name.startswith('__'):
            continue

        globals()[name] = value
        __all__.append(name)
