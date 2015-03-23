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
from collections import defaultdict
from lxml.etree import QName

class accumulator(object):

    """ Class providing a dictionary where repeated entries to
        a key generate a list rather than overwriting
    """

    def __init__(self, *args, **kwargs):
        super(accumulator, self).__init__()
        self._dict = defaultdict(list)
        self.update(*args, **kwargs)

    def __str__(self):
        """ String representation
        """
        return 'acumulator(' + ', '.join(['{0}={1:s}'.format(*it)
                                          for it in self.items()])


    def update(self, *args, **kwargs):
        """ Update the accumulator with a new set of pairs, a dictionary
            or a set of keyword arguments
        """
        # Update using argument which may be dictionaries
        # or lists of key, value pairs
        if args:
            for arg in args:
                try:
                    for key, value in arg.items():
                        self[key] = value
                except AttributeError:
                    # We have a list of pairs
                    for key, value in arg:
                        self[key] = value

        # Update using keyword arguments
        if kwargs:
            for key, value in kwargs.items():
                self[key] = value

    def replace(self, key, value):
        """ Explicitly replace the current value of key with the given value
        """
        del self._dict[key]
        self[key] = value

    def __setitem__(self, key, value):
        """ Setting items adds them to a list of values, rather than
            overwriting
        """
        self._dict[key].append(value)

    def __getitem__(self, key):
        """ Return items from the dictionary
        """
        item = self._dict[key]
        if len(item) == 1:
            return item[0]
        else:
            return item

    def __delitem__(self, key):
        """ Remove an item from the dictionary
        """
        del self._dict[key]

    def keys(self):
        """ Return the keys from the dictionary
        """
        return self._dict.keys()

    def values(self):
        """ Return the values from the dictionary
        """
        return [v[0] if len(v) == 1 else v for v in self._dict.values()]

    def items(self):
        """ Return the items from the dictionary
        """
        return zip(self.keys(), self.values())


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


class OGCServiceMapping(object):

    """ Provides a uniform interface to the variety of APIs published
        by the OGC
    """

    def __init__(self, service, version, method='get'):
        super(OGCServiceMapping, self).__init__()
        self.service = service
        self.version = version

        # Load in mappings dynamically, hook into accumulator to allow
        # repeated keys (although that's not 'proper' JSON we allow it
        # to be able to construct OGC2.0 requests)
        self.parameters = simplejson.load(
            pkg_resources.resource_stream(
                'pysiss.webservices.ogc',
                'interfaces/{0}/{1}/parameters.json'.format(service, version)),
            object_pairs_hook=accumulator)

    def request(self, request, method='get', **kwargs):
        """ Put together a PreparedRequest object to make the API call
        """
        # There might be a namespace associated with the request, strip it
        request = request.split('}')[-1]
        method = method.split('}')[-1]

        # Check that we actually know what to do
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
            return self.make_get_request(request, **kwargs)
        elif method == 'post':
            return self.make_post_request(request, **kwargs)

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
                inputs = {k: v for k, v in param.items()
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
        for key, param in parameter_dict.items():
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
                    raise KeyError('Missing parameter {0} required'.format(
                                    param))

        # Remove placeholders
        for key in parameter_dict.keys():
            if key.startswith('?'):
                del parameter_dict[key]

        return str(parameter_dict)

    def make_post_request(self, request, **kwargs):
        """ Construct a post request for an API call
        """
        raise NotImplementedError('Post requests not working yet...')


