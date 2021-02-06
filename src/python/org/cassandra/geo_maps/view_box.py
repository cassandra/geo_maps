from dataclasses import dataclass

from .display_bounds import DisplayBounds


@dataclass
class ViewBox:
    """ Holds the values for the viewbox attribute of a SVG image. """
    
    x       : float
    y       : float
    width   : float
    height  : float
    map_id  : int    = None
    
    def __post_init__(self):
        self._max_x = self.x + self.width
        self._max_y = self.y + self.height
        return
        
    def __str__(self):
        return f'{self.x} {self.y} {self.width} {self.height}'
    
    @property
    def min_x(self):
        return self.x
    
    @property
    def min_y(self):
        return self.y
    
    @property
    def max_x(self):
        return self._max_x
    
    @property
    def max_y(self):
        return self._max_y
    
    @staticmethod
    def from_attribute_value( value : str ):
        components = value.split(' ')
        if len(components) != 4:
            raise ValueError( f'Invalid viewBox value "{value}".' )
        return ViewBox( x = float(components[0]), y = float(components[1]),
                        width = float(components[2]), height = float(components[3]) )

    def intersect( self, other_view_box ):

        ul_x = max( self.min_x, other_view_box.min_x )
        ul_y = max( self.min_y, other_view_box.min_y )

        lr_x = min( self.max_x, other_view_box.max_x )
        lr_y = min( self.max_y, other_view_box.max_y )

        if ( ul_x > lr_x ) or ( ul_y > lr_y ):
            return None

        return ViewBox( x = ul_x,
                        y = ul_y,
                        width = lr_x - ul_x,
                        height = lr_y - ul_y )
            
    def union( self, other_view_box ):

        ul_x = min( self.min_x, other_view_box.min_x )
        ul_y = min( self.min_y, other_view_box.min_y )

        lr_x = max( self.max_x, other_view_box.max_x )
        lr_y = max( self.max_y, other_view_box.max_y )

        return ViewBox( x = ul_x,
                        y = ul_y,
                        width = lr_x - ul_x,
                        height = lr_y - ul_y )
            
    def contains_point( self, x : float, y : float ):
        return ( ( x >= self.x ) and ( x <= self._max_x )
                 and ( y >= self.y ) and ( y <= self._max_y ) )
         
    def corner_points(self):
        return [ ( self.x, self.y ),
                 ( self.x + self.width, self.y ),
                 ( self.x + self.width, self.y + self.height ),
                 ( self.x, self.y + self.height ) ]

    @staticmethod
    def from_display_bounds( display_bounds : DisplayBounds,
                             aspect_ratio : float,
                             padding_ratio : float = 0.1 ):

        if display_bounds.is_point:
            # TODO: Arbitrary for now
            ViewBox( x = display_bounds.x_min - 10, y = display_bounds.y_min - 10, width = 20, height = 20 )
            
        padding_x = display_bounds.x_span * padding_ratio  # total padding for sum of both sides
        padding_y = display_bounds.y_span * padding_ratio

        new_width = display_bounds.x_span + padding_x
        new_height = display_bounds.y_span + padding_y

        if new_height == 0.0:
            padding_y = new_width / aspect_ratio
        else:
            current_aspect_ratio = new_width / new_height
            if current_aspect_ratio > aspect_ratio:
                target_height = new_width / aspect_ratio
                padding_y += target_height - new_height
            else:
                target_width = display_bounds.y_span * aspect_ratio
                padding_x += target_width - new_width

        ul_x, ul_y = ( display_bounds.x_min - ( padding_x / 2.0 ),
                       display_bounds.y_min - ( padding_y / 2.0 ) )
        lr_x, lr_y = ( display_bounds.x_max + ( padding_x / 2.0 ),
                       display_bounds.y_max + ( padding_y / 2.0 ) )

        return ViewBox( x = ul_x, y = ul_y, width = lr_x - ul_x, height = lr_y - ul_y )
    

