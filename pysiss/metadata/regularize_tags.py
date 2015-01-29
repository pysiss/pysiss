""" file: regularize_tag.py
    author: Jess Robertson

    description: Utilities to regularize tags
"""

from .namespaces import shorten_namespace

def regularize(name):
    """ Return name in regularized form, that is, lowercased with shortened namespaces
    """
    rname = shorten_namespace(name)
    rname = rname.lower().replace(' ', '_')
    return rname
