Building and installing `pysiss`
================================

.. _installation:

Installing via pip
------------------

The easiest way to get pysiss is to install the `version hosted on PyPI <https://pypi.python.org/pypi/pysiss/0.0.2>`_ via pip.

You will have to have the standard `numpy <http://numpy.org>`_/`scipy <http://scipy.org>`_/`matplotlib <http://matplotlib.org>`_ stack. 

Installing the scientific Python stack can be a bit of a pain in the arse if you're not used to it, especially on non-Linux systems, so you might like to check out `Anaconda <https://store.continuum.io/cshop/anaconda/>`_, `Python(x, y) <https://code.google.com/p/pythonxy/>`_ or `Pyzo <http://www.pyzo.org/>`_ if you want an easy install experience. If you're on Linux then usually the package manager version is worth a try first.

Then pysiss should be installable using pip

    pip install pysiss

This should pull all the dependencies for pysiss automatically. Depending on where you're trying to install the library, you may need administrator priviledges to install the library. If you don't have adminstrator rights for your system, then you can install it locally using

    pip install pysiss --user

which will install it under your home directory (usually somewhere like :file:`~/.local/lib/`).

Building and installing pysiss from source
------------------------------------------

`pysiss` has quite a few dependencies, most of which come from the numpy/scipy/matplotlib ecosystem. See the instructions above for getting access to this stack.

Once you've got the numpy/scipy/matplotlib stack installed, you need:

- `pandas <http://pandas.pydata.org>'_ for data munging, 
- `shapely <http://toblerity.org/shapely/>'_, which lets you deal with vector GIS data nicely
- `owslib <https://pypi.python.org/pypi/OWSLib/>'_ for calls to SISS services, and
- `simplejson <https://pypi.python.org/pypi/simplejson>'_ and `lxml <http://lxml.de>'_ for dealing with JSON, XML and text data for some of the queries.

If you want to run the examples, you might also want to consider

- `ipython <http://ipython.org>'_ to run the iPython notebook examples
- `folium <http://folium.readthedocs.org/en/latest/>'_ a wrapper for leaflet.js maps
- `mpld3 <http://mpld3.github.io/>'_ a matplotlib to D3 wrapper

These are optional but pretty kick-arse libraries which you should install and play with anyway.

If you've installed all the libraries above, all you should need to do is enter the python directory, and execute

  python setup.py install

or

  python setup.py install --user

which should build and install pysiss for your system.

Unit tests
----------

To run the unit tests, just go to the base directory and execute

  python setup.py test

They only take a couple of seconds to run and should all pass unless I've screwed something up... The unit tests use the vanilla unittest framework, so should play nicely with your favourite testing framework should you prefer to use something else.

Building documentation
----------------------

You're currently reading some version of the documentation generated from the pysiss.borehole library. If you want to build your own version then you will need to have a version of `sphinx <http://sphinx.pocoo.org/>`_ installed -- you can check by doing the following at a terminal prompt:

  python -c 'import sphinx'

If that fails grab the latest version of and install it with::

  pip install Sphinx --upgrade

Now you are ready to build your docs, using make (or run the batch script make.bst if you're on Windows):

  cd docs && make html

(or :file:`latexpdf` if you want a LaTeX versionm, or :file:`epub` for ePub format - type :file:`make` to see all the options). The documentation will be dumped under :file:`build/<format>`. For HTML, if you point a browser to :file:`build/html/index.html`, you should see a basic sphinx site with the documentation for pysiss.borehole. For LaTeX you can open :file:`build/latex/pysiss.borehole.pdf` in your favourite PDF viewer to browse the documentation.

Contributing
------------

For a list of contributors, see `AUTHORS.md`.

We'd love to have more people use the library and contribute to it. If you've pulled this from the public repository on CSIRO install of Stash (`stash.csiro.au <https://stash.csiro.au/projects/DARDA/repos/pysiss/browse>`_), then you might like to check out the `mirrored repository on Github <https://github.com/pysiss/pysiss>`_ or `Bitbucket <https://bitbucket.org/pysiss/pysiss>` which should make it easier for non-CSIRO types to fork and hack away.

We like unit tests and documentation - feel free to contribute your own.

For more details, feel free to contact Jess: his email is jesse.robertson with CSIRO's domain (google it).

