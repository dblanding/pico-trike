# drive_trike.py

"""
pseudo_code:

GOAL_DIST = 1  # radius (m) considered to be "arrived" at goal, 

Read in waypoints.csv file
    If first line is 0, 0:
        then it contains (x,y) values (meters)
    Else:
        it contains (lat, lon) values
        Convert them to x, y values
    populate list of waypoints with X, Y values

# Drive along each segment of trip
for index in range(len(waypoints) - 1):
    start_pt = waypoints[index]
    goal_pt = waypoints[index + 1]
    line = (start_pt, goal_pt)
    while dist_to_goal_pt < GOAL_DIST:
        steer(curr_pose, line, )

def steer(curr_pose, line):
    # Set steering to keep curr_pt on line and pointed toward goal
    
        
# Add some delay to give IMU & GPS time to get working

"""
from math import atan2, pi
from machine import Pin, PWM, UART
import utime
from bno08x_rvc import BNO08x_RVC, RVCReadTimeoutError
from micropyGPS import MicropyGPS
from convert_coords import Convert_Coords

# Initialize coordinates at "Home" position
cc = Convert_Coords(28.924661, -81.969612, 148)

# Initialize GPS module
gps_module = UART(1, baudrate=9600, tx=Pin(20), rx=Pin(21))
time_zone = -5
gps = MicropyGPS(time_zone)

# Initialize IMU module
uart = UART(0, 115200, tx=Pin(16), rx=Pin(17))
rvc = BNO08x_RVC(uart)

# Set up pin for steering servo
pwm = PWM(Pin(15))
pwm.freq(50)

# PWM values for servo
MIN = 1_200_000
MID = 1_500_000
MAX = 1_800_000
MAX_ANGLE = 20  # degrees
GAIN = (MAX - MID) / 20

GOAL_DIST = 1  # radius (m) considered to be "arrived" at goal

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

    data = '{0:.6f}'.format(data)  # 6 decimal places
    return str(data)

def steer(angle):
    """Control steering: left=neg < angle(deg)=0 < right=pos"""
    if angle > MAX_ANGLE:
        angle = MAX_ANGLE
    elif angle < -MAX_ANGLE:
        angle = -MAX_ANGLE
    pwm_value = int(MID - (GAIN * angle))
    pwm.duty_ns(pwm_value)

# goal_x, goal_y = cc.latlon_to_xy(28.924725, -81.969643)  #d/w N corner
goal_x, goal_y = cc.latlon_to_xy(28.924797, -81.970497)  # mhc Santana & Carrera
count = 0
while True:
    # Get Latitude & Longitude coordinates
    length = gps_module.any()
    if length > 0:
        data = gps_module.read(length)
        for byte in data:
            message = gps.update(chr(byte))

    latitude = convert_coordinates(gps.latitude)
    longitude = convert_coordinates(gps.longitude)

    if latitude is not None and longitude is not None:
        # Convert to X, Y coords
        x, y = cc.latlon_to_xy(float(latitude), float(longitude))
        
        # Calculate angle to goal (degrees)
        theta = (180/ pi) * atan2(goal_y - y, goal_x - x)
    else:
        theta = None

    # Get yaw value (degrees)
    try:
        yaw, *rest = rvc.heading
    except RVCReadTimeoutError:
        yaw = None

    count += 1
    utime.sleep(0.01)  # looping fast makes IMU respond quickly
    if count % 10 == 0:  # but we don't need all that data
        count = 0
        # print("yaw = ", yaw)
        print(theta, yaw)
        if theta is not None:
            steer(-theta - yaw)
