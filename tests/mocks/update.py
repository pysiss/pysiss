#!/usr/bin/env python
""" file: update_mocks.py
	author: Jess Robertson
			CSIRO Mineral Resources Research Flagship
	date:   January 2015

	description: Update the mock files
"""

from resource import Resource
import simplejson
import os
import logging
import logging.config

MOCK_CONFIG_FILE = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    'mocks.json')


def main():
    # Set up logging
    from pysiss._log_config import LOG_CONFIG
    logging.config.dictConfig(LOG_CONFIG)
    logger = logging.getLogger('pysiss')

	# Load endpoint data from config file
    with open(MOCK_CONFIG_FILE, 'rb') as fhandle:
        mocks = simplejson.load(fhandle)

    # Make Resource objects, and update them
    for idx, (name, mock) in enumerate(mocks.items()):
        logger.info('Updating {0} from {1}'.format(name, mock['url']))
        res = Resource(**mock)
        result = res.update()
        logger.info('Finished updating\n')


if __name__ == '__main__':
	main()
