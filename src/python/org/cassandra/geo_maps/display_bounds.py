from dataclasses import dataclass


@dataclass
class DisplayBounds:
    """ Holds the 4 corner points of a 2D bounding box """
    
    x_min  : float  = 99999999999.0
    x_max  : float  = -99999999999.0
    y_min   : float  = 99999999999.0
    y_max   : float  = -99999999999.0

    def __repr__(self):
        return f'x = ( {self.x_min}, {self.x_max} ), y = ( {self.y_min}, {self.y_max} )'
    
    def __str__(self):
        return self.__repr__()

    def __bool__(self):
        if ( self.x_min > 99999999998.0 ) or ( self.y_min > 99999999998.0 ):
            return False
        return True
    
    @property
    def x_span(self):
        return abs(self.x_max - self.x_min)
    
    @property
    def y_span(self):
        return abs(self.y_max - self.y_min)
    
    def add_point( self, x : float, y : float ):
        self.add_x( x )
        self.add_y( y )
        return

    @property
    def is_point(self):
        return ( self.x_min == self.x_max ) and ( self.y_min == self.y_max )
        
    def add_bounds( self, other_bounds ):
        self.x_min = min( other_bounds.x_min, self.x_min )
        self.x_max = max( other_bounds.x_max, self.x_max )
        self.y_min = min( other_bounds.y_min, self.y_min )
        self.y_max = max( other_bounds.y_max, self.y_max )
        return
    
    def add_x( self, x : float ):
        self.x_min = min( x, self.x_min )
        self.x_max = max( x, self.x_max )
        return
    
    def add_y( self, y : float ):
        self.y_min = min( y, self.y_min )
        self.y_max = max( y, self.y_max )
        return

    def intersect( self, other_geo_bounds ):

        ll_x = max( self.x_min, other_geo_bounds.x_min )
        ll_y = max( self.y_min, other_geo_bounds.y_min )

        ur_x = min( self.x_max, other_geo_bounds.x_max )
        ur_y = min( self.y_max, other_geo_bounds.y_max )

        if ( ll_x > ur_x ) or ( ll_y > ur_y ):
            return None

        return DisplayBounds( x_min = ll_x,
                              x_max = ur_x,
                              y_min = ll_y,
                              y_max = ur_y )
