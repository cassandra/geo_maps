import logging
import unittest

from org.cassandra.geo_maps.geo_bounds import GeoBounds
import org.cassandra.geo_maps.geo_maps as geo_maps
from org.cassandra.geo_maps.view_box import ViewBox

logging.disable(logging.CRITICAL)


class GeoMapTestCase(unittest.TestCase):

    def test_AlbersMapProjection_x_y_from_deg(self):

        projection = geo_maps.AlbersMapProjection(
            reference_longitude_deg = -96.0,
            reference_latitude_deg = 37.5,
            standard_parallel_1_deg = 29.5,
            standard_parallel_2_deg = 45.5,
        )

        ##########
        # Origin
        
        x, y = projection.x_y_from_deg( longitude_deg = -96.0, latitude_deg = 37.5 )
        self.assertAlmostEqual( 0.0, x, 3 )
        self.assertAlmostEqual( 0.0, y, 3 )

        ##########
        # Move one direction in all four axis
        
        x, y = projection.x_y_from_deg( longitude_deg = -96.0, latitude_deg = 38.5 )
        self.assertAlmostEqual( 0.0, x, 3 )
        self.assertAlmostEqual( 69.84956867705023, y, 3 )

        x, y = projection.x_y_from_deg( longitude_deg = -96.0, latitude_deg = 36.5 )
        self.assertAlmostEqual( 0.0, x, 3 )
        self.assertAlmostEqual( -69.8404998056858, y, 3 )

        x, y = projection.x_y_from_deg( longitude_deg = -97.0, latitude_deg = 37.5 )
        self.assertAlmostEqual( -54.34331045483962, x, 3 )
        self.assertAlmostEqual( 0.2858889519893637, y, 3 )

        x, y = projection.x_y_from_deg( longitude_deg = -95.0, latitude_deg = 37.5 )
        self.assertAlmostEqual( 54.34331045484031, x, 3 )
        self.assertAlmostEqual( 0.2858889519893637, y, 3 )

        ##########
        # Four points in a rectangle
        
        x, y = projection.x_y_from_deg( longitude_deg = -97.0, latitude_deg = 38.5 )
        self.assertAlmostEqual( -53.608402435177354, x, 3 )
        self.assertAlmostEqual( 70.13159142946915, y, 3 )
        
        x, y = projection.x_y_from_deg( longitude_deg = -95.0, latitude_deg = 38.5 )
        self.assertAlmostEqual( 53.608402435177354, x, 3 )
        self.assertAlmostEqual( 70.13159142946915, y, 3 )
        
        x, y = projection.x_y_from_deg( longitude_deg = -95.0, latitude_deg = 36.5 )
        self.assertAlmostEqual( 55.07812305821839, x, 3 )
        self.assertAlmostEqual( -69.55074515609158, y, 3 )
        
        x, y = projection.x_y_from_deg( longitude_deg = -97.0, latitude_deg = 36.5 )
        self.assertAlmostEqual( -55.07812305821839, x, 3 )
        self.assertAlmostEqual( -69.55074515609158, y, 3 )
        
        return
    
    def test_AlbersMapProjection_deg_from_x_y__meridian_start(self):

        # Testing reverse projection assuming forward projection works

        projection = geo_maps.AlbersMapProjection(
            reference_longitude_deg = -96.0,
            reference_latitude_deg = 37.5,
            standard_parallel_1_deg = 29.5,
            standard_parallel_2_deg = 45.5,
        )
        
        for longitude, latitude in [
                ( -96.0, 37.5 ),

                ( -96.0, 38.5 ),
                ( -96.0, 35.5 ),

                ( -97.0, 37.5 ),
                ( -95.0, 37.5 ),
                
                ( -97.0, 38.5 ),
                ( -97.0, 35.5 ),
                ( -98.0, 38.5 ),
                ( -99.0, 35.5 ),
                ( -120.0, 50.5 ),
                ( -45.0, 20.5 ),
                ( -55.2, 41.5 ),

                ( -81.15127264439442, 25.263853338793016 ),
                ( -81.15858843137195, 24.89571739549468 ),
                ( -80.64731283060156, 24.88392006428615 ),
                ( -80.63785909356982, 25.252027883135245 ),
                
        ]:
            x, y = projection.x_y_from_deg( longitude_deg = longitude, latitude_deg = latitude )

            result_longitude, result_latitude = projection.deg_from_x_y( x = x, y = y )
            self.assertAlmostEqual( longitude, result_longitude, 5, f'{longitude}, {latitude}' )
            self.assertAlmostEqual( latitude, result_latitude, 5, f'{longitude}, {latitude}' )
            continue

        for longitude in range( -180, 180 ):
            for latitude in range( -90, 90 ):
                x, y = projection.x_y_from_deg( longitude_deg = float(longitude),
                                                latitude_deg = float(latitude) )
                result_longitude, result_latitude = projection.deg_from_x_y( x = x, y = y )
                self.assertAlmostEqual( longitude, result_longitude, 5, f'{longitude}, {latitude}' )
                self.assertAlmostEqual( latitude, result_latitude, 5, f'{longitude}, {latitude}' )
                continue
            continue
        return
    
    def test_GeoMap_projections__from_coords(self):

        # Testing reverse projection assuming forward projection works

        projection = geo_maps.AlbersMapProjection(
            reference_longitude_deg = -96.0,
            reference_latitude_deg = 37.5,
            standard_parallel_1_deg = 29.5,
            standard_parallel_2_deg = 45.5,
        )

        geo_map = geo_maps.GeoMap(
            projection = projection,
            geo_bounds = GeoBounds(
                longitude_min = -83.0,
                longitude_max = -79.0,
                latitude_min = 23.0,
                latitude_max = 25.5,
            ),
            svg_template_name = "_",
            view_box = ViewBox(
                x = 0.0,
                y = 0.0,
                width = 984.234,
                height = 755.998,
            ),
            display_x_scale = 8.3165,
            display_y_scale = 8.1012,
            display_x_offset = -6331.5623,
            display_y_offset = -6782.7542,
            
            rotation_angle_deg = -7.75,
        )
        
        for x, y in [
                ( 492.117, 585.61495075 ),
                ( 492.117, 793.2309015000001 ),
                ( 762.4122622500001, 793.2309015000001 ),
                ( 762.4122622500001, 585.61495075 ),
        ]:
            result_longitude, result_latitude = geo_map.coords_to_long_lat_deg( x = x, y = y )
            result_x, result_y = geo_map.long_lat_deg_to_coords( longitude_deg = result_longitude,
                                                                 latitude_deg = result_latitude )

            self.assertAlmostEqual( x, result_x, 5, f'{x}, {y}' )
            self.assertAlmostEqual( y, result_y, 5, f'{x}, {y}' )
            continue
        return

    def test_GeoMap_projections__from_long_lat(self):

        # Testing reverse projection assuming forward projection works

        projection = geo_maps.AlbersMapProjection(
            reference_longitude_deg = -96.0,
            reference_latitude_deg = 37.5,
            standard_parallel_1_deg = 29.5,
            standard_parallel_2_deg = 45.5,
        )

        geo_map = geo_maps.GeoMap(
            projection = projection,
            geo_bounds = GeoBounds(
                longitude_min = -83.0,
                longitude_max = -79.0,
                latitude_min = 23.0,
                latitude_max = 25.5,
            ),
            svg_template_name = "_",
            view_box = ViewBox(
                x = 0.0,
                y = 0.0,
                width = 984.234,
                height = 755.998,
            ),
            display_x_scale = 8.3165,
            display_y_scale = 8.1012,
            display_x_offset = -6331.5623,
            display_y_offset = -6782.7542,
            rotation_angle_deg = -7.75,
        )
        
        for longitude, latitude in [
                ( -81.15, 25.26 ),
                
                ( -96.0, 37.5 ),

                ( -95.0, 37.5 ),
                ( -95.0, 36.5 ),
                ( -96.0, 36.5 ),
                ( -96.0, 37.5 ),

        ]:
            result_x, result_y = geo_map.long_lat_deg_to_coords( longitude_deg = longitude,
                                                                 latitude_deg = latitude )
            result_longitude, result_latitude = geo_map.coords_to_long_lat_deg( x = result_x, y = result_y )

            self.assertAlmostEqual( longitude, result_longitude, 5, f'{longitude}, {latitude}' )
            self.assertAlmostEqual( latitude, result_latitude, 5, f'{longitude}, {latitude}' )
            continue

        return
        
