#!/usr/bin/env python
""" file: update_mocks.py
	author: Jess Robertson
			CSIRO Mineral Resources Research Flagship
	date:   January 2015

	description: Update the mock files
"""

from __future__ import print_function, division

from .resource import Resource

import json
import os

import logging
import logging.config
from pysiss._log_config import LOG_CONFIG
logging.config.dictConfig(LOG_CONFIG)
LOGGER = logging.getLogger('pysiss')

from setuptools import Command

MOCK_CONFIG_FILE = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    'mocks.json')


def update_mocks():
	# Load endpoint data from config file
    with open(MOCK_CONFIG_FILE, 'rb') as fhandle:
        mocks = json.load(fhandle)

    # Make Resource objects, and update them
    for idx, (mock) in enumerate(mocks):
        LOGGER.info('Updating from {0}'.format(mock['url']))
        res = Resource(**mock)
        result = res.update()
        LOGGER.info('Finished updating\n')


class UpdateMocks(Command):

    """ Setuptools command to update mock URL resources for tests

        to execute run python setup.py update_mocks
    """

    description = "update mock resource files for test suite from network"
    user_options = []
    boolean_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        update_mocks()
        LOGGER.info("Updated test data")


if __name__ == '__main__':
	update_mocs()
