""" file: service_mapping.py
    author: Jess Robertson
            CSIRO Mineral Resources Flagship
    date:   Monday February 2, 2015

    description: Utilities to describe service mapping from values to the
        correct version of the OGC Webservice API.
"""

from __future__ import print_function, division

from ...metadata import Metadata
from ...utilities import accumulator

import json
import pkg_resources
from lxml import etree
import requests
import io


class OGCQueryString(accumulator):

    """ Class providing an OGC query string, allows repeated keys
    """

    def __init__(self, *args, **kwargs):
        super(OGCQueryString, self).__init__(*args, **kwargs)

    def __str__(self):
        """ Print out query string
        """
        result = '?'
        for key, values in self._dict.items():
            if not (result.endswith('&') or result.endswith('?')):
                result += '&'
            result += '&'.join(['{0}={1}'.format(key, v) for v in values])
        return result

    def __repr__(self):
        return str(self)


class OGCService(object):

    """ Provides a uniform interface to the variety of APIs published
        by the OGC
    """

    def __init__(self, endpoint, service_type):
        super(OGCService, self).__init__()

        # Sort out endpoint
        self.ident = self.endpoint = endpoint.split('?')[0]
        self.service_type = service_type

        # Start a requests session
        self.session = requests.Session()

        # Make a getCapabilities request to determine version
        query = ('service={0}'
                 '&request=getcapabilities'
                 '&version=1.1.0').format(self.service_type.lower())
        response = self.session.get(self.endpoint + '?' + query)
        response.raise_for_status()
        self.capabilities = Metadata(response.content)
        self.version = self.capabilities.xpath('@version')[0]

        # Load in mappings dynamically, hook into accumulator to allow
        # repeated keys (although that's not 'proper' JSON we allow it
        # to be able to construct OGC2.0 requests)
        version_str = self.version.replace('.', '_')
        fname = pkg_resources.resource_filename(
            'pysiss.webservices.ogc',
            'interfaces/{0}/{1}/parameters.json'.format(service_type,
                                                        version_str))
        with open(fname) as fhandle:
            self.parameters = json.load(fhandle,
                                        object_pairs_hook=accumulator)

    def request(self, request, method='get', send=True, **kwargs):
        """ Put together a PreparedRequest object to make the API call
        """
        # There might be a namespace associated with the request, strip it
        request = request.split('}')[-1]
        method = method.split('}')[-1]

        # Check that we actually know what to do
        allowed_requests = set(self.parameters.keys())
        allowed_methods = {'get', 'post'}
        if request not in allowed_requests:
            raise ValueError('Unknown OGC request {0}, allowed values'
                             ' are {1}'.format(request, allowed_requests))
        if method not in allowed_methods:
            raise ValueError('Unknown HTTP method {0}, allowed values'
                             ' are {1}'.format(method, allowed_methods))

        # Palm off the construction to the appropriate method
        if method == 'get':
            request = self.make_get_request(request, **kwargs)
        elif method == 'post':
            request = self.make_post_request(request, **kwargs)

        if send:
            response = self.session.send(request)
            response.raise_for_status()  # Raises an exception on 4/500 codes
            return response
        else:
            return request

    def make_get_request(self, request, **kwargs):
        """ Construct a get request for an API call
        """
        # Function to get a single parameter
        def _get_value(param):
            "Parse a single parameter"
            # Deal with multiple options
            if isinstance(param, list):
                # Loop through options until we find one that works
                values = []
                for value in param:
                    try:
                        value = _get_value(value)
                        values.append(value)
                    except KeyError:
                        continue
                value = '&'.join(values)

            elif isinstance(param, accumulator):
                template = param['string']
                inputs = {k: v
                          for k, v in param.items()
                          if k != 'string'}
                for key, value in inputs.items():
                    try:
                        if value.startswith('@'):
                            inputs[key] = kwargs[value.lstrip('@')]
                    except AttributeError:
                        continue

                value = template.format(**inputs)

            else:
                value = (kwargs[param.lstrip('@')]
                         if param.startswith('@') else param)

            return value

        # Construct dictionary of parameters.
        parameter_dict = OGCQueryString(self.parameters[request])
        for key, param in list(parameter_dict.items()):
            if key.startswith('?'):
                # We have an optional key, check whether values have been
                # specified already
                try:
                    value = _get_value(param)
                    if value:
                        parameter_dict[key.lstrip('?')] = value
                except KeyError:
                    # We're missing something, so just delete the key
                    continue

            else:
                # We have a required key, better have a value for this or we
                # need to toss our toys out of the cot
                try:
                    parameter_dict.replace(key, _get_value(param))
                except KeyError:
                    raise KeyError(
                        'Missing parameter {0} required'.format(param))

        # Remove placeholders
        for key in list(parameter_dict.keys()):
            if key.startswith('?'):
                del parameter_dict[key]

        # Make request and return
        query_string = str(parameter_dict)
        request = requests.Request('GET', self.endpoint + '?' + query_string)
        return request.prepare()

    def make_post_request(self, request, **kwargs):
        """ Construct a post request for an API call
        """
        raise NotImplementedError('Post requests not working yet...')
