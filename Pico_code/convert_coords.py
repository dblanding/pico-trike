from math import modf, sqrt, tan, pi, sin, cos, atan2

EARTH_DIAM = 12_756_000  # (meters) approx sphere
METERS_PER_DEG = EARTH_DIAM * pi / 360
# More exactly, Earth is an oblate spheroid with larger dia at equator
A = 6_378_137  # ellipse semi-major axis of earth (m)
B = 6_356_752  # ellipse semi-minor axis of earth (m)

def deg2dms(decimal_deg):
    """Convert decimal degrees to deg, min, sec"""
    # math.modf() separates parts at '.'
    fraction, int_deg = modf(decimal_deg)
    fraction, int_min = modf(60 * fraction)
    sec = 60 * fraction
    return (int_deg, int_min, sec)

def east_west_foreshortening(lat):
    # calculate the foreshortening ratio (of east-west dimensions) at lat
    x = sqrt(1 / ( (1/A)**2 + (tan(lat * pi/180) / B )**2 ) )
    r = sqrt(x**2 * (1 + (tan(lat * pi/180))**2))
    return x / r

def r2p(x, y):
    """Convert rectangular coords (x, y) to polar (r, theta <rad>)."""
    r = sqrt(x**2 + y**2)
    theta = atan2(y, x)
    return (r, theta)

def p2r(r, theta):
    """Convert polar coords (r, theta <rad>) to rectangular (x, y)."""
    x = r * cos(theta)
    y = r * sin(theta)
    return (x, y)


class Convert_Coords():
    """Utility for converting from Lat, Lon to X, Y coords (meters)."""

    def __init__(self, home_lat, home_lon, frame_angle):
        """Home Latitude, Longitude, angle (deg) of X axis w/r/t East"""
        self.home_lat = home_lat  # Latitude of position at powerup
        self.home_lon = home_lon  # Longitude of position at powerup
        # Angle (w/r/t true East) robot is headed at powerup
        self.frame_angle = frame_angle * pi /180  # (radians)
        self.f = east_west_foreshortening(home_lat)

    def latlon_to_xy(self, lat, lon):
        """Convert decimal lat, lon coordinates to X, Y (meters)"""

        # First: Calculate (E, N) map coords from Lat/Lon
        northing = (lat - self.home_lat) * METERS_PER_DEG
        easting = (lon - self.home_lon) * METERS_PER_DEG * self.f
        point = (easting, northing)

        # Second: rotate frame from (E, N) to (X, Y)
        r, theta = r2p(easting, northing)  # convert to polar coords
        theta -= self.frame_angle  # subtract self.frame_angle
        x, y = p2r(r, theta)  # convert polar to rectangular
        return x, y

 
if __name__ == "__main__":
    lat = 28.925  # degrees
    # Test calculation of 'f' at local latitude, equator, pole
    print(east_west_foreshortening(lat))  # 0.8752535719485478
    print(east_west_foreshortening(0))  # 1.0
    print(east_west_foreshortening(90))  # ~0.0
    # Test ConvertCoords() against Google Maps
    # pnt in d/w at cntr of garage Lat/Lon: 28.924659060130185, -81.9695933569919
    # pnt in d/w at street Lat/Lon: 28.924696362963235, -81.9696663923254
    # Google Maps dist = 8.27 m     ConvertCoords() shows dist = 8.24 m
    cc = ConvertCoords(28.924659060130185, -81.9695933569919, 148)
    pt = cc.latlon_to_xy(28.924696362963235, -81.9696663923254)
    print(pt)  # (8.235090404042644, 0.24938427823916032)
