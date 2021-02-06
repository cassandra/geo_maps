# Albers Map Projections in Python

This is a code snippet to capture a Python implementation of converting a Geo coordinate (longitude and latitude) into X-Y coordinates of a 2D image using the Albers Projection.

The Albers projection is just one type of projection used in 2D display of (3D) geographic areas.  More common is the Mercator projection, which this code does not implement. To tell the difference, look at the upper edge (the 49th parallel) to see if it is straight or curved.  The Albers projection is the one where it appears curved. (There are many different projection types, these are just the most common ones.)

![Map Projection Types](images/projection-types.png "Map Projection Types")

# How to Use

This is not a stand-alone app or a library. It is simply some code snippets for the (non-trivial) Albers projection. I had trouble finding a good stand-alone Python implementation, spent the time creating it, and wanted to share.

If you just want the "math" for doing the projection, then this class is all you need:
```
src/python/org/cassandra/geo_maps/geo_maps.py:AlbersMapProjection
```
It has two main methods for converting to and from geo coords and x-y coords.

If you want to see a scheme for using this projection to display long/lat on a 2D image, then the remainder of the classes provide some helpers and a pattern for doing this.  The file

[src/python/org/cassandra/geo_maps/example.py](src/python/org/cassandra/geo_maps/example.py) 

provides a simple example for generating an SVG which draws a circle at a few geo points over the top of the US map. The comments explains the main steps needed and you can run it with:
```
python3 -m venv venv
source venv/bin/activate
export PYTHONPATH=`pwd`/src/python
python src/python/org/cassandra/geo_maps/example.py 
```


# Code Overview

The main class that captured the math necessary for the Albers projection is in:
```
src/python/org/cassandra/geo_maps/geo_maps.py:AlbersMapProjection
```

Specific instances of the typcially used projections are provided for the US:
```
src/python/org/cassandra/geo_maps/geo_maps.py:USA_CONTINENTAL_PROJECTION
src/python/org/cassandra/geo_maps/geo_maps.py:ALASKA_PROJECTION
src/python/org/cassandra/geo_maps/geo_maps.py:HAWAII_PROJECTION
```
You could create an instance for other locations as long as you know the reference points for the Albers projection.


To use these to render points on a 2D map image for display this class is used:

```
src/python/org/cassandra/geo_maps/geo_maps.py:GeoMap
```

Specific instances of this for mapping long/lat onto the provided SVG image "usa_continental.svg" are:
```
src/python/org/cassandra/geo_maps/geo_maps.py:USA_CONTINENTAL_GEO_MAP
src/python/org/cassandra/geo_maps/geo_maps.py:ALASKA_CONTINENTAL_GEO_MAP
src/python/org/cassandra/geo_maps/geo_maps.py:HAWAII_CONTINENTAL_GEO_MAP
```
You can adapt this to use a different SVG file, but you will have to determine the geo boundaries, scale and rotation that might have been applied when the SVG map was drawn. The SVG needs to represent an Albers projection, but people tend to do this at different scales and sometimes even apply a rotation to make it look nicer.

*SVG image is courtesy of the wikimedia folks.*

## The Tricky Part

In order to map long/lat to that particular SVG file, we need *three* different projections for that single SVG file.  That SVG is the typical composite map of the US showing Alaska and Hawaii in different locations, using different scales as well as having different projection parameters. Oh my!

Thus, for rendering arbitrary geo points on this map and ensure the right projection and mapping to the SVG is used, the following class is used:
```
src/python/org/cassandra/geo_maps/geo_maps.py:CompositeGeoMap
```
This combines the three different projections and knows which geo points need which projections.

# Setup and testing

A few bare-bones tests are provided which can be run with something like:
```
python3 -m venv venv
source venv/bin/activate
export PYTHONPATH=`pwd`/src/python
python -m unittest org.cassandra.geo_maps.tests.test_geo_maps 
```

# License

See: [LICENSE](LICENSE)
