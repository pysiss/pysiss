""" file:   block_requests.py
    author: Jess Robertson
            CSIRO Mineral Resources Flagship
    date:   September 2, 2014

    description: Utilities for subdividing bounding box requests into several
        queries. Useful if the endpoint does not implement paging.
"""

import numpy
import textwrap
import requests
import os
import logging

LOGGER = logging.getLogger('pysiss')

def make_blocks(lower_corner, upper_corner, nx_blocks, ny_blocks=None):
    """ Subdivide a bbox into a number of smaller bboxes, to improve the
        request times from web services
    """
    # Work out block sizes
    if ny_blocks is None:
        ny_blocks = nx_blocks
    (lx, ly), (ux, uy) = lower_corner, upper_corner
    dx = (ux - lx) / float(nx_blocks)
    dy = (uy - ly) / float(ny_blocks)

    # Make an index for x and y
    x_idx, y_idx = \
        numpy.meshgrid(numpy.arange(nx_blocks), numpy.arange(ny_blocks))

    # Return blocks as lower and upper corners
    lower_x, upper_x = map(lambda x: lx + x * dx, (x_idx, x_idx + 1))
    lower_y, upper_y = map(lambda y: ly + y * dy, (y_idx, y_idx + 1))
    corners = zip(zip(lower_x.ravel(), lower_y.ravel()),
                  zip(upper_x.ravel(), upper_y.ravel()))
    return corners

# Post request body
BBOX_FILTER_REQUEST = textwrap.dedent("""\
    <?xml version="1.0" encoding="utf-8"?>
    <wfs:GetFeature
     xmlns:wfs="http://www.opengis.net/wfs"
     xmlns:ogc="http://www.opengis.net/ogc"
     xmlns:gml="http://www.opengis.net/gml"
     xmlns:sa="http://www.opengis.net/sampling/1.0"
     maxFeatures="{max_features}" service="WFS"
     version="1.1.0" xmlns:gsml="urn:cgi:xmlns:CGI:GeoSciML:2.0">
       <wfs:Query typeName="gsml:MappedFeature">
        <ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">
           <ogc:BBOX>
             <ogc:PropertyName>gsml:shape</ogc:PropertyName>
             <gml:Envelope srsName="EPSG:4326">
               <gml:lowerCorner>
                 {lower_corner[0]}, {lower_corner[1]}
               </gml:lowerCorner>
               <gml:upperCorner>
                 {upper_corner[0]}, {upper_corner[1]}
               </gml:upperCorner>
             </gml:Envelope>
           </ogc:BBOX>
         </ogc:Filter>
       </wfs:Query>
    </wfs:GetFeature>
""")


def post_block_requests(wfsurl, filename,
                        lower_corner, upper_corner, nx_blocks, ny_blocks=None,
                        max_features=500, timeout=2000):
    """ Make several POST requests to a WFS URL and stash the data in seperate
        XML files

        This method splits a large bounding box into several smaller boxes and
        makes a request for each box seperately. This is useful for Web Feature
        Services which do not implement paging support.

        :param wfsurl: The URL of the Web Feature Service to query
        :type wfsrul: string
        :param filename: The root filename to stream the response to. The
            individual requests will be split into individual files under
            ./tmp, with each subfilename looking like
            tmp/{filename}_{index}.xml. The final combined file will look like
            {filename}.xml.
        :type filename: str
        :param lower_corner,upper_corner: A (latitude, longitude) tuple
            denoting the lower/upper corners of the bounding box
        :type lower_corner,upper_corner: tuple
        :param nx_blocks,ny_blocks: The number of subblocks in each direction.
            ny_blocks is optional - if set to None or not specified it takes
            the same value as nx_blocks.
        :type nx_blocks,ny_blocks: int
        :param max_features: The maximum number of features to ask for from the
            server. If you find that you're missing some features, try
            increasing this value. Alternatively, if you're getting a lot of
            timeout errors (503s) then try decreasing this value and
            increasing the number of subblocks in the query.
        :type max_features: int
        :param timeout: The timeout for each request, in seconds.
        :type timeout: int
    """
    # Split bounding box into blocks to make requests more manageable
    blocks = make_blocks(lower_corner, upper_corner, nx_blocks, ny_blocks)

    # Iterate over blocks, make requests
    for block_idx, (lower_corner, upper_corner) in enumerate(blocks):
        # Construct request parameters
        params = dict(lower_corner=lower_corner,
                      upper_corner=upper_corner,
                      max_features=max_features)
        data = BBOX_FILTER_REQUEST.format(**params)

        # Make the WFS requests
        response = requests.post(url=wfsurl,
                                 data=data,
                                 stream=True,
                                 timeout=timeout)

        # Make a temporary directory to hold the results of the requests
        if not os.path.exists('./xml_tmp'):
            os.mkdir('xml_tmp')

        # Stream body to file
        subfilename = 'xml_tmp/{0}_{1}.xml'.format(filename, block_idx)
        if response.status_code == 200:
            with open(subfilename, 'wb') as fhandle:
                for chunk in response.iter_content(chunk_size=int(1e5)):
                    fhandle.write(chunk)
        else:
            LOGGER.error('Request failed for file {1} - {0}'.format(
                response.status_code, subfilename))
