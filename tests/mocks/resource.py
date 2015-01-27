""" file: request.py
	author: Jess Robertson
			CSIRO Mineral Resources Research Flagship
	date:   January 2015

	description: Update the mock files
"""

import os
import httmock
import requests

class Resource(object):

    """ A mock resource which returns a cached file rather than a
        proper network call.
    """

    HEADERS = {'content-type': 'application/json'}

    def __init__(self, url, method, params, data=None):
        self.data = data
        self.method = method
        self.params = params
        self.url = url

        # Make a file path to stash the cached response
        self.folder = os.path.join(
            os.path.dirname(os.path.realpath(__file__))
            'cache', url.lstrip('https://'))
        self.file_path = os.path.join(
            self.folder,
            '?' + '&'.join(
                ('{0}={1}'.format(*it) for it in self.params.items())))

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
            return httmock.response(404, {}, self.HEADERS, None,
                                    5, self.request)

    def update(self):
        """ Update the cached response on file
        """
        # Check that we have a folder available
        if not os.path.exists(self.folder):
            os.mkdir(self.folder)

        # Get response from server
        if self.session is None:
            self.session = requests.Session()
        response = self.session.send(self.request.prepare())
        with open(self.file_path, 'wb') as fhandle:
            fhandle.write(response.content)


@all_requests
def mock_resource(url, request):
    """ Redirect requests calls to the relevant mock'd Resource object
    """
    # Pick out a few things to pass to the Resource class
    try:
        baseurl, params = request.url.split('?')
        params = dict([st.split('=') for st in params.split('&')])
    except IndexError:
        baseurl, params = url, None
    try:
        data = request.data
    except AttributeError:
        data = None

    # Generate the resource object
    res = Resource(url=baseurl, method=request.method, params=params, data=data)
    return res.response()
