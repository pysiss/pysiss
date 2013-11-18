Building and installing `pyboreholes`
=====================================

.. _installation:

All you should need to do is enter the python directory, and execute::

    python setup.py install

which should build and install the Python bindings for your system. Depending on your system, you may need adminstrator priviledges to run the install command.

.. _documentation

Building documentation
----------------------

You're currently reading some version of the documentation generated from the pyboreholes library. If you want to build your own version then you will need to have a version of `sphinx <http://sphinx.pocoo.org/>`_ installed -- you can check by doing the following at a terminal prompt::

  python -c 'import sphinx'

If that fails grab the latest version of and install it with::

  sudo easy_install -U Sphinx

Now you are ready to build your docs, using make (or run the batch script :file:`make.bst` if you're on Windows)::

  cd docs && make html

(or :file:`latexpdf` if you want a LaTeX versionm, or :file:`epub` for ePub format - type :file:`make` to see all the options). The documentation will be dumped under :file:`build/<format>`. For HTML, if you point a browser to :file:`build/html/index.html`, you should see a basic sphinx site with the documentation for pyboreholes. For LaTeX you can open :file:`build/latex/pyboreholes.pdf` in your favourite PDF viewer to browse the documentation.