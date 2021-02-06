import math

MILES_PER_KM = 0.621371

EARTH_RADIUS_AT_EQUATOR_KM = 6378.137
EARTH_RADIUS_AT_POLES_KM = 6356.752
EARTH_RADIUS_AT_LAT_25_KM = 6374.344
EARTH_RADIUS_AT_LAT_40_KM = 6369.345
EARTH_RADIUS_AT_LAT_49_KM = 6366.001

EARTH_RADIUS_AT_EQUATOR_MILES = EARTH_RADIUS_AT_EQUATOR_KM * MILES_PER_KM
EARTH_RADIUS_AT_LAT_40_MILES = EARTH_RADIUS_AT_LAT_40_KM * MILES_PER_KM

# 69.44 miles (approx) for each line of latitude (would be independent of
# location on globe if the earth was a perfect sphere).
#
MILES_PER_LATITUDE_LINE = 69.44
MILES_PER_LONGITUDE_LINE_AT_LAT_40 = 53.00


def get_miles_per_latitude():
    """
    Return the number of miles in one line of the latitude meridian lines.
    This is invariant of longitude.
    """
    return MILES_PER_LATITUDE_LINE


def get_miles_per_longitude( reference_latitude : float = 40.0 ):
    """
    Return the number of miles in one line of the longitude meridian lines.
    This depends on the latitude, but if not provided, a nomial location is chosen.
    """
    return get_distance( lat1 = reference_latitude, lng1 = 0.0, lat2 = reference_latitude, lng2 = 1.0 )


def get_latitude_span( distance_miles : float ):
    """
    Return the latitude increment value necessary to span the given number
    of miles.
    """
    return distance_miles / MILES_PER_LATITUDE_LINE


def get_longitude_span( latitude : float, distance_miles : float ):
    """
    Return the longitude increment value necessary to span the given number
    of miles at the given latitude.
    """
    # 49 miles for each longitude line at 45 degrees north
    # 53 miles for each longitude line at 40 degrees north (middle of US)
    # 57 miles for each longitude line at 35 degrees north
    if math.isclose( distance_miles, 0.0, rel_tol = 1e-8 ):
        return 0.0
    miles_per_longitude_line = get_distance( latitude, 0.0, latitude, 1.0, miles=True )
    return float(distance_miles) / miles_per_longitude_line


def get_distance( lat1, lng1, lat2, lng2, miles=True ):
    """ 
    Distance between two lat/lng coordinates in km using the Haversine formula.
    Uses decimal degrees.

    Copyright 2016, Chris Youderian, SimpleMaps, http://simplemaps.com/resources/location-distance
    Released under MIT license - https://opensource.org/licenses/MIT
    """
    earth_radius = EARTH_RADIUS_AT_LAT_40_KM
    
    lat1 = math.radians( lat1 )
    lat2 = math.radians( lat2 )
    lat_dif = lat2 - lat1
    lng_dif = math.radians( lng2 - lng1 )
    a = math.sin( lat_dif / 2.0 )**2 + math.cos( lat1 ) * math.cos( lat2 ) * math.sin( lng_dif / 2.0 )**2
    distance_km = 2 * earth_radius * math.asin( math.sqrt(a) )

    if miles:
        return distance_km * MILES_PER_KM
    else:
        return distance_km

    
