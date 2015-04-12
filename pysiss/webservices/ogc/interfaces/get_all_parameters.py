#!/usr/bin/env python
""" file: get_all_parameters.py
    author: Jess Robertson
            CSIRO Minerals Resources Flagship
    date:   today

    description: Find all the parameters described in the specification files
"""

import os


def get_folders(folder):
    """ Get all folders in the current folder
    """
    return [f for f in os.listdir(folder)
            if os.path.isdir(os.path.join(folder, f))]


def get_parameters():
    """ Get the parameters for the different interfaces

        Returns a dictionary keyed by interface (e.g. 'wcs') with a list of
        unique parameters
    """
    current_directory = os.getcwd()
    interfaces = map(os.path.abspath, get_folders(
                     os.path.join(current_directory)))
    params = {i: [] for i in interfaces}
    for interface in interfaces:
        versions = [os.path.join(interface, v) for v in get_folders(interface)]
        for version in versions:
            paramfile = os.path.join(version, 'parameters.json')
            try:
                with open(paramfile, 'rb') as fhandle:
                    for line in fhandle:
                        words = line.replace('"', '').replace(',', '').split()
                        params[interface].extend([w for w in words
                                                  if w.startswith('@')])
            except IOError:
                continue

    # Sort and uniqify the parameters
    params = {i: sorted([p.lstrip('@') for p in set(plist)])
              for i, plist in params.items()}
    return params

if __name__ == '__main__':
    PARAMS = get_parameters()
    for iface, params in PARAMS.items():
        print '\nParameters for interface {0}: {1}'.format(
                    os.path.basename(iface), params)
