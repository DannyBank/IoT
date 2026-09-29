"""
Design a MicroPython system using the TEMT6000 light sensor, PIR mo-
tion sensor, and WS2812B LED ring.

Task:
. Measure the ambient light level using the TEMT6000.
. Detect the presence of a person using the PIR sensor.
. If motion is detected and the environment is dark, turn ON the LED
ring.
. Use different LED colours to represent different light levels.
. Turn OFF the LED ring when no motion is detected.
Challenge
Experiment with different light thresholds and LED colours.
"""

import time
from machine import ADC, Pin, neopixel

# --- Hardware Initialization ---
# 1. TEMT6000 Ambient Light Sensor (Analog input on GPIO 34)
adc_temt = ADC(Pin(34))
adc_temt.atten(ADC.ATTN_11DB)  # Full range: ~0.0V - 3.3V (0-4095)

# 2. PIR Motion Sensor (Digital input on GPIO 13)
pir_sensor = Pin(13, Pin.IN, Pin.PULL_DOWN)

# 3. WS2812B LED Ring (16 LEDs on GPIO 18)
NUM_LEDS = 16
np = neopixel.NeoPixel(Pin(18), NUM_LEDS)

# --- Thresholds & Configuration ---
DARK_THRESHOLD = 300     # Below this = Night Mode (Warm Color)
DIM_THRESHOLD = 1200     # Below this = Dim Mode (Cool Color), Above = Bright (No LED)
OFF_DELAY = 5            # Seconds to keep LEDs lit after motion stops

# --- Helper Functions ---
def set_ring_color(r, g, b):
    for i in range(NUM_LEDS):
        np[i] = (r, g, b)
    np.write()

def clear_ring():
    set_ring_color(0, 0, 0)

# --- Main Program Loop ---
print("Smart Nightlight System Active. Monitoring environment...")
clear_ring()

motion_timer = 0  # Timestamp tracking when motion was last detected

try:
    while True:
        ambient_light = adc_temt.read()
        motion_detected = pir_sensor.value() == 1
        current_time = time.time()

        if motion_detected:
            motion_timer = current_time

        # Check if we are within the off-delay window following motion
        is_active_window = (current_time - motion_timer) < OFF_DELAY

        if is_active_window:
            # Motion active & environment is dark/dim
            if ambient_light < DARK_THRESHOLD:
                # Dark environment -> Soft Amber (night-vision friendly)
                set_ring_color(150, 40, 0)
                status_color = "Amber (Dark Mode)"
            elif ambient_light < DIM_THRESHOLD:
                # Dim environment -> Soft Cool Blue/White
                set_ring_color(80, 120, 150)
                status_color = "Cool White (Dim Mode)"
            else:
                # Bright environment -> Keep LEDs off
                clear_ring()
                status_color = "OFF (Sufficient Ambient Light)"
        else:
            # Motion timeout reached or no motion detected
            clear_ring()
            status_color = "OFF (No Motion)"

        # Live telemetry output in Thonny Shell
        print(f"ADC Light: {ambient_light:<4} | Motion: {int(motion_detected)} | LED State: {status_color}")
        
        time.sleep(0.2)

except KeyboardInterrupt:
    clear_ring()
    print("\nNightlight System Halted Cleanly.")