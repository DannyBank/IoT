import time
from machine import ADC, Pin
import neopixel

# --- Configuration ---
ADC_PIN = 34  # ADC pin connected to TEMPT6000 OUT (e.g., GPIO34 on ESP32, 26 on Pico)
PIXEL_PIN = 14  # GPIO pin connected to NeoPixel DIN
NUM_LEDS = 8  # Number of LEDs on the WCMCU-2812B-8 ring

# Max channel brightness limit (0 to 255)
MAX_CHANNEL_BRIGHTNESS = 255

# Color RGB endpoints
# Whitish-Blue (cool light) at 0% intensity
COLOR_START = (180, 220, 255)
# Rose-Red at 100% intensity
COLOR_END = (255, 20, 100)

# Setup ADC
adc = ADC(Pin(ADC_PIN))

# For ESP32: Set 11dB attenuation for full range (0V - 3.6V)
# Uncomment the line below if using an ESP32:
# adc.atten(ADC.ATTN_11DB)

# Setup NeoPixel
np = neopixel.NeoPixel(Pin(PIXEL_PIN), NUM_LEDS)


def read_sensor_percentage():
    """Reads the ADC and returns a light intensity percentage (0.0 to 1.0)."""
    # 16-bit ADC read (0 to 65535)
    raw_val = adc.read_u16()

    # Map to 0.0 - 1.0 float range
    percentage = raw_val / 65535.0

    # Ensure bounds [0.0, 1.0]
    return max(0.0, min(1.0, percentage))


def update_ring_light(intensity_pct):
    """Fills the NeoPixel ring proportionally and shifts color from Whitish-Blue to Rose-Red."""
    # Compute current color interpolation based on overall ambient light intensity
    r_target = int(
        COLOR_START[0] + (COLOR_END[0] - COLOR_START[0]) * intensity_pct
    )
    g_target = int(
        COLOR_START[1] + (COLOR_END[1] - COLOR_START[1]) * intensity_pct
    )
    b_target = int(
        COLOR_START[2] + (COLOR_END[2] - COLOR_START[2]) * intensity_pct
    )

    # Total capacity scaled across all LEDs
    total_level = intensity_pct * NUM_LEDS

    for i in range(NUM_LEDS):
        # Calculate how much intensity belongs to this specific LED
        led_fill = max(0.0, min(1.0, total_level - i))

        # Scale the target color by the individual LED's fill/brightness
        r = int(r_target * led_fill)
        g = int(g_target * led_fill)
        b = int(b_target * led_fill)

        np[i] = (r, g, b)

    np.write()


# --- Main Loop ---
print("TEMPT6000 Light Ring Monitor Running...")

while True:
    # 1. Read ambient light intensity percentage
    light_pct = read_sensor_percentage()

    # 2. Update the LED ring display
    update_ring_light(light_pct)

    # 3. Delay briefly to smooth out readings
    time.sleep_ms(20)