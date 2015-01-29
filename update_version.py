""" file: update_version.py
    author: Jess Robertson
            CSIRO Minerals Resources Flagship
    date:   January 2015

    description: Tool to update the version number using `git describe`
"""

import subprocess
import os
from setuptools import Command
import re

VERSION_PY_TEMPLATE = """\
# This file is originally generated from Git information by running 'setup.py
# update_version'. Distribution tarballs contain a pre-generated copy of this
# file.
__version__ = '{0}'
"""


def update_version():
    # Query git for the current description
    if not os.path.isdir(".git"):
        print "This does not appear to be a Git repository."
        return
    try:
        p = subprocess.Popen(["git", "describe", "--dirty", "--always"],
                             stdout=subprocess.PIPE)
        stdout = p.communicate()[0]
        if p.returncode != 0:
            raise EnvironmentError
        else:
            ver = stdout.strip()
    except EnvironmentError:
        print "Unable to run git, leaving pysiss/_version.py alone"
        return

    # Write to file
    with open('pysiss/_version.py', 'wb') as fhandle:
        fhandle.write(VERSION_PY_TEMPLATE.format(ver))


def get_version():
    """ Get the currently set version
    """
    try:
        with open("pysiss/_version.py") as fhandle:
            for line in (f for f in fhandle if not f.startswith('#')):
                return re.match("__version__ = '([^']+)'", line).group(1)
    except EnvironmentError:
        print "Can't find pysiss/_version.py - what's the version, doc?"
        return 'unknown'


class Version(Command):

    """ Setuptools command to update version

        to execute run python setup.py version
    """

    description = "update _version.py from Git repo"
    user_options = []
    boolean_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        update_version()
        print "Version is now", get_version()

if __name__ == '__main__':
    update_version()
