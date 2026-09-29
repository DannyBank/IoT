"""
Exercise 3: Smart Ventilation System
Design an automatic ventilation system using the AHT20 + BMP280, servo
motor, and push button.

Task:
. Continuously monitor temperature and humidity.
. Define a temperature threshold for activating ventilation.
. When the temperature exceeds the threshold, rotate the servo to
simulate opening a ventilation flap.
. When the temperature returns to normal, rotate the servo back to
simulate closing the flap.
. Use the push button to manually override the automatic control.
Challenge
Display the sensor readings, servo position, and operating mode
(Automatic or Manual) in the Thonny Shell.
"""

import time
from machine import I2C, Pin, PWM
import ahtx0
import bmp280

# --- Hardware Initialization ---
i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
aht20 = ahtx0.AHT20(i2c)
bmp = bmp280.BMP280(i2c, addr=0x77)

# Servo Configuration (50Hz PWM for SG90 / standard servos)
servo_pwm = PWM(Pin(13), freq=50)

# Push Button Configuration with Internal Pull-Up
button = Pin(14, Pin.IN, Pin.PULL_UP)

# --- Threshold & State Settings ---
TEMP_OPEN_THRESHOLD = 28.0    # °C to trigger opening
TEMP_CLOSE_THRESHOLD = 26.5   # °C to trigger closing (Hysteresis)

mode = "AUTO"                 # Modes: "AUTO" or "MANUAL"
manual_flap_state = False     # False = Closed, True = Open
current_servo_angle = 0       # 0° (Closed) to 90° (Open)

# Button Debouncing Variables
last_button_state = 1
last_debounce_time = 0
DEBOUNCE_DELAY = 200          # Milliseconds

# --- Helper Functions ---
def set_servo_angle(angle):
    """
    Maps 0 to 90 degrees to ESP32 16-bit PWM duty cycle (50Hz).
    0° ≈ 0.5ms pulse (duty 1638 / 65535)
    90° ≈ 1.5ms pulse (duty 4915 / 65535)
    """
    duty_min = 1638
    duty_max = 4915
    duty = int(duty_min + (angle / 90.0) * (duty_max - duty_min))
    servo_pwm.duty_u16(duty)

def check_button():
    """Handles non-blocking button press with debouncing and mode toggling."""
    global mode, manual_flap_state, last_button_state, last_debounce_time
    
    current_time = time.ticks_ms()
    reading = button.value()
    
    # State change detected (falling edge: button pressed down)
    if reading == 0 and last_button_state == 1:
        if time.ticks_diff(current_time, last_debounce_time) > DEBOUNCE_DELAY:
            last_debounce_time = current_time
            
            # Toggle logic: AUTO -> MANUAL (OPEN) -> MANUAL (CLOSED) -> AUTO
            if mode == "AUTO":
                mode = "MANUAL"
                manual_flap_state = True
            elif mode == "MANUAL" and manual_flap_state:
                manual_flap_state = False
            else:
                mode = "AUTO"
                
    last_button_state = reading

# --- Main Program Loop ---
print("Smart Ventilation System Starting...")
set_servo_angle(0)  # Start with flap closed

try:
    while True:
        check_button()
        
        # Read sensors
        temperature = aht20.temperature
        humidity = aht20.relative_humidity
        pressure = bmp.pressure / 100  # hPa
        
        # Determine Flap Position based on Mode
        if mode == "AUTO":
            if temperature >= TEMP_OPEN_THRESHOLD:
                current_servo_angle = 90
            elif temperature <= TEMP_CLOSE_THRESHOLD:
                current_servo_angle = 0
            # If between thresholds, maintain previous position (Hysteresis)
        else:
            # MANUAL Mode
            current_servo_angle = 90 if manual_flap_state else 0

        # Update Servo Output
        set_servo_angle(current_servo_angle)
        
        # Format Shell Output
        flap_status = "OPEN (90°)" if current_servo_angle == 90 else "CLOSED (0°)"
        print(f"[MODE: {mode:<6}] Temp: {temperature:.1f}°C | Hum: {humidity:.1f}% | Flap: {flap_status}")
        
        time.sleep(0.1)  # Fast sampling loop for button responsiveness

except KeyboardInterrupt:
    servo_pwm.deinit()
    print("\nSystem Halted cleanly.")