# collect_data.py

from machine import Pin, PWM, UART
import utime
from bno08x_rvc import BNO08x_RVC, RVCReadTimeoutError
from micropyGPS import MicropyGPS
from latlon2xy import LatLon2XY

INITIALIZED = False  # HOME pose initialized in X,Y frame?
ANGLE = 148  # Angle (deg) from TRUE EAST to X axis of X,Y frame

# Set up LED indicator -> printing data
led = Pin('LED', Pin.OUT)

# Initialize GPS module
uart1 = UART(1, baudrate=9600, tx=Pin(20), rx=Pin(21))
time_zone = -5
gps = MicropyGPS(time_zone)

# Initialize IMU module
uart0 = UART(0, 115200, tx=Pin(16), rx=Pin(17))
rvc = BNO08x_RVC(uart0)

def convert_coordinates(sections):
    if sections[0] == 0:  # sections[0] contains the degrees
        return None

    # sections[1] contains the minutes
    data = sections[0] + (sections[1] / 60.0)

    # sections[2] contains 'E', 'W', 'N', 'S'
    if sections[2] == 'S':
        data = -data
    if sections[2] == 'W':
        data = -data
    return data


loop_count = 0
while True:
    # Get yaw value (degrees)
    try:
        yaw, *rest = rvc.heading
    except RVCReadTimeoutError:
        yaw = None

    loop_count += 1
    utime.sleep(0.01)  # Being in a fast loop makes IMU respond quickly
    if loop_count == 90:  # Everything else can go in the slow loop
        loop_count = 0
        
        # Update GPS data
        my_sentence = (str(uart1.readline()))[1:]
        for x in my_sentence:
            gps.update(x)

        # Collect GPS data
        if gps.fix_type == 3:
            lat = convert_coordinates(gps.latitude)
            lon = convert_coordinates(gps.longitude)
            crs = gps.course
            spd = gps.speed[2] * 3600 / 1000  # m/s
            
            if not INITIALIZED:
                # Initialize X, Y coordinate frame
                cf = LatLon2XY(lat, lon, ANGLE)
                INITIALIZED = True
                x, y = 0, 0
            else:
                x, y = cf.latlon_to_xy(lat, lon)
            print(x, y, yaw, lat, lon, crs, spd)
            led.value(1)
            utime.sleep(0.1)  # light ON time
            led.value(0)
