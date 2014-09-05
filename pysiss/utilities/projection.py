""" file: projection.py (pysiss.utilities)

    description: Projection utilities
"""

# from osgeo import ogr
# from shapely.wkb import loads


# def project(geom, to_epsg=900913, from_epsg=4326):
#     """utility function to do quick projection with ogr,
#     to and from shapely objects

#         >>> from shapely.geometry import LineString
#         >>> l = LineString([[-121, 43], [-122, 42]])
#         >>> lp = project(l, from_epsg=4326, to_epsg=26910)
#         >>> lp.wkt
#         'LINESTRING (663019.0700828594854102 4762755.6415722491219640,
#             582818.0692490270594135 4650259.8474613213911653)'

#         Stolen from http://hackmap.blogspot.com.au/2008/03/ogr-python-projection.html
#     """

#     to_srs = ogr.osr.SpatialReference()
#     to_srs.ImportFromEPSG(to_epsg)

#     from_srs = ogr.osr.SpatialReference()
#     from_srs.ImportFromEPSG(from_epsg)

#     ogr_geom = ogr.CreateGeometryFromWkb(geom.wkb)
#     ogr_geom.AssignSpatialReference(from_srs)

#     ogr_geom.TransformTo(to_srs)
#     return loads(ogr_geom.ExportToWkb())
