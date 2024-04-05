from machine import Pin, UART
import utime
from bno08x_rvc import BNO08x_RVC, RVCReadTimeoutError
from micropyGPS import MicropyGPS

# Initialize IMU module
uart = UART(0, 115200, tx=Pin(16), rx=Pin(17))
rvc = BNO08x_RVC(uart)

# Initialize GPS module
gps_module = UART(1, baudrate=9600, tx=Pin(4), rx=Pin(5))
time_zone = -3
gps = MicropyGPS(time_zone)

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

loop_count = 0
try:
    while True:
        loop_count += 1
        try:
            yaw, *rest = rvc.heading
        except RVCReadTimeoutError:
            yaw = None

        if loop_count == 10:
            loop_count = 0
            length = gps_module.any()
            if length > 0:
                data = gps_module.read(length)
                for byte in data:
                    message = gps.update(chr(byte))

            latitude = convert_coordinates(gps.latitude)
            longitude = convert_coordinates(gps.longitude)

            if latitude is None or longitude is None:
                continue
            print(latitude, longitude, yaw)

        utime.sleep_ms(10)  # need to go fast to make IMU responsive
except KeyboardInterrupt:
    print("\nCtrl-C pressed to exit.")
finally:
    uart.deinit()
