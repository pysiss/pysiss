Introduction to pySISS
======================

PySISS makes it easy to perform analysis on geological datasets (including boreholes & geological measurements, raster and vector map data, and vocabularies) within Python, using data slurped from OGC-compliant webservices.

Our aim is to provide a stack of Python libraries plus a bunch of glue and parsing code so that you can get your sticky hands on the actual data quickly, without having to worry about OGC APIs and GeoSciML semantics.

This means we rely pretty heavily on a lot of excellent Python libraries (e.g. [pandas](http://pandas.pydata.org), [shapely](http://toblerity.org/shapely/manual.html), [rasterio](http://github.com/mapbox/rasterio) and [lxml](http://lxml.de)) to provide the native Python objects and metadata support at the other end. But it also means that getting some data is as simple as:

```python
from pysiss.webservices import ogc

# Set up an OGC coverage service endpoint
wcs = ogc.CoverageService('http://someURL')

# Get a raster dataset over some bounding box from the first layer
# available on the server
covg = wcs.get_coverage(ident=wcs.layers[0],
                        bounds=some_bounding_box)

# Show the pretty data...
covg.show()
```

**Where does the name come from?**

SISS stands for the [Spatial Information Services Stack](https://www.seegrid.csiro.au/wiki/Siss/WebHome), which is a suite of tools for spatial data interoperability using the OGC standards, GeoServer, FullMoon and GeoNetwork. It deals with map, feature and raster data, as well as providing vocabulary services to handle semantic data, and registries to track and catalogue available data services. Many Australian government agencies use SISS to push out geospatial datasets over OGC-compliant webservices.

PySISS is just a Python client which sits on top of the hard work done by the agencies releasing the data.

**Where can I get some data to try this out?**

A good starting point is the [AuScope portal](http://portal.auscope.org) which will let you discover and visualise some of the datasets available. The data from the examples below come from exactly the same endpoints. You can find the enpoint url by clicking on the little binary icon beside each layer.

**Can I use this freely?**

Yep - pySISS is released under the CSIRO BSD/MIT license, whose terms are available in the `LICENSE.md` file.

**Warning** - this library is in an alpha state and could change without warning.

[![Build Status](https://travis-ci.org/pysiss/pysiss.svg?branch=develop)](https://travis-ci.org/pysiss/pysiss)
[![Coverage Status](https://coveralls.io/repos/pysiss/pysiss/badge.svg?branch=develop)](https://coveralls.io/r/pysiss/pysiss?branch=develop)
[![Code Health](https://landscape.io/github/pysiss/pysiss/develop/landscape.svg)](https://landscape.io/github/pysiss/pysiss/develop)

Examples
--------

**Getting borehole data from the NVCL**

The [National Virtual Core Library (NVCL)](http://www.auscope.org.au/site/nvcl.php) is a collaboration between the Australian state geological surveys, Geoscience Australia, CSIRO and AuScope which provides drillcore information via webservices. An example borehole

```python
from pysiss.webservices import nvcl

gswa = nvcl.NVCLImporter('gswa')  # Use nvcl.NVCLEndpointRegistry to see valid keys
borehole = gswa.get_borehole('PDP2C')
print(borehole)
```

prints

```
Borehole PDP2C at origin position latitude -21.177643 degree, longitude 119.429516 degree, elevation 0.0 meter, PropertyType origin position elevation: long name is "origin position elevation", units are 1 meter contains 1 datasets & 0 features
SDs: PointDataset PDP2C: with 6057 depths and 34 properties
Borehole details: {'driller': BoreholeDetail(name='driller', values='Mount Magnet Drilling', property_type=None), 'inclination type': BoreholeDetail(name='inclination type', values='inclined down', property_type=None), 'drilling method': BoreholeDetail(name='drilling method', values='diamond core', property_type=None), 'cored interval': BoreholeDetail(name='cored interval', values={'lower corner': <Quantity(69.3, 'meter')>, 'upper corner': <Quantity(114.6, 'meter')>}, property_type=PropertyType envelope: long name is "cored interval envelope", units are 1 meter), 'shape': BoreholeDetail(name='shape', values=[-21.1776, 119.43, -21.1775, 119.43], property_type=None), 'start point': BoreholeDetail(name='start point', values='natural ground surface', property_type=None), 'date of drilling': BoreholeDetail(name='date of drilling', values=datetime.datetime(2004, 1, 1, 0, 0), property_type=None)}
```

Boreholes have their own domains defining interval or point samples, and can also show imagery. For more on this see the docs.

**Getting some ASTER data and munging it up with geological data**

The Advanced Spaceborne Thermal Emission and Reflection Radiometer (ASTER) is an imaging instrument onboard Terra. ASTER supplies high resolution visible, thermal and infrared spectral imagery. Geoscience Australia makes some data products derived from this data available via WCS. There's a seperate WCS endpoint for each ASTER product. We're going to grab a few of the compositional products. Here I've pulled the WCS URL from the AuScope portal.

```python
from pysiss.webservices import ogc

# Products to pull
aster_products = [
    'AlOH_group_composition',
    'Ferric_oxide_composition',
    'MgOH_group_composition'
]
bounds = (119.5, -20.6, 119.6, -20.5)
wcsurl = 'http://aster.nci.org.au/thredds/wcs/aster/vnir/Aus_Mainland/Aus_Mainland_{0}_reprojected.nc4'

coverages = {}
for product in aster_products:
    url = wcsurl.format(product)
    wcs = ogc.CoverageService(url)
    coverages[product] = wcs.get_coverage(ident=wcs.layers[0],
                                          bounds=bounds)
```

...and we can plot this data as an image.

Installing
----------

**Using Anaconda/binstar**

The easiset way to get pysiss is to install ContinuumIO's [Anaconda](http://continuum.io/downloads), and install from our prebuild binaries. Once Anaconda is installed, just run

	conda install binstar
	conda config --add channels jesserobertson
	conda install pysiss

and everything should just happen like magic. Optionally, you can create a seperate conda environment for pysiss by doing the following

	conda create -n pysiss python=2.7 pysiss
	source activate pysiss

which keeps everything isolated from other conda packages you might have.

**Using pip**

An alternative way to get pysiss is to install the [version hosted on PyPI](https://pypi.python.org/pypi/pysiss/) via pip. This isn't quite as nice as installing via conda as you have to handle the non-Python library dependencies yourself.

You will have to have the standard [numpy](http://numpy.org)/[scipy](http://scipy.org)/[matplotlib](http://matplotlib.org) stack. You also need to have the GDAL libraries and Python bindings installed.

_For more details on installing these libraries for Windows, Mac and Linux please see INSTALL.md_

Once the dependencies are installed pysiss and all its Python dependencies should be installable using pip

    pip install pysiss

This should pull all the dependencies for pysiss automatically. Depending on where you're trying to install the library, you may need administrator priviledges to install the library. If you don't have adminstrator rights for your system, then you can install it locally using

    pip install pysiss --user

which will install it under your home directory (usually somewhere like `~/.local/lib/`).

**From source**

`pysiss` has quite a few dependencies, most of which come from the numpy/scipy/matplotlib ecosystem. You also need to have the GDAL libraries and Python bindings installed. See the instructions in INSTALL.md for getting access to this stack.

*Installing PySISS dependencies*

Once you've got the numpy/scipy/matplotlib stack plus the GDAL libraries installed, you need:

- [pandas](http://pandas.pydata.org) for data munging,
- [shapely](http://toblerity.org/shapely/), which lets you deal with vector GIS data nicely
- [lxml](http://lxml.de) for dealing with XML and text data for some of the queries.

If you want to run the examples, you might also want to consider

- [ipython](http://ipython.org) to run the iPython notebook examples
- [folium](http://folium.readthedocs.org/en/latest/) a wrapper for leaflet.js maps
- [mpld3](http://mpld3.github.io/) a matplotlib to D3 wrapper

These are optional but pretty kick-arse libraries which you should install and play with anyway.

*Building PySISS*

If you've installed all the libraries above, all you should need to do is enter the python directory, and execute

    python setup.py install

or

    python setup.py install --user

which should build and install pysiss for your system.

*Running unit tests*

To run the unit tests, just go to the base directory and execute

	python setup.py update_mocks test

They only take a couple of seconds to run and should all pass unless I've screwed something up... The unit tests use the vanilla unittest framework, so should play nicely with your favourite testing framework should you prefer to use something else.

The update_mocks command pulls down some data from the network to use in the tests. You should only need to run it once as this gets cached so that you can run the tests later without a network connection.

*Building documentation*

If you want to build your own version then you will need to have a version of [sphinx](http://sphinx.pocoo.org/) installed -- you can check by doing the following at a terminal prompt:

    python -c 'import sphinx'

If that fails grab the latest version of and install it with::

    pip install Sphinx --upgrade

Now you are ready to build your docs, using make (or run the batch script make.bst if you're on Windows):

    cd docs && make html

(or latexpdf if you want a LaTeX versionm, or epub for ePub format - type make to see all the options). The documentation will be dumped under build/{format}. For HTML, if you point a browser to docs/build/html/index.html, you should see a basic sphinx site with the documentation for pysiss. For LaTeX you can open docs/build/latex/pysiss.pdf in your favourite PDF viewer to browse the documentation.

I can't promise the documentation is very up to date at the moment though...

Contributing
------------

For a list of contributors, see `AUTHORS.md`.

We'd love to have more people use the library and contribute to it. If you've pulled this from the public repository on CSIRO install of Stash ([stash.csiro.au](https://stash.csiro.au/projects/DARDA/repos/pysiss/browse)), then you might like to check out the [mirrored repository on Github](https://github.com/pysiss/pysiss) or [Bitbucket](https://bitbucket.org/pysiss/pysiss) which should make it easier for non-CSIRO types to fork and hack away.

For more details, feel free to contact Jess: his email is jesse.robertson with CSIRO's domain (google it).
