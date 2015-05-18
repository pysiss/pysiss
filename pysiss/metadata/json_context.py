""" file:   json_context.py (pysiss.metadata)
    author: Jess Robertson
            CSIRO Minerals Resources Flagship
    date:   Wednesday 27 August, 2014

    description: Implementations dealing with a JSON-LD context
"""

from namespace_map import NamespaceMap

from lxml import etree

def merge_namespace_and_tag(tag):
    """ Merge a tag with its namespace

        Handles URIs and URNs. If a tag doesn't have a namespace
        then this just returns the tag.
    """
    try:
        # Try to merge the namespace and the localname
        qname = etree.QName(tag)
        if qname.namespace:
            if qname.namespace.count(':') > 1: # We have a URN
                seperator = ':'
            else: # We have a URI
                seperator = '/'
            tag = qname.namespace + seperator + qname.localname
    except ValueError:
        pass
    return tag


def is_qname(tag):
    """ Determine whether a tag is a qname or not.

        A tag is a qname if it contains one ':' and that is not
        followed by '//'.
    """
    return tag.count(':') == 1 and not tag.split(':')[1].startswith('//')


class JSONLDContext(object):

    """ Stores a context for a JSON-LD file

        This also handles namespaces for XML in a slightly different manner to
        standard JSON-LD - sometimes it's useful to be able to retain a short
        namespace in the keys (especially if there are likely to be namespace
        clashes). So the JSON context can do one of four things:

            if namespace_handling == 'none', then no namespace handling is done
                and nothing gets written to the JSON context, except for
                container items. Keys retain their full strings.
            if namespace_handling == 'remove', then namespaces are removed from
                the keys (although each key is aliased back to the namespace in
                the JSON-LD context) and only the localname is preserved.
            if namespace_handling == 'shorten', then short namespaces are
                created for each key, of the form <ns>:<local> (like an XML
                QName). The full namespace is still recoverable from the
                context. A dictionary mapping each short namespace to a context
                is given in the #namespaces attribute under the root element.
            if namespace_handling == 'identify', then namespaces are identified
                but not shortened. No keys are written to the JSON-LD context
                but a list of namespaces is written to the #namespaces
                attribute.

        Parameters:
            mapping - a dict containing some initial definitions
            namespace_handling - how XMl namespaces should be handled. Must be
                one of 'remove', 'short' or 'full', otherwise a ValueError is
                raised.
    """

    def __init__(self, namespace_handling=None, mapping=None):
        super(JSONLDContext, self).__init__()
        self.nsmap = NamespaceMap()
        self.nslist = set()

        # Set up context data and pass through iteration stuff
        self._context = {}
        for attr in ('values', 'keys', 'items'):
            setattr(self, attr, getattr(self._context, attr))

        # Check that we've got the right value for the namespace handling
        allowed_values = ('none', 'remove', 'shorten', 'identify')
        if namespace_handling is None:
            namespace_handling = 'none'
        if namespace_handling not in allowed_values:
            raise ValueError("Invalid namespace handling option " +
                             "{0}, allowed values are {1}".format(
                                  namespace_handling, allowed_values))

        # Assign the correct method to process
        self._process = getattr(self, '_process_' + namespace_handling)
        self.namespace_handling = namespace_handling

        # Copy in initialization
        if mapping:
            for key, value in mapping.items():
                self[key] = value

    def __str__(self):
        """ Representation for use in a JSON-LD document
        """
        # Declare as a context
        rep = "'@context': {\n"

        # We sort to make sure that namespace declarations occur first
        # so 'ns' key comes before 'ns:foo'
        for key in sorted(self._context.keys()):
            value = self._context[key]
            rep += '    {0}: {1},\n'.format(key, value)
        rep += '}'
        return rep

    def __repr__(self):
        """ Representation of JSONLDContext
        """
        return 'JSONLDContext(namespace_handling={1}, mapping={0})'.format(
                   str(self._context), self.namespace_handling)

    def __getitem__(self, tag):
        """ Get the context associated with a given tag
        """
        try:
            return self._context[tag]
        except KeyError as err:
            # We may have a QName, so handle this
            if is_qname(tag):
                namespace, localname = tag.split(':')
                namespace = self._context[namespace]
                return merge_namespace_and_tag('{{{0}}}{1}'.format(
                                                namespace, localname))
            else:
                raise err

    def __setitem__(self, tag, context):
        """ Set the context associated with a tag
        """
        self._context[tag] = context

    def process(self, tag):
        """ Process a tag, handling the namespace in the correct way
        """
        return self._process(tag)

    def _process_identify(self, tag):
        """ Process a tag, identifying any namespaces
        """
        self.nsmap.add_from_tag(tag)
        return merge_namespace_and_tag(tag)

    def _process_none(self, tag):
        """ Process a tag, doing nothing with namespaces
        """
        return merge_namespace_and_tag(tag)

    def _process_shorten(self, tag):
        """ Process a tag, removing namespaces to the context but
            leaving a shortened version of the namespace in the tag
        """
        short_tag = self.nsmap.shorten(tag)
        if is_qname(short_tag):
            namespace, _ = short_tag.split(':')
            self[namespace] = self.nsmap[namespace]
        return short_tag

    def _process_remove(self, tag):
        """ Process a tag, removing namespaces to the context
        """
        self.nsmap.add_from_tag(tag)
        try:
            qname = etree.QName(tag)
            self[qname.localname] = merge_namespace_and_tag(tag)
            tag = qname.localname
        except ValueError:
            pass
        return tag
