from machine import Pin, PWM
from time import sleep

# Connect the SG90 signal wire to GPIO 25
SERVO_PIN = 25

servo = PWM(Pin(SERVO_PIN), freq=80)

def set_angle(angle):
    # Keep the angle within the safe range
    angle = max(0, min(180, angle))

    # Approximate SG90 pulse range:
    # 0°   = 1.0 ms
    # 180° = 2.0 ms
    min_duty = 3276
    max_duty = 6553

    duty = int(min_duty + (angle / 180) * (max_duty - min_duty))
    servo.duty_u16(duty)


while True:
    set_angle(0)
    sleep(0.10)

    set_angle(90)
    sleep(0.10)

    set_angle(180)
    sleep(0.10)