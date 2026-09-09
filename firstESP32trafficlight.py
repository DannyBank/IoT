import machine
import time

# Pin Definitions
RED_PIN = 12
AMBER_PIN = 13
GREEN_PIN = 14

# Initialize Pins as Outputs
red_led = machine.Pin(RED_PIN, machine.Pin.OUT)
amber_led = machine.Pin(AMBER_PIN, machine.Pin.OUT)
green_led = machine.Pin(GREEN_PIN, machine.Pin.OUT)

def turn_off_all():
    """Utility function to reset all LEDs to off state."""
    red_led.value(0)
    amber_led.value(0)
    green_led.value(0)

print("Traffic Light System Started...")

# Main Loop
while True:
    # 1. STOP: Red Light ON
    turn_off_all()
    red_led.value(1)
    print("State: RED (Stop)")
    time.sleep(0.5)  # Hold Red for 5 seconds

    # 2. GO: Green Light ON
    turn_off_all()
    green_led.value(1)
    print("State: GREEN (Go)")
    time.sleep(0.5)  # Hold Green for 5 seconds

    # 3. CAUTION: Amber Light ON
    turn_off_all()
    amber_led.value(1)
    print("State: AMBER (Prepare to Stop)")
    time.sleep(1)  # Hold Amber for 2 seconds