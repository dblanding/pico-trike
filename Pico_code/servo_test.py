from machine import Pin,PWM
import utime

STEP = 50_000
MIN = 1_200_000
MID = 1_500_000
MAX = 1_800_000

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
