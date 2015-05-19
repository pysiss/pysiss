""" file:   json_target.py (pysiss.metadata)
    author: Jess Robertson
            CSIRO Minerals Resources Flagship
    date:   May 2015

    description: Implementation of a JSON-LD target for lxml parsers
"""

from json_context import JSONLDContext
from ..utilities import accumulator

from lxml import etree

class JSONLDTarget(object):

    """ Target parser for lxml which emits JSON-LD rather than an XML tree

        This also handles namespaces for XML in a slightly different manner to
        standard JSON-LD - sometimes it's useful to be able to retain a short
        namespace in the keys (especially if there are likely to be namespace
        clashes). So the JSON context can do one of four things:

            if namespace_handling == 'none' or None, then no namespace handling
                is done and nothing gets written to the JSON context, except
                for container items. Keys retain their full strings.
            if namespace_handling == 'remove', then namespaces are removed from
                the keys (although each key is aliased back to the namespace in
                the JSON-LD context) and only the localname is preserved.
            if namespace_handling == 'shorten', then short namespaces are
                created for each key, of the form <ns>:<local> (like an XML
                QName). The full namespace is still recoverable from the
                context. A dictionary mapping each short namespace to a context
                is given in the #namespaces attribute under the root element.

            if namespace_handling == 'full', then namespaces are identified but
                not shortened. No keys are written to the JSON-LD context but
                a list of namespaces is written to the #namespaces attribute.

        Parameters:
            namespace_handling - how XMl namespaces should be handled. Must be
                one of 'remove', 'short' or 'full', otherwise a ValueError is
                raised.
    """

    def __init__(self, namespace_handling=None):
        self._first = True
        self.stack = []
        self.result = None
        self.context = JSONLDContext(namespace_handling=namespace_handling)

    @property
    def current_element(self):
        """ Returns a reference to the body of the currently building element
        """
        if len(self.stack):
            return self.stack[-1][1]
        else:
            return None

    def start(self, tag, attrib):
        """ Start generating a new object
        """
        # Push element onto stack to wait for children to be read
        self.stack.append((self.context.process(tag), accumulator()))

        # Add attributes to body
        if attrib:
            self.current_element['#attributes'] = \
                {self.context.process(k): self.context.process(v)
                 for k, v in attrib.items()}

    def data(self, data):
        """ Convert text to objects

            Data gets pushed to the current element
        """
        data = data.strip()
        if data != '':
            self.current_element['#data'] = data

    def end(self, tag):
        # Pop off currently building element
        tag, elem = self.stack.pop()
        if '#data' in elem.keys():
            # Clean up text by concatenating everything together
            if isinstance(elem['#data'], list):
                elem['#data'] = ' '.join(*elem['#data'])

            # If we've got no attributes, only text then we can move the data
            # up to the top level
            if list(elem.keys()) == ['#data']:
                elem = elem['#data']
            else:
                elem = dict(elem)

        elif not(elem):
            # If element is empty, replace with None
            elem = None

        else:
            # For everything else, convert to dict
            elem = dict(elem)

        # Refactor containers and hyperlinks to be more JSONeque
        if isinstance(elem, dict):
            # XML container classes end up looking something like tag:
            # {tag2: [stuff]}, which we can reshape to be tag: [stuff], with a
            # note in the context of tag: {@id: tag2, @container: @list}
            subelem_keys = [k for k in elem.keys() if not k.startswith('#')]
            if len(subelem_keys) == 1 and \
                isinstance(elem[subelem_keys[0]], list):
                # Replace current body with container
                container_type = tag
                contained_type = subelem_keys[0]
                elem = elem[contained_type]

                # Move container out to context (if it hasn't already)
                if isinstance(self.context[tag], str):
                    self.context[tag] = {'@id': self.context[container_type],
                                         '@type': self.context[contained_type],
                                         '@container': '@set'}

            # We can also check whether we have a URL as an attribute
            # We move this out an make a note in the context
            else:
                try:
                    # Identify the href link
                    attr_keys = list(elem['#attributes'].keys())
                    href_keys = ['href', 'xlink:href',
                                 'http://www.w3.org/1999/xlink/href']
                    if (list(elem.keys()) == ['#attributes']) \
                        and len(attr_keys) == 1 \
                        and (attr_keys[0] in href_keys):
                        elem = elem['#attributes'][attr_keys[0]]

                    # Move container out to context (if it hasn't already)
                    if isinstance(self.context[tag], str):
                        self.context[tag] = {'@id': self.context[tag],
                                             '@type': '@id'}
                except KeyError:
                    # There's no '#attributes' key
                    pass

        # Store result
        if self.current_element:  # Append to next element as child
            self.current_element[tag] = elem
        else:                     # We're at the root element so stash it away
            self.result = {tag: elem}

    def comment(self, text):
        """ Comments are ignored
        """
        pass

    def close(self):
        """ Clean up parser for next file
        """
        result, self.result = self.result, None
        context, self.context = self.context, JSONLDContext()
        self._first = True
        self.stack = []
        return result, context
