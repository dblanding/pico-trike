from machine import Pin,PWM
import utime

STEP = 100_000
MIN = 1_100_000
MID = 1_500_000
MAX = 1_900_000

pwm = PWM(Pin(15))

pwm.freq(50)
pwm.duty_ns(MID)
print(MID)
utime.sleep(1)

value = MIN
while value <= MAX:
    print(value)
    pwm.duty_ns(value)
    value += STEP
    utime.sleep(1)
pwm.duty_ns(MID)
print(MID)
