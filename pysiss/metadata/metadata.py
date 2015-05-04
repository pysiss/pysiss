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
            a tuple containing an lxml.etree.ElementTree instance holding
            the parsed data, and a pysiss.metadata.NamespaceMap instance
            holding the namespace urls and keys
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
                                   events=('end', 'start-ns'),
                                   remove_comments=True,
                                   recover=True))
    for event, elem in context:
        if event == 'start-ns':
            nskey, nsurl = elem  # start-ns elem is a tuple
            nspace[nskey] = nsurl

    # Return the results if we have em
    if elem is not None:
        return Metadata(elem)
    else:
        raise ValueError("Couldn't parse xml")


class Metadata(object):

    """ Class to store metadata record

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

    def __init__(self, elem=None, register=False,
                 tag=None, text=None, **attributes):
        super(Metadata, self).__init__()
        self.uuid = uuid.uuid5(uuid.NAMESPACE_DNS,
                               PYSISS_NAMESPACE + 'metadata')
        self.ident = self.uuid

        # Slurp in data
        if elem is not None and tag is not None:
            if tag != elem.tag:
                raise ValueError(("Tags for element and constructor differ "
                                  "(elem.tag = {0}, constructor argument={1})."
                                  " Bailing out!").format(elem.tag, tag))

        elif elem is not None:
            # Check we have an element, not elementtree
            if isinstance(elem, etree._ElementTree):
                elem = elem.getroot()
            elif not isinstance(elem, etree._Element):
                raise ValueError("Argument to 'elem' in Metadata constructor "
                                 "is not of type lxml.etree.ElementTree or "
                                 "lxml.etree.Element (it's type is "
                                 "{0})".format(type(elem)))

            # Copy over new namespaces
            self.namespaces = NamespaceMap(*elem.nsmap.values())
            self.root = etree.Element(elem.tag,
                                      nsmap=self.namespaces,
                                      children=elem.getchildren())
            self.tag = self.root.tag

        elif tag is not None:
            # Create an empty metadata instance
            self.namespaces = NamespaceMap(tag)
            self.root = etree.Element(tag, nsmap=self.namespaces)

        else:
            raise ValueError('One of tree or xml or tag has to be specified to '
                             'create a Metadata instance')

        # Add other attributes
        for key, value in attributes.items():
            self.set(key, value)
        if text:
            self.root.text = text
        self.text = self.root.text

        # Register yourself with the registry if required
        if register:
            self.registry.register(self)

    def __str__(self):
        """ String representation
        """
        template = 'Metadata record {0}, of datatype {1}'
        short_tag = qname_str(self.namespaces.shorten(self.root.tag))
        return template.format(self.ident, short_tag)

    def __getitem__(self, tag):
        """ Return the element associated with the given tag
        """
        return self.find(tag)

    def get(self, attribute):
        """ Get the value of the given attribute
        """
        return self.root.get(attribute)

    def set(self, attribute, value):
        """ Set the value of the given attribute
        """
        self.root.set(attribute, value)

    def append(self, tag, text=None, children=None, **attributes):
        """ Add and return a metadata element with given attributes
            and text to the metadata instance.

            Parameters:
                tag - the tag of the new metadata element. This can use
                    the currently defined namespaces (which will be copied
                    into the new Metadata instance).
                text - the text to be associated with the element
                attributes - key-value pairs to be associated with this content.
        """
        element = etree.SubElement(self.root, tag)
        for key, value in attributes.items():
            self.root.set(key, value)
        if text:
            element.text = text
        if children:
            element.append(children)
        return Metadata(element)

    def extend(self, *metadata):
        """ Add and return metadata elements to the tree
        """
        for metadatum in metadata:
            self.root.append(metadatum.root)

    def xpath(self, *args, **kwargs):
        """ Pass XPath queries through to underlying element

            Uses the namespace dictionary from the metadata element
            to expand namespace definitions

            Parameters: see lxml.etree.xpath for details
        """
        keys = set(kwargs.keys())
        if 'namespaces' in keys:
            kwargs['namespaces'].update(self.namespaces)
        else:
            kwargs.update(namespaces=self.namespaces)
        results = self.root.xpath(*args, **kwargs)

        # We need to check that we've actually got back element tree elements
        # before trying to wrap in a Metadata instance - xpath results may be
        # strings!
        try:
            return [Metadata(r) for r in results]
        except ValueError:
            return results

    def find(self, *args, **kwargs):
        """ Pass ElementPath queries through to underlying element
        """
        keys = set(kwargs.keys())
        if 'namespaces' in keys:
            kwargs['namespaces'].update(self.namespaces)
        else:
            kwargs.update(namespaces=self.namespaces)
        return Metadata(self.root.find(*args, **kwargs))

    def findall(self, *args, **kwargs):
        """ Pass ElementPath queries through to underlying element
        """
        keys = set(kwargs.keys())
        if 'namespaces' in keys:
            kwargs['namespaces'].update(self.namespaces)
        else:
            kwargs.update(namespaces=self.namespaces)
        results = self.root.findall(*args, **kwargs)
        try:
            return [Metadata(r) for r in results]
        except ValueError:
            return results

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
