from dataclasses import dataclass
import math
from typing import List

from .display_bounds import DisplayBounds
from .geo_bounds import GeoBounds
from .view_box import ViewBox
from . import utils


@dataclass
class AlbersMapProjection:

    # Ref: https://en.wikipedia.org/wiki/Albers_projection
    
    # The center of the displayed map
    #
    reference_longitude_deg  : float
    reference_latitude_deg   : float

    standard_parallel_1_deg  : float
    standard_parallel_2_deg  : float

    # Ref: https://spatialreference.org/ref/esri/usa-contiguous-albers-equal-area-conic/prettywkt/
    #
    #  SPHEROID["GRS_1980",6378137,298.257222101]] -> 6378137 meters = 3963.190592 miles
    #
    radius_miles = utils.EARTH_RADIUS_AT_EQUATOR_MILES

    # For zero comparisons
    EPSILON = 0.000000001
    
    @property
    def reference_longitude_radians(self):
        return math.radians( self.reference_longitude_deg )
    
    @property
    def reference_latitude_radians(self):
        return math.radians( self.reference_latitude_deg )
    
    @property
    def standard_parallel_1_radians(self):
        return math.radians( self.standard_parallel_1_deg )
    
    @property
    def standard_parallel_2_radians(self):
        return math.radians( self.standard_parallel_2_deg )

    def __post_init__(self):
        # Common for all projections
        self.n = 0.5 * ( math.sin( self.standard_parallel_1_radians )
                         + math.sin( self.standard_parallel_2_radians ) )

        self.C = ( math.cos( self.standard_parallel_1_radians ) ** 2 ) \
            + 2 * self.n * math.sin( self.standard_parallel_1_radians )

        self.rho_0 = ( self.radius_miles / self.n ) \
            * math.sqrt( self.C - ( 2 * self.n * math.sin( self.reference_latitude_radians ) ))
        
        return
    
    def x_y_from_deg( self, longitude_deg : float, latitude_deg : float ):
        
        # Ref: https://en.wikipedia.org/wiki/Albers_projection#Formulas
        
        longitude = math.radians( longitude_deg )
        latitude = math.radians( latitude_deg )
    
        theta = self.n * ( longitude - self.reference_longitude_radians )

        rho_basis = self.C - ( 2 * self.n * math.sin( latitude ))
        if rho_basis < 0.0:
            return ( 0, 0 )
        rho = ( self.radius_miles / self.n ) * math.sqrt( rho_basis )
        
        x = rho * math.sin( theta )
        y = self.rho_0 - ( rho * math.cos( theta ))

        return ( x, y )

    def deg_from_x_y( self, x : float, y : float ):

        # Ref: https://mathworld.wolfram.com/AlbersEqual-AreaConicProjection.html

        rho_0_minus_y = self.rho_0 - y
        
        rho = math.sqrt( x**2 + rho_0_minus_y**2 )
        if abs(rho) > self.EPSILON:
            if self.n < 0.0:
                rho *= -1.0
                x *= -1.0
                rho_0_minus_y *= -1.0

            rho_adjusted = rho * self.n / self.radius_miles
            latitude_operand = ( self.C - ( rho_adjusted * rho_adjusted ) ) / ( 2 * self.n )
            if abs(latitude_operand) <= 1.0:
                latitude_radians = math.asin( latitude_operand )
            elif latitude_operand < 0.0:
                latitude_radians = -1.0 * math.pi / 2.0
            else:
                latitude_radians = math.pi / 2.0
            
            theta = math.atan2( x, rho_0_minus_y )

        else:
            theta = 0.0
            if self.n > 0:
                latitude_radians = math.pi / 2.0
            else:
                latitude_radians = -1.0 * math.pi / 2.0
        
        longitude_radians = self.reference_longitude_radians + ( theta / self.n )

        longitude_deg = math.degrees( longitude_radians )
        latitude_deg = math.degrees( latitude_radians )

        return ( longitude_deg, latitude_deg )

        
