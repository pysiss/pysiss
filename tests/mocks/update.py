#!/usr/bin/env python
""" file: update_mocks.py
	author: Jess Robertson
			CSIRO Mineral Resources Research Flagship
	date:   January 2015

	description: Update the mock files
"""

from resource import Resource
import simplejson

def main():
	# Load endpoint data from config file
    with open('mocks.json', 'rb') as fhandle:
        mocks = simplejson.load(fhandle)

    # Make Resource objects, and update them
    for mock in mocks.values():
        print 'Updating {0}'.format(mock['url'])
        res = Resource(**mock)
        res.update()

if __name__ == '__main__':
	main()
