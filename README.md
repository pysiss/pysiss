Introduction to pysiss
======================

This is a python module designed to make it easy to perform analysis based on SISS services (including boreholes & geological measurements, raster and vector map data, and vocabularies) within Python using your favourite Python libraries. 

**Warning** - this library is in a pre-pre-pre-alpha state and could change without warning.

For a list of contributors, see `contributors.md`.

Building and installing pysiss
------------------------------

`pysiss` has quite a few dependencies, most of which come from the numpy/scipy/matplotlib ecosystem. 

You will have to have the standard [numpy][1]/[scipy][2] stack at a minimum, while you will need [matplotlib][4] for the plotting modules. Installing the scientific Python stack can be a bit of a pain in the arse if you're not used to it, especially on non-Linux systems, so you might like to check out [Enthought Canopy][6], [Anaconda][7], [Python(x, y)][8] or [Pyzo][11] if you want an easy install experience.

Once you've got the numpy/scipy/matplotlib stack installed, you need:

- [pandas][3] for data munging, 
- [owslib][12] for calls to SISS services,
- [simplejson](https://pypi.python.org/pypi/simplejson), [lxml](http://lxml.de) and [BeautifulSoup](http://www.crummy.com/software/BeautifulSoup/) for dealing with JSON, XML and text data for some of the queries.

If you want to run the examples, you might also want to consider

- [folium](http://folium.readthedocs.org/en/latest/) a python wrapper for leaflet.js maps


If you've installed all the libraries above, all you should need to do is enter the python directory, and execute

    python setup.py install

which should build and install the Python bindings for your system. Depending on where you're trying to install the library, you may need administrator priviledges to install the library. If you don't have adminstrator rights for your system, then you can install it locally using

    python setup.py install --user

which will install it under your home directory. You can install only part of the library if you wish (or if you're missing libraries), just run

    python setup.py --help

for more details.

To run the unit tests, just go to the base directory and execute

	python setup.py test

They only take a couple of seconds to run and should all pass unless I've screwed something up... The unit tests use the vanilla unittest framework, so should play nicely with your favourite testing framework should you prefer to use something else.

Building documentation
----------------------

You're currently reading some version of the documentation generated from the pysiss library. If you want to build your own version then you will need to have a version of [sphinx][10] installed -- you can check by doing the following at a terminal prompt:

    python -c 'import sphinx'

If that fails grab the latest version of and install it with::

    easy_install -U Sphinx

Now you are ready to build your docs, using make (or run the batch script make.bst if you're on Windows):

    cd docs && make html

(or latexpdf if you want a LaTeX versionm, or epub for ePub format - type make to see all the options). The documentation will be dumped under build/<format>. For HTML, if you point a browser to docs/build/html/index.html, you should see a basic sphinx site with the documentation for pysiss. For LaTeX you can open docs/build/latex/pysiss.pdf in your favourite PDF viewer to browse the documentation.

Contributing
------------

We'd love to have more people use the library and contribute to it. If you've pulled this from the public repository on CSIRO install of Stash ([stash.csiro.au][9]), then you might like to check out the [mirrored repository on Bitbucket][14] which should make it easier for non-CSIRO types to fork and hack away.

We like unit tests and documentation - feel free to contribute your own.

For more details, feel free to contact Jess: his email is jesse.robertson with CSIRO's domain (google it).

[1]: http://numpy.org
[2]: http://scipy.org
[3]: http://pandas.pydata.org
[4]: http://matplotlib.org
[6]: https://www.enthought.com/products/canopy/
[7]: https://store.continuum.io/cshop/anaconda/
[8]: https://code.google.com/p/pythonxy/
[9]: https://stash.csiro.au/projects/DARDA
[10]: http://sphinx.pocoo.org/
[11]: http://www.pyzo.org/
[12]: https://pypi.python.org/pypi/OWSLib/
[14]: http://bitbucket.org/pysiss/pysiss