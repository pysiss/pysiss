Introduction to pyboreholes
===========================

author: Jess Robertson, David Benn & Ben Caradoc-Davies, CSIRO Minerals Down Under

email: jesse.robertson with CSIRO's domain (google it)

date: Friday 16 May, 2014

This is a python module to carry out some basic analysis of borehole data. Warning - this library is in a pre-pre-pre-alpha state and could change without warning.

Building and installing pyboreholes
-----------------------------------

`pyboreholes` has a few dependencies, most of which come from the numpy/scipy/matplotlib ecosystem. You will have to have [numpy][1] and [pandas][3] at a minimum, while you will need [scipy][2] to use the pyboreholes.analysis module, [matplotlib][4] for the plotting module, and [owslib][12] for OWS calls in the NVCL importer. You can install all of these (with the exception of the cwavelets library, see below) in a single line with the following command:

    pip install numpy scipy matplotlib pandas owslib

If your system complains that it can't find pip, then try easy_install install ... instead.

If the command line is a bit scary than most of these libraries should come for free with a standard scientific Python stack these days, check out [Enthought Canopy][6], [Anaconda][7], [Python(x, y)][8] or [Pyzo][11] if you want an easy install experience.

If you've installed all the libraries above, all you should need to do is enter the python directory, and execute

    python setup.py install

which should build and install the Python bindings for your system. Depending on where you're trying to install the library, you may need administrator priviledges to install the library. If you don't have adminstrator rights for your system, then you can install it locally using

    python setup.py install --user

which will install it under your home directory. You can install only part of the library if you wish (or if you're missing libraries), just run

    python setup.py --help

for more details.

To run the unit tests, just go to the base directory and execute

	python -m unittest tests

They only take a couple of seconds to run and should all pass unless I've screwed something up...

Building documentation
----------------------

You're currently reading some version of the documentation generated from the pyboreholes library. If you want to build your own version then you will need to have a version of [sphinx][10] installed -- you can check by doing the following at a terminal prompt:

  python -c 'import sphinx'

If that fails grab the latest version of and install it with::

  easy_install -U Sphinx

Now you are ready to build your docs, using make (or run the batch script make.bst if you're on Windows):

  cd docs && make html

(or latexpdf if you want a LaTeX versionm, or epub for ePub format - type make to see all the options). The documentation will be dumped under build/<format>. For HTML, if you point a browser to docs/build/html/index.html, you should see a basic sphinx site with the documentation for pyboreholes. For LaTeX you can open docs/build/latex/pyboreholes.pdf in your favourite PDF viewer to browse the documentation.

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