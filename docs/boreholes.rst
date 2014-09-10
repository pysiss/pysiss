.. _boreholes:

.. _base_namespace:
.. py:module:: pysiss.borehole

Borehole class
==============

A Borehole class instance stores all of the domains defined on a particular borehole. Different domains may correspond to different datasets (e.g. multi-element geochemistry vs geophysical logs vs spectral data) which can be sampled on different domains, and have different measurement characteristics (i.e. spectral data has a wavelength dimension, while geochemistry data tends to be a single value at each point). The actual borehole data is stored as properties defined on these domains.

In the future this class may include methods to desurvey a borehole and interpret more complex borehole features.

Borehole class API
------------------

.. autoclass:: pysiss.borehole.Borehole
    :members:
    :undoc-members:

.. autoclass:: pysiss.borehole.Details
    :members:
    :undoc-members:

.. autoclass:: pysiss.borehole.Property
    :members:
    :undoc-members:

.. autoclass:: pysiss.borehole.Dataset
    :members:
    :undoc-members:

.. autoclass:: pysiss.borehole.PointDataset
    :members:
    :undoc-members:

.. autoclass:: pysiss.borehole.IntervalDataset
    :members:
    :undoc-members:

.. automodule:: pysiss.borehole.analysis
    :members:
    :undoc-members:

SISS Borehole generators
------------------------

.. automodule:: pysiss.borehole.siss
    :members:
    :undoc-members:
