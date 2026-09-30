import time
from machine import Pin, PWM

# Setup PWM pins (Adjust GPIO pin numbers to match your wiring)
# Typical pins shown below (e.g., Raspberry Pi Pico / ESP32)
pin_red = Pin(12, Pin.OUT)
pin_yellow = Pin(13, Pin.OUT)
pin_green = Pin(14, Pin.OUT)

# Initialize PWM on each pin at 1000 Hz
pwm_red = PWM(pin_red, freq=1000)
pwm_yellow = PWM(pin_yellow, freq=1000)
pwm_green = PWM(pin_green, freq=1000)

# Define 16-bit PWM range (0 to 65535 for MicroPython v1.19+)
MAX_DUTY = 65535


def set_duty(pwm, level):
    """Sets the duty cycle (0.0 to 1.0) for a given PWM object."""
    pwm.duty_u16(int(level * MAX_DUTY))


def fade_between(pwm_out, pwm_in, steps=100, delay=0.02):
    """Fades out one PWM pin while fading in another.

    - pwm_out: PWM object fading from 100% to 0%
    - pwm_in: PWM object fading from 0% to 100%
    - steps: Granularity of the fade
    - delay: Time delay between each step in seconds
    """
    for i in range(steps + 1):
        ratio = i / steps
        set_duty(pwm_in, ratio)  # Gradually turn ON next LED
        set_duty(pwm_out, 1.0 - ratio)  # Gradually turn OFF current LED
        time.sleep(delay)


# Turn off all lights initially
set_duty(pwm_red, 0)
set_duty(pwm_yellow, 0)
set_duty(pwm_green, 0)

# Start cycle with Green turned fully ON
set_duty(pwm_green, 1.0)
time.sleep(1)  # Hold initial green for 1 second

print("Starting traffic light fade loop...")

try:
    while True:
        # 1. Fade from Green to Yellow
        fade_between(pwm_green, pwm_yellow, steps=100, delay=0.02)
        time.sleep(1.5)  # Brief hold on yellow

        # 2. Fade from Yellow to Red
        fade_between(pwm_yellow, pwm_red, steps=100, delay=0.02)
        time.sleep(1.5)  # Brief hold on red

        # 3. Fade from Red back to Green
        fade_between(pwm_red, pwm_green, steps=100, delay=0.02)
        time.sleep(1.5)  # Brief hold on green

except KeyboardInterrupt:
    # Safely turn off all LEDs on stop
    pwm_red.deinit()
    pwm_yellow.deinit()
    pwm_green.deinit()
    print("Traffic light controller stopped.")