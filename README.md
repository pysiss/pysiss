Introduction to pysiss
======================

We want to make it easy to perform geological data analysis based on SISS services (including boreholes & geological measurements, raster and vector map data, and vocabularies) within Python using your favourite Python libraries. 

This library is released under the CSIRO BSD/MIT license, whose terms are available in the `LICENSE.md` file. 

**Warning** - this library is in a pre-alpha state and could change without warning.

[![Build Status](https://travis-ci.org/pysiss/pysiss.svg?branch=develop)](https://travis-ci.org/pysiss/pysiss)
[![Coverage Status](https://coveralls.io/repos/pysiss/pysiss/badge.svg?branch=develop)](https://coveralls.io/r/pysiss/pysiss?branch=develop)
[![Code Health](https://landscape.io/github/pysiss/pysiss/develop.svg)](https://landscape.io/github/pysiss/pysiss/develop)

Installing via conda
--------------------

The easiset way to get pysiss is to install ContinuumIO's [Anaconda](http://continuum.io/downloads), and install from our prebuild binaries. Once Anaconda is installed, just run

	conda install binstar
	conda config --add channels jesserobertson
	conda install pysiss

and everything should just happen like magic. Optionally, you can create a seperate conda environment for pysiss by doing the following

	conda create -n pysiss python=2.7 pysiss
	source activate pysiss

which keeps everything isolated from other conda packages you might have.

Installing via pip
------------------

An alternative way to get pysiss is to install the [version hosted on PyPI](https://pypi.python.org/pypi/pysiss/) via pip. This isn't quite as nice as installing via conda as you have to handle the non-Python library dependencies yourself.

You will have to have the standard [numpy](http://numpy.org)/[scipy](http://scipy.org)/[matplotlib](http://matplotlib.org) stack. You also need to have the GDAL libraries and Python bindings installed.

_For more details on installing these libraries for Windows, Mac and Linux please see INSTALL.md_

Once the dependencies are installed pysiss and all its Python dependencies should be installable using pip

    pip install pysiss

This should pull all the dependencies for pysiss automatically. Depending on where you're trying to install the library, you may need administrator priviledges to install the library. If you don't have adminstrator rights for your system, then you can install it locally using

    pip install pysiss --user

which will install it under your home directory (usually somewhere like `~/.local/lib/`).

Building and installing pysiss from source
------------------------------------------

`pysiss` has quite a few dependencies, most of which come from the numpy/scipy/matplotlib ecosystem. You also need to have the GDAL libraries and Python bindings installed. See the instructions in INSTALL.md for getting access to this stack.

Once you've got the numpy/scipy/matplotlib stack plus the GDAL libraries installed, you need:

- [pandas](http://pandas.pydata.org) for data munging, 
- [shapely](http://toblerity.org/shapely/), which lets you deal with vector GIS data nicely
- [simplejson](https://pypi.python.org/pypi/simplejson) and [lxml](http://lxml.de) for dealing with JSON, XML and text data for some of the queries.

If you want to run the examples, you might also want to consider

- [ipython](http://ipython.org) to run the iPython notebook examples
- [folium](http://folium.readthedocs.org/en/latest/) a wrapper for leaflet.js maps
- [mpld3](http://mpld3.github.io/) a matplotlib to D3 wrapper

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

If you want to build your own version then you will need to have a version of [sphinx](http://sphinx.pocoo.org/) installed -- you can check by doing the following at a terminal prompt:

    python -c 'import sphinx'

If that fails grab the latest version of and install it with::

    pip install Sphinx --upgrade

Now you are ready to build your docs, using make (or run the batch script make.bst if you're on Windows):

    cd docs && make html

(or latexpdf if you want a LaTeX versionm, or epub for ePub format - type make to see all the options). The documentation will be dumped under build/<format>. For HTML, if you point a browser to docs/build/html/index.html, you should see a basic sphinx site with the documentation for pysiss. For LaTeX you can open docs/build/latex/pysiss.pdf in your favourite PDF viewer to browse the documentation.

Contributing
------------

For a list of contributors, see `AUTHORS.md`.

We'd love to have more people use the library and contribute to it. If you've pulled this from the public repository on CSIRO install of Stash ([stash.csiro.au](https://stash.csiro.au/projects/DARDA/repos/pysiss/browse)), then you might like to check out the [mirrored repository on Github](https://github.com/pysiss/pysiss) or [Bitbucket](https://bitbucket.org/pysiss/pysiss) which should make it easier for non-CSIRO types to fork and hack away.

We like unit tests and documentation - feel free to contribute your own.

For more details, feel free to contact Jess: his email is jesse.robertson with CSIRO's domain (google it).