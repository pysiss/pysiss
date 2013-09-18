Introduction to borehole_analysis
=================================

author: Jess Robertson, CSIRO Earth Science and Resource Engineering

email: jesse.robertson with CSIRO's domain (google it)

date: Wednesday 1 May 2013

This is a python module to carry out some basic analysis of borehole data

Probably the easiest way to get a feel for the behavior of the library is to have a look at the use cases supplied in this documentation. 

Building and installing `borehole_analysis`
---------------------------------

All you should need to do is enter the python directory, and execute

    $ ./setup.py build && sudo ./setup.py install

which should build and install the Python bindings for your system.

Building documentation
----------------------

If you want to build the documentation for `borehole_analysis` then you will need to have a version of `sphinx <http://sphinx.pocoo.org/>`_ installed -- you can check by doing::

  python -c 'import sphinx'

If that fails grab the latest version of and install it with::

  > sudo easy_install -U Sphinx

Now you are ready to build a template for your docs, using
sphinx-quickstart::

  > cd docs && make html

(or latexpdf if you want a latex version - type `make` to see all the options). The documentation will be dumped under build/<format>. For HTML, if you point a browser to `build/html/index.html`, you should see a basic sphinx site with the documentation for `borehole_analysis`
