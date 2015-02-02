""" file: service_mapping.py
    author: Jess Robertson
            CSIRO Mineral Resources Flagship
    date:   Monday February 2, 2015

    description: Utilities to describe service mapping from values to the
        correct version of the OGC Webservice API.
"""

import simplejson
import pkg_resources
from copy import deepcopy


def _parse_parameters(parameters):
    """ Parse the parameter spec for the given request

        Asking for an unknown request will raise a KeyError
    """
    categories = {
        'required_key': [],
        'optional_key': [],
        'specified_value': {},
        'user_required_value': {},
        'user_optional_value': {}
    }
    links = []
    defaults = {}

    # Little function to parse a single value
    def _process_value(is_optional, value):
        # Values are supplied or specified (beginning with '@')
        is_user_value = value.startswith('@')
        if is_user_value and is_optional:
            categories['user_optional_value'].append(value.lstrip('@'))
        elif is_user_value and not is_optional:
            categories['user_required_value'].append(value.lstrip('@'))
        else:
            categories['specified_value'].append(value)

    # Sweep through and process everything
    for key, value in parameters.items():
        # Keys are either required or optional (begining with '?')
        is_optional = key.startswith('?')
        if is_optional:
            categories['optional_key'].append(key.lstrip('?'))
        else:
            categories['required_key'].append(key)

        if isinstance(value, list):
            # We have a list of values which must appear together
            map(lambda v: _process_value(is_optional, v),
                value)
            links.append(set(value))
            defaults[key] = [None] * len(value)
        elif isinstance(value, str):
            _process_value(is_optional, value)
            defaults[key] = None
        else:
            raise ValueError('Unknown value type {0}'.format(value))

    return categories, links, defaults


class OGCServiceMapping(object):

    """ Provides a uniform interface to the variety of APIs published
        by the OGC
    """

    def __init__(self, service, version, method='get'):
        super(OGCServiceMapping, self).__init__()
        self.service = service
        self.version = version

        # Load in mappings dynamically
        self.parameters = simplejson.load(
            pkg_resources.resource_stream(
                'pysiss.webservices.ogc',
                'interfaces/{0}/{1}/parameters.json'.format(service, version)))

    def request(self, request, method='get', **kwargs):
        """ Put together a PreparedRequest object to make the API call
        """
        # Chekc that we actually know what to do
        allowed_requests = self.parameters.keys()
        allowed_methods = ('get', 'post')
        if request not in allowed_requests:
            raise ValueError('Unknown OGC request {0}, allowed values'
                             ' are {1}'.format(request, allowed_requests))
        if method not in allowed_methods:
            raise ValueError('Unknown HTTP method {0}, allowed values'
                             ' are {1}'.format(method, allowed_methods))

        # Palm off the construction to the appropriate method
        if method == 'get':
            return self._get_request(request, **kwargs)
        elif method == 'post':
            return self._post_request(request, **kwargs)

    def _get_request(self, request, **kwargs):
        """ Construct a get request for an API call
        """
        # Get the request parameters
        categories, links = _parse_parameters(self.parameters[request])

        # Construct dictionary of parameters.
        parameter_dict = deepcopy(self.parameters.request)
        for key, param in parameter_dict.items():
            if key.startswith('?'):
                # We have an optional key, check whether values have been
                # specified already
                try:
                    if isinstance(param, list):
                        value = [kwargs[v] if v.startswith('@')
                                 else v for v in param]
                    else:
                        value = \
                            kwargs[param] if param.startswith('@') else param
                    parameter_dict[key.lstrip('?')] = value
                finally:
                    # We'll get here always - if things have been spec'd
                    # properly there will be a proper value available
                    # otherwise we didn't need this key anyway
                    del parameter_dict[key]

            else:
                # We have a required key, better have a value for this or we
                # need to toss our toys out of the cot
                try:
                    if isinstance(param, list):
                        value = [kwargs[v] for v in param]
                    else:
                        value = kwargs
                    parameter_dict[key] = value
                except KeyError:
                    raise KeyError('Missing parameter {0} required'.format(
                                    param))

        return params

    def _post_request(self, request, **kwargs):
        """ Construct a post request for an API call
        """
        raise NotImplementedError('Post requests not working yet...')


