# relay driver

from machine import Pin
from utime import sleep

led = Pin("LED", Pin.OUT)
relay = Pin(18, Pin.OUT)

while True:
    led.value(1)
    relay.value(1)
    sleep(1)
    led.value(0)
    relay.value(0)
    sleep(1)