from math import modf, sqrt, tan, pi

a = 6_378_137  # semi-major axis of earth (m)
b = 6_356_752  # semi-minor axis of earth (m)

def deg2dms(decimal_deg):
    # Convert decimal degrees to deg, min, sec
    # math.modf() separates parts at '.'
    fraction, int_deg = modf(decimal_deg)
    fraction, int_min = modf(60 * fraction)
    sec = 60 * fraction
    return (int_deg, int_min, sec)

def east_west_foreshortening(lat):
    # calculate the foreshortening ratio (of east-west dimensions) at lat
    x = sqrt(1 / ( (1/a)**2 + (tan(lat * pi/180) / b )**2 ) )
    r = sqrt(x**2 * (1 + (tan(lat * pi/180))**2))
    return x / r

if __name__ == "__main__":
    lat = 28.925  # degrees
    print(east_west_foreshortening(lat))  # 0.8752535719485478
    print(east_west_foreshortening(0))  # 1.0
    print(east_west_foreshortening(90))  # 0.0