@dataclass
class GeoMap:
    """ Defines how a map projection lines up with an SVG file of a map with that projection. """
    
    projection         : AlbersMapProjection
    geo_bounds         : GeoBounds
    svg_template_name  : str
    view_box           : ViewBox
    
    # To adjust for the placement of the image (in SVG view box scale units)
    display_x_offset   : float  = None
    display_y_offset   : float  = None

    display_x_scale    : float  = None
    display_y_scale    : float  = None

    rotation_angle_deg : float  = None

    calibration_points : List  = None
    
    def __post_init__(self):

        self._rotation_angle_radians = None
        self._sine_angle = None
        self._cosine_angle = None
        if self.rotation_angle_deg:
            self._rotation_angle_radians = math.radians( self.rotation_angle_deg )
            self._sine_angle = math.sin( self._rotation_angle_radians )
            self._cosine_angle = math.cos( self._rotation_angle_radians )

        return

    @property
    def aspect_ratio(self):
        return self.view_box.width / self.view_box.height
    
    def long_lat_deg_to_coords( self, longitude_deg, latitude_deg ):

        projected_x, projected_y = self.projection.x_y_from_deg( longitude_deg = longitude_deg,
                                                                 latitude_deg = latitude_deg )
        
        if self._rotation_angle_radians:
            rotated_x = ( projected_x * self._cosine_angle ) - ( projected_y * self._sine_angle )
            rotated_y = ( projected_x * self._sine_angle ) + ( projected_y * self._cosine_angle )
            scaled_x = rotated_x * self.display_x_scale
            scaled_y = rotated_y * self.display_y_scale
        else:
            scaled_x = projected_x * self.display_x_scale
            scaled_y = projected_y * self.display_y_scale

        offset_x = scaled_x + self.display_x_offset
        offset_y = self.display_y_offset - scaled_y

        return ( offset_x , offset_y )
    
    def coords_to_long_lat_deg( self, x, y ):

        offset_x = x - self.display_x_offset
        offset_y = self.display_y_offset - y
        
        scaled_x = offset_x / self.display_x_scale
        scaled_y = offset_y / self.display_y_scale
        
        if self._rotation_angle_radians:
            rotated_x = ( scaled_x * self._cosine_angle ) + ( scaled_y * self._sine_angle )
            rotated_y = ( -1.0 * scaled_x * self._sine_angle ) + ( scaled_y * self._cosine_angle )
            longitude, latitude = self.projection.deg_from_x_y( x = rotated_x, y = rotated_y )
        else:
            longitude, latitude = self.projection.deg_from_x_y( x = scaled_x, y = scaled_y )

        return ( longitude, latitude )
  

USA_CONTINENTAL_PROJECTION = AlbersMapProjection(

    # References:
    #
    # https://gis.stackexchange.com/questions/141580/which-projection-is-best-for-mapping-the-contiguous-united-states
    # https://spatialreference.org/ref/esri/usa-contiguous-albers-equal-area-conic/html/
    #
    # From: https://pubs.usgs.gov/bul/1532/report.pdf, p. 94
    # 
    # Albers Equal-Area Conic projection, with standard parallels 20° G.nd 60° N.
    # This illustration includes all of North America to show the change in spacing of the
    # parallels. When used for maps of the 48 conterminous States standard parallels
    # are 29.5° and 45.5° N.
    #
    # For maps of Alaska, the chosen standard parallels are lats. 55° and
    # 65° N., and for Hawaii, lats. 8° and 18° N. In the latter case,
    # both parallels are south of the islands, but they were chosen to
    # include maps of the more southerly Canal Zone and especially the
    # Philippine Islands.

    reference_longitude_deg = -96.0,
    reference_latitude_deg = 37.5,

    standard_parallel_1_deg = 29.5,
    standard_parallel_2_deg = 45.5,
)


ALASKA_PROJECTION = AlbersMapProjection(

    # References:
    #  https://epsg.io/3338
    
    reference_longitude_deg = -154.0,
    reference_latitude_deg = 50.0,

    standard_parallel_1_deg = 55.0,
    standard_parallel_2_deg = 65.0,
)


HAWAII_PROJECTION = AlbersMapProjection(

    # References:
    #  https://epsg.io/102007
    
    reference_longitude_deg = -157.0,
    reference_latitude_deg = 13.0,

    standard_parallel_1_deg = 8.0,
    standard_parallel_2_deg = 18.0,
)


USA_CONTINENTAL_GEO_MAP = GeoMap(

    # Values arrived at by trial and error via map calibration testing page.
    
    projection = USA_CONTINENTAL_PROJECTION,

    geo_bounds = GeoBounds(
        longitude_min = -124.8679,
        longitude_max = -66.8628,
        latitude_min = 24.3959,
        latitude_max = 49.3877,
    ),
    
    svg_template_name = "usa_continental.svg",

    view_box = ViewBox(
        x = 0.0,
        y = 0.0,
        width = 958.0,
        height = 602.0,
    ),
    
    display_x_scale = 0.3332,
    display_y_scale = 0.3318,
    display_x_offset = 491.0249,
    display_y_offset = 323.6935,
    
)


ALASKA_CONTINENTAL_GEO_MAP = GeoMap(

    # Values arrived at by trial and error via map calibration testing page.
    
    projection = ALASKA_PROJECTION,

    geo_bounds = GeoBounds(
        longitude_min = -180.0,
        longitude_max = -129.993,
        latitude_min = 50.5,
        latitude_max = 71.5232,
    ),
    
    svg_template_name = "usa_continental.svg",

    view_box = ViewBox(
        x = 0.0,
        y = 0.0,
        width = 958.0,
        height = 602.0,
    ),
    
    display_x_scale = 0.1301,
    display_y_scale = 0.1311,
    display_x_offset = 132.4555,
    display_y_offset = 638.5017,
    
    rotation_angle_deg = -11.0,
)

