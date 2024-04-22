from machine import Pin, UART
import utime
from bno08x_rvc import BNO08x_RVC, RVCReadTimeoutError

# Initialize IMU module
uart = UART(0, 115200, tx=Pin(16), rx=Pin(17))
rvc = BNO08x_RVC(uart)

count = 0
while True:
    try:
        yaw, pitch, roll, *accels = rvc.heading  # yaw increases turning right
    except RVCReadTimeoutError:
        yaw = None

    count += 1
    utime.sleep(0.01)  # looping fast makes IMU respond quickly
    if count % 10 == 0:  # but we don't need all that data
        print(yaw)
        count = 0
