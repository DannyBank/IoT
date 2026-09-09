import time
from machine import Pin
import dht

# Initialize the sensor pin (change GPIO pin as needed)
# For DHT11, use dht.DHT11(Pin(15))
# For DHT22 or DHT21, use dht.DHT22(Pin(15))
sensor = dht.DHT11(Pin(32))

def read_dht():
    try:
        # Trigger the measurement
        sensor.measure()
        
        # Extract temperature and humidity
        temp = sensor.temperature()  # Celsius
        humidity = sensor.humidity()  # Percentage
        
        print(f"Temperature: {temp:.1f}°C")
        print(f"Humidity: {humidity:.1f}%")
        
    except OSError as e:
        print("Failed to read sensor:", e)

# Main loop
while True:
    read_dht()
    # DHT sensors need at least 1-2 seconds between readings
    time.sleep(2)