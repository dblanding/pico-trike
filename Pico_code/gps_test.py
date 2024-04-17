# GPS reader
# https://github.com/inmcm/micropyGPS

import time
from machine import Pin
from machine import UART
from micropyGPS import MicropyGPS

time_zone = -5
my_gps = MicropyGPS(time_zone)

uart = UART(1, baudrate=9600, tx=Pin(20), rx=Pin(21))

# Basic UART --> terminal printer, use to test your GPS module
while True:
    my_sentence = (str(uart.readline()))[1:]
    print(my_sentence)
    print(type(my_sentence))

    for x in my_sentence:
        my_gps.update(x)

    time.sleep(1)
    print("Satellite data updated: ", my_gps.satellite_data_updated())
    print("Latitude: ", my_gps.latitude)
    print("Longitude: ", my_gps.longitude)
    print("Course: ", my_gps.course)
    # speed in knots, mph, km/hr
    print("Speed: ", my_gps.speed)
    print("Altitude: ", my_gps.altitude)
    print("Geoid height: ", my_gps.geoid_height)
    # time (H, M, S) not accounting for daylight time
    print("Timestamp: ", my_gps.timestamp)
    print("Date: ", my_gps.date)
    print("No. of satellites: ", my_gps.satellites_in_use)
    print("Satellites used: ", my_gps.satellites_used)
    # Fix types can be: 1 = no fix, 2 = 2D fix, 3 = 3D fix
    print("Fix type: ", my_gps.fix_type)
    print("\n")
    