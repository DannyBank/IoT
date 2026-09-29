import dht
import time
from machine import Pin

# --- Configuration ---
DHT_PIN = 16  # Pin connected to DHT11 Data pin

RED_PIN = 19  # Pin connected to Red LED
YELLOW_PIN = 18  # Pin connected to Yellow LED
GREEN_PIN = 17  # Pin connected to Green LED

# Temperature Thresholds (in Celsius)
TEMP_WARN_LOW = 64  # Below this triggers Yellow
TEMP_WARN_HIGH = 68  # Above this triggers Yellow
TEMP_CRIT_HIGH = 75  # Above this triggers Red
TEMP_CRIT_LOW = 63  # Below this triggers Red

# Setup Hardware
sensor = dht.DHT11(Pin(DHT_PIN))  # Use dht.DHT22 if using a DHT22 module

led_red = Pin(RED_PIN, Pin.OUT)
led_yellow = Pin(YELLOW_PIN, Pin.OUT)
led_green = Pin(GREEN_PIN, Pin.OUT)


def set_traffic_light(red_state, yellow_state, green_state):
    """Utility to easily set all three LED states (1 for ON, 0 for OFF)."""
    led_red.value(1 if red_state else 0)
    led_yellow.value(1 if yellow_state else 0)
    led_green.value(1 if green_state else 0)


def update_status_light(temperature):
    """Updates the traffic light LEDs based on the measured temperature."""
    if TEMP_WARN_LOW <= temperature <= TEMP_WARN_HIGH:
        # Optimal Range -> Green
        set_traffic_light(red_state=False, yellow_state=False, green_state=True)
    elif (
        TEMP_WARN_HIGH < temperature <= TEMP_CRIT_HIGH
    ):
        # Warning Range -> Yellow
        set_traffic_light(red_state=False, yellow_state=True, green_state=False)
    elif (temperature > TEMP_CRIT_HIGH):
        # Critical Range -> Red
        set_traffic_light(red_state=True, yellow_state=False, green_state=False)
    elif (TEMP_CRIT_LOW <= temperature < TEMP_WARN_LOW):
        # set all
        set_traffic_light(red_state=True, yellow_state=True, green_state=True)
    else:
        # set all
        set_traffic_light(red_state=True, yellow_state=True, green_state=True)


# --- Main Loop ---
print("DHT11 Traffic Light Monitor Running...")

while True:
    try:
        # DHT11 requires at least 1-2 seconds between readings
        sensor.measure()

        temp = sensor.temperature()  # Temperature in °C
        humidity = sensor.humidity()  # Relative Humidity in %

        print(f"Temperature: {temp}°C | Humidity: {humidity}%")

        # Update the traffic light states
        update_status_light(humidity)

    except OSError as e:
        # DHT sensors can occasionally drop a frame or time out
        print("Failed to read from DHT11 sensor:", e)

    # DHT11 sampling rate limit is ~1Hz (read once every 2 seconds)
    time.sleep(2)