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

MOCK_CONFIG_FILE = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    'mocks.json')


def main():
	# Load endpoint data from config file
    with open(MOCK_CONFIG_FILE, 'rb') as fhandle:
        mocks = simplejson.load(fhandle)

    # Make Resource objects, and update them
    for idx, (name, mock) in enumerate(mocks.items()):
        print '{1}: Updating {0}'.format(name, idx + 1)
        print '   Hitting {0}...'.format(mock['url']),
        res = Resource(**mock)
        res.update()
        print 'done\n'


if __name__ == '__main__':
	main()
