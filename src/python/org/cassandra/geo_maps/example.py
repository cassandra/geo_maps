import os

from org.cassandra.geo_maps.geo_bounds import GeoBounds
from org.cassandra.geo_maps.geo_maps import UsaContinentalCompositeGeoMap
from org.cassandra.geo_maps.view_box import ViewBox


# These are the points we will plot over the US map.
#
GEO_POINTS = [
    { 'label': 'New York', 'latitude': 40.694300, 'longitude': -73.924900 },
    { 'label': 'Boston', 'latitude': 42.318800, 'longitude': -71.084600 },
    { 'label': 'Baltimore', 'latitude': 39.305100, 'longitude': -76.614400 },
    { 'label': 'Chicago', 'latitude': 41.837300, 'longitude': -87.686100 },
]

# This is the main class for doing the projection, deciding which
# projection is appropriate for a given point and has details of how to map
# to the coordinates of that particular SVG file (2D map).
#
usa_composite_map = UsaContinentalCompositeGeoMap

# In this example, we only want to display the portion of the map necessary
# to capture the points in the GEO_POINTS. i.e., we are not displaying the
# entire country map (unless the points span the country).
#
# We compute the geo bounds and then use that to find the display bounds via
# the projection.
#
geo_bounds = GeoBounds()
for geo_point in GEO_POINTS:
    geo_bounds.add_point( longitude = geo_point['longitude'],
                          latitude = geo_point['latitude'] )
    continue
display_bounds = usa_composite_map.geo_bounds_to_display_bounds( geo_bounds = geo_bounds )

# You can generate a map with a different aspect ratio than the original
# SVG, but in this example we don't.
#
aspect_ratio = usa_composite_map.default_aspect_ratio

# Since we are bounding the display by a set of cities, we typically do not
# want them to be right on the edge of the map, so have the ability to
# extend/pad the display area.
#
padding_ratio = 0.1

# The final viewBox for the SVG
#
view_box = ViewBox.from_display_bounds( display_bounds = display_bounds,
                                        aspect_ratio = aspect_ratio,
                                        padding_ratio = padding_ratio )

# Now we can generate the SVG plotting those point on the map.
#
outfile = 'example.svg'
with open( outfile, 'w' ) as out_fh:
    out_fh.write( '<svg id="usa-continental-map" class="geo-map"\n'
                  f'     xmlns="http://www.w3.org/2000/svg" viewBox="{view_box}">' )

    # Render the base map. The code supports the possibility of it having
    # multiple SVGs, but in this case there is only one.
    #
    for svg_template_name in usa_composite_map.svg_template_name_list:
        cur_dirname = os.path.dirname( __file__ )
        svg_filename = os.path.join( cur_dirname, svg_template_name )
        with open( svg_filename, 'r' ) as in_fh:
            out_fh.write( in_fh.read() )
        continue

    # Now we render each point as a circle with a text label.
    #
    for geo_point in GEO_POINTS:

        # First, get the appropriate GeoMap instance (which depends on whether
        # this point is in the lower 48, Alaska or Hawaii.
        #
        composite_map = usa_composite_map.get_geo_map_for_point(
            longitude_deg = geo_point['longitude'],
            latitude_deg = geo_point['latitude'],
        )

        # Then we can map the point into the SVG display space.
        #
        x, y = composite_map.long_lat_deg_to_coords(
            longitude_deg = geo_point['longitude'],
            latitude_deg = geo_point['latitude'],
        )
        out_fh.write( f'<circle cx="{x}" cy="{y}" r="3"></circle>\n' )
        out_fh.write( f'<text x="{x+5}" y="{y+5}" style="font-size: 12;">{geo_point["label"]}</text>\n' )
        continue
    
    out_fh.write( '</svg>' )


print( f'The example SVG file was written to: {outfile}.' )
print( f'Try this in your browser: file://{os.getcwd()}/{outfile}' )

