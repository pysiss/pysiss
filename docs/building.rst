Building and installing `pysiss.borehole`
=====================================

.. _installation:

Installing dependencies
-----------------------

`pysiss.borehole` has a few dependencies, most of which come from the numpy/scipy/matplotlib ecosystem. You will have to have `numpy <http://numpy.org>`_ at a minimum, while you will need `scipy <http://scipy.org>`_ and `cwavelets <https://stash.csiro.au/projects/DARDA/repos/cwavelets/browse>`_ to use the pysiss.borehole.analysis module, `matplotlib <http://matplotlib.org>`_ for the plotting module, and `pywavelets <http://www.pybytes.com/pywavelets/>`_ to have access to the SpectralDomain class. You can install all of these (with the exception of the `cwavelets` library, see below) in a single line with the following command:

    pip install numpy scipy matplotlib pywavelets

If your system complains that it can't find `pip`, then try `easy_install install ...` instead. If you're running some version of Linux then there are probably packages for all of these - see your package manager for more info.

If the command line is a bit scary than most of these libraries should come for free with a standard scientific Python stack these days, check out `Enthought Canopy <https://www.enthought.com/products/canopy/>`_, `Anaconda <https://store.continuum.io/cshop/anaconda/>`_, `Python(x, y) <https://code.google.com/p/pythonxy/> or `Pyzo <http://www.pyzo.org/>`_ if you want an easy install experience.

Build and install `cwavelets`
-----------------------------

The `cwavelets` library is currently being developed internally in CSIRO - if you have access to this repository through the `DARDA Stash site <https://stash.csiro.au/projects/DARDA>`_ then you've probably got access to this library as well. You'll have to download and install the code following the instructions on that page (many of the dependencies are the same as for here). This is an optional install but you won't have access to the `WaveletDomain` class if you don't have this available on your system.

Build and install the library
-----------------------------

If you've installed all the libraries above, all you should need to do is enter the python directory, and execute

    python setup.py install

which should build and install the Python bindings for your system. Depending on where you're trying to install the library, you may need administrator priviledges to install the library. You can install only part of the library if you wish (or if you're missing libraries), just run

    python setup.py --help

for more details.

.. _documentation:

Building documentation
----------------------

You're currently reading some version of the documentation generated from the pysiss.borehole library. If you want to build your own version then you will need to have a version of `sphinx <http://sphinx.pocoo.org/>`_ installed -- you can check by doing the following at a terminal prompt:

  python -c 'import sphinx'

If that fails grab the latest version of and install it with::

  easy_install -U Sphinx

Now you are ready to build your docs, using make (or run the batch script `make.bst` if you're on Windows):

  cd docs && make html

(or :file:`latexpdf` if you want a LaTeX versionm, or :file:`epub` for ePub format - type :file:`make` to see all the options). The documentation will be dumped under :file:`build/<format>`. For HTML, if you point a browser to :file:`build/html/index.html`, you should see a basic sphinx site with the documentation for pysiss.borehole. For LaTeX you can open :file:`build/latex/pysiss.borehole.pdf` in your favourite PDF viewer to browse the documentation.