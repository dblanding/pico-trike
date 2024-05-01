# simple_loop.py
"""
1. At Power-up, set trike at garage door, square to house, facing street.
    This sets the IMU (yaw=0) along the X-axis
2. Next, press button to enter the main loop
    When the LED starts to blink:
        3D GPS data is available
        Target waypoints[0] is set as X,Y origin
        Data recording begins
        Steers to each target in waypoints sequentially
        Once it arrives at final target:
            Cut off power to motor
            Exit program
"""

from math import atan2, pi, sqrt
from machine import Pin, PWM, UART
import utime
from bno08x_rvc import BNO08x_RVC, RVCReadTimeoutError
from micropyGPS import MicropyGPS
from latlon2xy import LatLon2XY

waypoints_lat_lon = [(28.924715, -81.969655),
                     (28.924715, -81.969780),
                     ]
LAT_0, LON_0 = waypoints_lat_lon[0]  # Home coords
GOAL_REACHED = False
HOME_ANGLE = 148  # Angle (deg) from TRUE EAST to X axis of X,Y frame
DATAFILENAME = 'data0.txt'
INITIALIZED = False  # HOME pose initialized in X,Y frame?
STEERING_GAIN = 0.6

# PWM values for servo
MIN = 1_200_000
MID = 1_500_000
MAX = 1_800_000
MAX_ANGLE = 20  # degrees
SERVO_GAIN = (MAX - MID) / 20
GOAL_DIST = 2  # radius (m) considered to be "arrived" at goal

# set up button
button = Pin(5, Pin.IN, Pin.PULL_UP)

# Set up LED indicator -> printing data
led = Pin(22, Pin.OUT)

# Initialize GPS module
uart1 = UART(1, baudrate=9600, tx=Pin(20), rx=Pin(21))
time_zone = -5
gps = MicropyGPS(time_zone)

# Initialize IMU module
uart0 = UART(0, 115200, tx=Pin(16), rx=Pin(17))
rvc = BNO08x_RVC(uart0)

# Set up pin for steering servo
pwm = PWM(Pin(15))
pwm.freq(50)

# Set up relay for motor (N.O.)
relay = Pin(18, Pin.OUT)
relay.value(0)

# Initialize X, Y coordinate frame and
# Translate waypoints from Lat/Lon to X/Y coordinates
cf = LatLon2XY(LAT_0, LON_0, HOME_ANGLE)
waypoints_x_y = [cf.latlon_to_xy(lat, lon)
                 for lat, lon in waypoints_lat_lon]

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

def record(line):
    """Append data to file."""
    line += '\n'
    with open(DATAFILENAME, 'a') as file:
        file.write(line)

def steer(angle):
    """Steer left for negative values, right for positive values"""
    if angle > MAX_ANGLE:
        angle = MAX_ANGLE
    elif angle < -MAX_ANGLE:
        angle = -MAX_ANGLE
    pwm_value = int(MID - (SERVO_GAIN * angle))
    pwm.duty_ns(pwm_value)

# Wait for button press to start
while True:
    if button.value() == 0:
        print("Start button pressed")
        break
    utime.sleep(0.1)
utime.sleep(1)

curr_leg = 0
loop_count = 0
while True:
    loop_count += 1

    # Check for Program Exit request
    if button.value() == 0:
        print("Exit button pressed")
        break

    # Check if goal reached for this leg
    if GOAL_REACHED:
        print(f"Leg {curr_leg + 1} complete")
        record(f"Leg {curr_leg + 1} complete")
        curr_leg += 1
        if curr_leg >= len(waypoints_x_y):
            print("Final leg of trip complete")
            record("Final leg of trip complete")
            break
        else:
            print("Proceed to next leg")
            record("Proceed to next leg")
            GOAL_REACHED = False

    # Get heading value (degrees)
    try:
        yaw, *rest = rvc.heading  # yaw (deg) increases w/ right turn
    except RVCReadTimeoutError:
        yaw = None

    if yaw:
        hdg_deg = -yaw  # heading (hdg_deg) is + CCW from X-axis
    utime.sleep(0.01)  # fast loop makes IMU respond quickly

    if loop_count == 10:
        led.value(0)  # Leave LED on until 10th loop cycle

    if loop_count == 100:  # Everything else can go in the slow loop
        
        loop_count = 0  # Reset loop_count

        x_goal, y_goal = waypoints_x_y[curr_leg]

        # Update GPS data
        my_sentence = (str(uart1.readline()))[1:]
        for word in my_sentence:
            gps.update(word)

        if gps.fix_type == 3:

            # Turn on the motor
            relay.value(1)

            # Collect GPS data
            lat = convert_coordinates(gps.latitude)
            lon = convert_coordinates(gps.longitude)
            hr, mn, sec = gps.timestamp
            time = f"{hr}:{mn}:{sec}"
            day, mon, yr = gps.date
            date = f"{mon}/{day}/{yr}"
            sats = gps.satellites_used

            if not INITIALIZED:
                record(date)
                data_header = "Time, X (m), Y (m), Heading (deg), Dist (m), Course (deg), Satellites"
                print(data_header)
                record(data_header)
                INITIALIZED = True

            x, y = cf.latlon_to_xy(lat, lon)  # current position

            # Check distance to goal
            dist = sqrt((x_goal - x)**2 + (y_goal - y)**2)
            if dist < GOAL_DIST:
                GOAL_REACHED = True

            # Steer to align heading w/ course to goal
            if not GOAL_REACHED:
                crs_deg = atan2((y_goal - y), (x_goal - x)) * 180 / pi  # course to goal
                steer_deg = (hdg_deg - crs_deg) * STEERING_GAIN  # steering angle (deg)
                steer(steer_deg)

            # print & record data
            text_data = f"{time}, {x}, {y}, {hdg_deg}, {dist}, {crs_deg}, {sats}"
            print(text_data)
            record(text_data)

            # Turn on LED to signal successful data recording
            led.value(1)
        else:
            # Stop if no 3D gps reading
            relay.value(0)

relay.value(0)
led.value(0)
steer(0)
