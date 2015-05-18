""" file:   metadata.py (pysiss.metadata)
    author: Jess Robertson
            CSIRO Minerals Resources Flagship
    date:   Wednesday 27 August, 2014

    description: Functions to deal with gsml:geologicFeature data

    Geologic features can be shared by many different objects, so it makes
    sense to seperate these out into a seperate registry.
"""

from __future__ import print_function, division

from .registry import MetadataRegistry
from .namespaces import NamespaceMap
from .pysiss_namespace import PYSISS_NAMESPACE

from lxml import etree
import io
import uuid


def qname_str(qname):
    """ Represent a QName in a namespace:localname string
    """
    if qname.namespace not in (None, 'None', 'none'):
        result = '{0}:{1}'.format(qname.namespace, qname.localname)
    else:
        result = '{0}'.format(qname.localname)
    return result


def yamlify(mdata, nsmap, indent_width=2, indent=0):
    """ Convert an ETree instance into a YAML-esque representation

        Parameters
            mdata - an Metadata instance
            indent_width - with of a single indent step in characters
            indent - initial number of indentations
    """
    # Build line for current element
    spaces = ' ' * indent_width * indent
    result = spaces + qname_str(nsmap.shorten(mdata.tag))

    # Add lines for text
    if mdata.text and mdata.text.strip() != '':
        result += ' {0}'.format(mdata.text)

    # ... and metadata
    if mdata.attrib:
        for key in mdata.attrib.keys():
            qname = qname_str(nsmap.shorten(key))
            result += '\n' + spaces + ' ' * indent_width + \
                      '@{0}: {1}'.format(qname, mdata.attrib[key])

    # Add lines for children
    result += '\n'
    for child in mdata.getchildren():
        result += yamlify(child, nsmap,
                          indent_width=indent_width,
                          indent=indent + 1)
    return result


def xml_to_metadata(xml):
    """ Read some XML containing a metadata record

        Parameters:
            xml - either a handle to an open xml file, or a string of XML

        Returns:
            the new Metadata instance containing the record
    """
    # Initialize tree and XML namespaces
    if not isinstance(xml, io.IOBase):
        try:
            xml = io.BytesIO(xml.encode('utf-8'))
        except AttributeError:
            # We already have a bytestring so don't bother encoding it
            xml = io.BytesIO(xml)
    nspace = NamespaceMap()

    # Walk tree and generate parsing events to normalize tags
    elem = None
    context = iter(etree.iterparse(xml,
                                   events=('start-ns', 'start', 'end'),
                                   remove_comments=True,
                                   recover=True))
    for event, elem in context:
        # start-ns elem is a tuple with a key and url
        # We don't care about the key
        nspace.add_from_uri(elem[1])

    # Return the results if we have em
    if context.root is not None:
        return Metadata(elem=context.root, namespaces=nspace)
    else:
        raise ValueError("Couldn't parse xml")


def as_metadata(obj):
    """ Convert the given object to a Metadata instance

        Parameters:
            obj - the object to be converted. obj can be a string containing
            some xml, a handle to an open file, or an lxml element or elementtree
            instance. If object is already a Metadata instance, it is just returned.

        Returns:
            a Metadata instance
    """
    # Just return if we're already a metadata object
    if isinstance(Metadata, obj):
        return obj
    elif isinstance((io.IOBase, string), obj):
        return xml_to_metadata(obj)
    elif isinstance(lxml._Element):
        return Metadata(elem=obj)
    elif isinstance(lxml._ElementTree):
        return Metadata(elem=obj.root)


