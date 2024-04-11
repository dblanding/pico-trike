# collect_gps_data.py

from machine import Pin, UART
import utime
from micropyGPS import MicropyGPS

DATAFILENAME = 'data.txt'
RECORD_DATA_REQUESTED = False

# Initialize GPS module
gps_module = UART(1, baudrate=9600, tx=Pin(20), rx=Pin(21))
time_zone = -5
gps = MicropyGPS(time_zone)

# set up button to trigger data recording
button = Pin(5, Pin.IN, Pin.PULL_UP)

# Set up LED indicator -> button pushed
led = Pin(18, Pin.OUT)

def record(line):
    """Append data to file."""
    print(line)
    line += '\n'
    with open(DATAFILENAME, 'a') as file:
        file.write(line)

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

while True:
    length = gps_module.any()
    if length > 0:
        data = gps_module.read(length)
        for byte in data:
            message = gps.update(chr(byte))

    latitude = convert_coordinates(gps.latitude)
    longitude = convert_coordinates(gps.longitude)

    if latitude is None or longitude is None:
        continue
    # print('Lat: ' + latitude)
    # print('Lon: ' + longitude)

    utime.sleep_ms(100)  # Add a 100ms delay between GPS updates
    
    if button.value()==0:
        print("Button Pressed")
        led.value(1)
        utime.sleep(0.1)  # Debounce time
        led.value(0)
        record('Lat: ' + latitude + '\t' + 'Lon: ' + longitude)
