from dataclasses import dataclass

from . import utils


@dataclass
class GeoBounds:
    """
    Holds the 4 corner points of a geographic bounding "box" (its really a spherical cap).
    """

    longitude_min  : float  = 999999.0
    longitude_max  : float  = -999999.0
    latitude_min   : float  = 999999.0
    latitude_max   : float  = -999999.0

    def __repr__(self):
        return ( f'long = ( {self.longitude_min}, {self.longitude_max} ),'
                 ' lat = ( {self.latitude_min}, {self.latitude_max} )' )
    
    def __str__(self):
        return self.__repr__()

    def __bool__(self):
        return ( self.longitude_min <= 180.0 ) and ( self.latitude_min <= 90.0 )
    
    def corner_points(self):
        return [ ( self.longitude_min, self.latitude_min ),
                 ( self.longitude_max, self.latitude_min ),
                 ( self.longitude_max, self.latitude_max ),
                 ( self.longitude_min, self.latitude_max ) ]
    
    @property
    def longitude_span(self):
        return abs(self.longitude_max - self.longitude_min)
    
    @property
    def latitude_span(self):
        return abs(self.latitude_max - self.latitude_min)
    
    @property
    def longitude_span_miles(self):
        reference_latitude = ( self.latitude_max + self.latitude_min ) / 2.0
        return self.longitude_span * utils.get_miles_per_longitude(
            reference_latitude = reference_latitude )

    @property
    def latitude_span_miles(self):
        return self.latitude_span * utils.get_miles_per_latitude()
    
    def add_point( self, longitude : float, latitude : float ):
        self.add_longitude( longitude )
        self.add_latitude( latitude )
        return
    
    def add_bounds( self, other_geo_bounds : 'GeoBounds' ):
        self.longitude_min = min( other_geo_bounds.longitude_min, self.longitude_min )
        self.longitude_max = max( other_geo_bounds.longitude_max, self.longitude_max )
        self.latitude_min = min( other_geo_bounds.latitude_min, self.latitude_min )
        self.latitude_max = max( other_geo_bounds.latitude_max, self.latitude_max )
        return
    
    def add_longitude( self, longitude : float ):
        self.longitude_min = min( longitude, self.longitude_min )
        self.longitude_max = max( longitude, self.longitude_max )
        return
    
    def add_latitude( self, latitude : float ):
        self.latitude_min = min( latitude, self.latitude_min )
        self.latitude_max = max( latitude, self.latitude_max )
        return

    def contains_point( self, longitude_deg : float, latitude_deg : float ):
        return ( ( longitude_deg >= self.longitude_min )
                 and ( longitude_deg <= self.longitude_max )
                 and ( latitude_deg >= self.latitude_min )
                 and ( latitude_deg <= self.latitude_max ) )

    def contains_bounds( self, other_geo_bounds : 'GeoBounds' ):
        for longitude, latitude in other_geo_bounds.corner_points():
            if not self.contains_point( longitude_deg = longitude, latitude_deg = latitude ):
                return False
            continue
        return True

    def intersect( self, other_geo_bounds : 'GeoBounds' ):

        ll_x = max( self.longitude_min, other_geo_bounds.longitude_min )
        ll_y = max( self.latitude_min, other_geo_bounds.latitude_min )

        ur_x = min( self.longitude_max, other_geo_bounds.longitude_max )
        ur_y = min( self.latitude_max, other_geo_bounds.latitude_max )

        if ( ll_x > ur_x ) or ( ll_y > ur_y ):
            return None

        return GeoBounds( longitude_min = ll_x,
                          longitude_max = ur_x,
                          latitude_min = ll_y,
                          latitude_max = ur_y )
            
    def intersects( self, other_geo_bounds : 'GeoBounds' ):
        return self.intersect( other_geo_bounds ) is not None

    def set_latitude_range_min( self, desired_miles : float ):
        # N.B. Latitude distance not affected by longitude
        current_miles = utils.get_distance( self.latitude_min, 0.0, self.latitude_max, 0.0 )
        if current_miles >= desired_miles:
            return
        expand_miles = ( desired_miles - current_miles ) / 2.0
        expand_latitude_deg = utils.get_latitude_span( distance_miles = expand_miles )
        self.latitude_min -= expand_latitude_deg
        self.latitude_max += expand_latitude_deg
        return