HAWAII_CONTINENTAL_GEO_MAP = GeoMap(

    # Values arrived at by trial and error via map calibration testing page.
    
    projection = HAWAII_PROJECTION,

    geo_bounds = GeoBounds(
        longitude_min = -160.3922,
        longitude_max = -154.6271,
        latitude_min = 18.71,
        latitude_max = 22.3386,
    ),

    svg_template_name = "usa_continental.svg",
    
    view_box = ViewBox(
        x = 0.0,
        y = 0.0,
        width = 958.0,
        height = 602.0,
    ),
    
    display_x_scale = 0.3279,
    display_y_scale = 0.3371,
    display_x_offset = 325.5313,
    display_y_offset = 729.5,
    
    rotation_angle_deg = -0.5,
)


class CompositeGeoMap:
    """Combines multiple GeoMaps that share the same SVG file. i.e.,
    multiple maps rendered together.  

    To common example of this is the US map showing Alaska and Hawaii in
    the lower right hand corner below the Continetal US. These are not in
    the same geo coordinate space as the 48 continuous states *AND* they
    use different projection parameters (same Albers projection type, but
    different reference points on the globe.)

    Note that this means that the GeoBounds for the map can be a list of
    bounds, not just one bounding box, since different areas of the map can
    represent different geographic areas.
    """

    def __init__( self, map_id : int, geo_map_list : List[GeoMap] ):
        """ First one in list is considered default. List cannot be empty. """
        
        assert( geo_map_list )
        self._map_id = map_id
        self._geo_map_list = geo_map_list
        self._default_geo_map = self._geo_map_list[0]
        
        self._geo_bounds = GeoBounds()
        self._geo_bounds_list = list()
        
        svg_template_name_set = set()  # GeoMap often share the same SVG
        
        for geo_map in self._geo_map_list:
            # Make sure each view box reflects this composite map's id
            geo_map.view_box.map_id = self._map_id
            
            self._geo_bounds.add_bounds( geo_map.geo_bounds )
            self._geo_bounds_list.append( geo_map.geo_bounds )
            svg_template_name_set.add( geo_map.svg_template_name )
            continue

        self._svg_template_name_list = list(svg_template_name_set)
        
        return

    @property
    def map_id(self):
        return self._map_id
    
    @property
    def geo_bounds(self):
        """ A single view of the union of bounds for all contained GeoMap """
        return self._geo_bounds

    @property
    def geo_bounds_list(self):
        """ A list of the individual bounds for each contained GeoMap """
        return self._geo_bounds_list

    @property
    def default_view_box(self):
        return self._default_geo_map.view_box
    
    @property
    def default_reference_longitude_deg(self):
        return self._default_geo_map.projection.reference_longitude_deg
    
    @property
    def default_reference_latitude_deg(self):
        return self._default_geo_map.projection.reference_latitude_deg

    @property
    def default_aspect_ratio(self):
        return self._default_geo_map.aspect_ratio

    @property
    def svg_template_name_list(self):
        return self._svg_template_name_list

    def contains_bounds( self, geo_bounds : GeoBounds ):
        for geo_map_bounds in self._geo_bounds_list:
            if geo_map_bounds.contains_bounds( other_geo_bounds = geo_bounds ):
                return True
            continue
        return False
        
    def get_geo_map_for_point( self,
                               longitude_deg : float,
                               latitude_deg : float ):
        for geo_map in self._geo_map_list:
            if geo_map.geo_bounds.contains_point( longitude_deg = longitude_deg,
                                                  latitude_deg = latitude_deg ):
                return geo_map
            continue
        return self._default_geo_map

    def geo_bounds_to_display_bounds( self, geo_bounds : GeoBounds ):

        display_bounds = DisplayBounds()
        
        for geo_map in self._geo_map_list:
            intersection_geo_bounds = geo_map.geo_bounds.intersect( geo_bounds )
            if not intersection_geo_bounds:
                continue
            for longitude, latitude in intersection_geo_bounds.corner_points():
                x, y = geo_map.long_lat_deg_to_coords( longitude_deg = longitude,
                                                       latitude_deg = latitude )
                display_bounds.add_point( x = x, y = y )
                continue
            continue

        return display_bounds

    def view_box_to_geo_bounds_list( self, view_box : ViewBox ):

        geo_bounds_list = list()
        for geo_map in self._geo_map_list:

            geo_bounds = GeoBounds()
            for x, y in view_box.corner_points():
                longitude, latitude = geo_map.coords_to_long_lat_deg( x = x, y = y )
                geo_bounds.add_point( longitude = longitude, latitude = latitude )
                continue

            # If the long/lat form the projections do not fall inside the
            # known bounds, then we can ignore it.
            
            if not geo_map.geo_bounds.intersects( geo_bounds ):
                continue
            
            geo_bounds_list.append( geo_bounds )
            continue
        
        return geo_bounds_list

    
UsaContinentalCompositeGeoMap = CompositeGeoMap(
    map_id = 1,
    geo_map_list = [
        USA_CONTINENTAL_GEO_MAP,
        ALASKA_CONTINENTAL_GEO_MAP,
        HAWAII_CONTINENTAL_GEO_MAP,
    ]
)