class Metadata(object):

    """ Class to store metadata record

        Can be initialized with an lxml.Element instance, or with a tag.

        Queries (XPath, or ElementPath) are passed through to the underlying
        element, with a few nicities to deal with XML namespaces.

        Parameters:
            elem - either an etree.ElementTree or etree.Element instance
                containing already-parsed data. Optional, but one of 'xml' or
                tree must be specified.
            tag - the tag for the metadata. Optional, if not specified
                the tag of the root of the metadata tree will be used. If both
                elem and tag are specified and elem.tag != tag, a ValueError
                will be raised.
            **kwargs - arbitrary attributes to attach to the metadata instance
    """

    registry = MetadataRegistry()

    def __init__(self, elem=None, tag=None,
                 text=None, namespaces=None, **attributes):
        super(Metadata, self).__init__()
        self.uuid = uuid.uuid5(uuid.NAMESPACE_DNS,
                               PYSISS_NAMESPACE + 'metadata')
        self.ident = self.uuid
        self._namespaces = namespaces or NamespaceMap()
        self._update_namespaces = True

        # Construct underlying element
        if elem is not None:
            self.root = elem
        elif tag is not None:
            self.root = etree.Element(tag, **attributes)
            if text:
                self.root.text = text
        else:
            raise ValueError(
                'You need to specify one of the tag or elem arguments to'
                'construct a Metadata instance')

        # Update other values
        if text:
            self.text = self.root.text = text
        self.attrib = self.root.attrib
        if attributes:
            self.set_attributes(**attributes)

        # Construct a namespace for the given element
        self.tag = tag or self.root.tag
        self.namespaces.add_from_tag(self.tag)

        # Add query methods
        for qmethod in ('xpath', 'find', 'findall'):
            setattr(self, qmethod, self._query_wrapper(qmethod))


    def __str__(self):
        """ String representation
        """
        template = 'Metadata record {0}, tagged with {1}'
        short_tag = qname_str(self.namespaces.shorten(self.root.tag))
        return template.format(self.ident, short_tag)

    def __getitem__(self, query):
        """ Return the element associated with the given tag

            Executes the given ElementPath query on the tree using
            lxml.findall, however if there is only one response, then
            it will unwrap the element from the list.
        """
        return self.findall(query, unwrap=True)

    @property
    def namespaces(self):
        """ Get the current namespace dictionary
        """
        if self._update_namespaces:
            self._namespaces.harvest_namespaces(self.root)
            self._update_namespaces = False
        return self._namespaces

    def get_attribute(self, attribute):
        """ Get the value of the given attribute
        """
        self._try_expanding_tag(attribute)
        return self.root.get(attribute)

    def set_attributes(self, **kwargs):
        """ Set the value of the given attribute

            Parameters:
                **kwargs - key value pairs for the given attributes
        """
        for attribute, value in kwargs.items():
            self._try_expanding_tag(attribute)
            self._try_expanding_tag(value)
            self.root.set(attribute, value)

    def get_children(self):
        """ Return an iterable over the children of the metadata element
        """
        return (self._wrap_element(c) for c in self.root.getchildren())

    def get_parent(self):
        """ Return the parent node of the given metadata element
        """
        return self._wrap_element(self.root.getparent())

    def _try_expanding_tag(self, tag):
        """ Will expand a tag if required
        """
        try:
            qname = etree.QName(tag)
            if qname.namespace is not None:
                qname.namespace = self.namespaces[qname.namespace]
                tag = qname_str(qname)
        except KeyError:
            pass
        except ValueError:
            pass

    def add_subelement(self, tag, text=None, **attributes):
        """ Add and return a metadata element with given attributes
            and text to the metadata instance.

            Parameters:
                tag - the tag of the new metadata element. This can use
                    the currently defined namespaces (which will be copied
                    into the new Metadata instance).
                text - the text to be associated with the element
                **attributes - key-value pairs to be associated with this content.
        """
        self._try_expanding_tag(tag)
        elem = etree.SubElement(self.root, tag)
        for key, value in attributes.items():
            elem.set(key, value)
        if text:
            elem.text = text
        self._update_namespaces = True
        return self._wrap_element(elem)

    def append(self, metadata):
        """ Add a preexisting metadata instance
        """
        self.root.append(metadata.root)
        for namespace_uri in metadata.namespaces.values():
            self.namespaces.add_from_uri(namespace_uri)

    def extend(self, *obj):
        """ Add and return metadata elements to the tree

            For details on the allowable object types that can be converted to
            to Metadata element instances, see the docstring for `as_metadata`
        """
        for obj in objs:
            self.append(as_metadata(obj))
        self._update_namespaces = True

    def register(self):
        """ Register this metadata instance with the Metadata registry
        """
        # Register yourself with the registry if required
        self.registry.register(self)

    def yaml(self, indent_width=2):
        """ Return a YAML-like representation of the tags

            Parameters:
                indent_width - the number of spaces in each indent level.
                    Optional, defaults to 2.

            Returns:
                a string reprentation of the metadata tree
        """
        return yamlify(self.root, self.namespaces,
                       indent_width=indent_width)

    def _query_wrapper(self, method):
        """ Wrapper around query methods for the metadata instance

            Constructs a namespace dictionary to make it easier to run
            concise query strings. Also wraps the results as a Metadata
            instance.
        """
        def _query(*qargs, unwrap=False, **qkwargs):
            """ Run query, extract results
            """
            keys = set(qkwargs.keys())
            if 'namespaces' in keys:
                qkwargs['namespaces'].update(self.namespaces)
            else:
                qkwargs.update(namespaces=self.namespaces)

            # Get results
            results = getattr(self.root, method)(*qargs, **qkwargs)

            # Wrap results and return
            try:
                try:
                    # Mostly things come back as lists
                    results = [self._wrap_element(r) for r in results]

                    # Unwrap the list if there's only one value to worry about
                    if unwrap:
                        if len(results) == 0:
                            return None
                        elif len(results) == 1:
                            return results[0]
                        else:
                            return results
                    else:
                        return results

                except TypeError:
                    # We don't have an iterator, so try wrapping directly...
                    return self._wrap_element(results)

            except AttributeError:
                # Something about making a metadata instance has failed, so
                # just return the results
                return results


        # Copy over docstring from lxml documentation
        setattr(_query, '__doc__', getattr(etree.ElementBase, method).__doc__)
        return _query

    def _wrap_element(self, elem):
        """ Wrap an element as a Metadata instance without having to update namespace
            definitions.
        """
        md = Metadata(elem=elem, namespaces=self.namespaces)
        md._update_namespaces = False
        return md
