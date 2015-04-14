""" file: request.py
	author: Jess Robertson
			CSIRO Mineral Resources Research Flagship
	date:   January 2015

	description: Update the mock files
"""

from __future__ import print_function, division

import os
import httmock
import requests
import hashlib

from . import PRINT_INTERCEPTIONS


class Resource(object):

    """ A mock resource which returns a cached file rather than a
        proper network call.
    """

    HEADERS = {'content-type': 'text'}

    def __init__(self, url, method, params, data=None):
        self.data = data
        self.method = method
        self.params = params
        self.url = url

        # Make a file path to stash the cached response
        self.folder = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            'cache', url.lstrip('https://'))

        # We're just going to generate a hash based on the sorted parameter
        # characters
        query_string = \
            '&'.join(('{0}={1}'.format(*it) for it in self.params.items()))
        self.filename = hashlib.md5(
            ''.join(sorted(query_string)).encode('utf-8')).hexdigest()
        self.file_path = os.path.join(self.folder, self.filename)

        # Make request object to return
        self.session = None
        self.request = requests.Request(url=self.url, method=self.method,
                                        params=self.params, data=self.data)

    def response(self):
        """ Return a response object
        """
        try:
            with open(self.file_path, 'r') as fhandle:
                content = fhandle.read()
            return httmock.response(200, content, self.HEADERS, None,
                                    5, self.request)
        except IOError:
            print(
                "Warning: Missing a mock file {0} ".format(self.file_path)
                + "- have you updated the mock resources by running "
                + "`python setup.py update_mocks` recently?")
            return httmock.response(404, {}, self.HEADERS, None,
                                    5, self.request)

    def update(self):
        """ Update the cached response on file
        """
        # Check that we have a folder available
        if not os.path.exists(self.folder):
            os.makedirs(self.folder)

        # Get response from server
        if self.session is None:
            self.session = requests.Session()
        response = self.session.send(self.request.prepare())
        if response.ok:
            print("Writing to {0}".format(self.file_path))
            with open(self.file_path, 'wb') as fhandle:
                fhandle.write(response.content)
        else:
            print(("Couldn't hit {0}, server returned {1}. "
                   "Leaving {2} alone.").format(response.url,
                                                response.status_code,
                                                self.file_path))


@httmock.all_requests
def mock_resource(url, request):
    """ Redirect requests calls to the relevant mock'd Resource object
    """
    if PRINT_INTERCEPTIONS:
        print("Intercepted HTTP request: {0}".format(url))

    # Pick out a few things to pass to the Resource class
    try:
        baseurl = url.netloc + url.path
        if url.query != '':
            params = url.query.replace('%3A', ':')
            params = dict([st.split('=') for st in params.split('&')])
        else:
            params = {}
    except (IndexError, ValueError):
        baseurl, params = url.netloc + url.path, {}
    try:
        data = request.data
    except AttributeError:
        data = None

    # Generate the resource object
    res = Resource(url=baseurl, method=request.method,
                   params=params, data=data)
    if PRINT_INTERCEPTIONS:
        print("Looking for file {0}".format(res.filename))
    return res.response()
