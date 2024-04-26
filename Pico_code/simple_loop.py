# simple_loop.py
"""
At Power-up, Trike should be positioned square to house, facing street.
This sets the IMU (yaw=0) along the X-axis
Next, press button to begin the loop
Once the LED starts to blink:
    3D GPS data available
    Data recording begins
    Steers toward the target
    When arrived at target X-coord value:
        Program exits
        Data collection stops

But the Trike keeps going because it is solar powered
So you have to grab it (or give it some shade)
"""

from math import atan2, pi
from machine import Pin, PWM, UART
import utime
from bno08x_rvc import BNO08x_RVC, RVCReadTimeoutError
from micropyGPS import MicropyGPS
from latlon2xy import LatLon2XY

XH, YH = 0, 0  # X, Y coords of HOME
XT, YT = 12, 0  # X, Y coordinates of target
HOME_LAT = 28.924700
HOME_LON = -81.969660
HOME_ANGLE = 148  # Angle (deg) from TRUE EAST to X axis of X,Y frame
DATAFILENAME = 'data0.txt'
INITIALIZED = False  # HOME pose initialized in X,Y frame?
STEERING_GAIN = 0.75

# PWM values for servo
MIN = 1_200_000
MID = 1_500_000
MAX = 1_800_000
MAX_ANGLE = 20  # degrees
SERVO_GAIN = (MAX - MID) / 20
GOAL_DIST = 2  # radius (m) considered to be "arrived" at goal

# set up button to trigger program exit
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
    """Steer left for Neg values, right for positive values"""
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

x = 0
loop_count = 0
while True:
    loop_count += 1

    # Check for Program Exit request
    if button.value() == 0:
        print("Exit button pressed")
        break
    if x > XT:
        print(f"Reached goal: x = {x} m")
        break

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
        # Reset loop_count
        loop_count = 0

        # Update GPS data
        my_sentence = (str(uart1.readline()))[1:]
        for word in my_sentence:
            gps.update(word)

        # Collect GPS data
        if gps.fix_type == 3:
            lat = convert_coordinates(gps.latitude)
            lon = convert_coordinates(gps.longitude)
            hr, min, sec = gps.timestamp
            time = f"{hr}:{min}:{sec}"
            day, mon, yr = gps.date
            date = f"{mon}/{day}/{yr}"

            if not INITIALIZED:
                # Initialize X, Y coordinate frame
                cf = LatLon2XY(HOME_LAT, HOME_LON, HOME_ANGLE)
                INITIALIZED = True
                x, y = 0, 0
                record(date)
                table_header = "Time, X (m), Y (m), Steer (deg)"
                print(table_header)
                record(table_header)
            else:
                x, y = cf.latlon_to_xy(lat, lon)

            # Steer to align heading w/ course
            crs_deg = atan2((0 - y), (12 - x)) * 180 / pi  # course to target
            steer_deg = (hdg_deg - crs_deg) * STEERING_GAIN  # steering angle (deg)
            steer(steer_deg)

            # print & record data
            text_data = f"{time}, {x}, {y}, {steer_deg}"
            print(text_data)
            record(text_data)

            # Turn on LED to signal successful data recording
            led.value(1)

led.value(0)
steer(0)