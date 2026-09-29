"""
Exercise 2: Environmental Warning System
Design an environmental monitoring system using the AHT20 + BMP280,
traffic light module, and buzzer.

Task:
. Measure temperature, humidity, and atmospheric pressure.
. Define suitable thresholds for normal, warning, and critical conditions.
. Display the environmental status using the traffic light:
. Green - Normal condition.
. Yellow - Warning condition.
. Red - Critical condition.
. Activate the buzzer when a critical condition occurs.
Challenge
Determine and justify their own environmental thresholds.
"""
import time
from machine import I2C, Pin, PWM
import ahtx0
import bmp280

# 1. Hardware Initialization
i2c = I2C(0, scl=Pin(22), sda=Pin(21))

# Peripheral pin configuration
led_green = Pin(27, Pin.OUT)
led_yellow = Pin(26, Pin.OUT)
led_red = Pin(25, Pin.OUT)

# Active Buzzer on GPIO 14 (Using PWM for clean control)
buzzer_pwm = PWM(Pin(14), freq=2000, duty=0)

# Initialize Sensor Modules
aht20 = ahtx0.AHT20(i2c)
bmp = bmp280.BMP280(i2c, addr=0x77)

def set_traffic_light(green, yellow, red):
    led_green.value(green)
    led_yellow.value(yellow)
    led_red.value(red)

def alert_buzzer(enable):
    if enable:
        buzzer_pwm.duty(512)  # 50% duty cycle at 2 kHz
    else:
        buzzer_pwm.duty(0)

def evaluate_environment(temp, hum, press):
    # Critical Check (Crosses high hazard levels)
    if (temp > 35.0 or temp < 10.0) or (hum > 75.0) or (press < 995.0):
        return "CRITICAL"
    
    # Warning Check
    if (temp > 28.0 or temp < 18.0) or (hum > 60.0 or hum < 30.0) or (press < 1008.0):
        return "WARNING"
    
    return "NORMAL"

# --- Main Program Loop ---
print("System Operational. Monitoring environment...")

try:
    while True:
        temperature = aht20.temperature
        humidity = aht20.relative_humidity
        pressure = bmp.pressure / 100  # Convert Pa to hPa

        status = evaluate_environment(temperature, humidity, pressure)

        print(f"[{status}] Temp: {temperature:.1f}°C | Humidity: {humidity:.1f}% | Pressure: {pressure:.1f} hPa")

        if status == "NORMAL":
            set_traffic_light(1, 0, 0)
            alert_buzzer(False)

        elif status == "WARNING":
            set_traffic_light(0, 1, 0)
            alert_buzzer(False)

        elif status == "CRITICAL":
            set_traffic_light(0, 0, 1)
            # Pulsed alert pattern for critical state
            alert_buzzer(True)
            time.sleep(0.2)
            alert_buzzer(False)
            time.sleep(0.2)

        time.sleep(1.6)

except KeyboardInterrupt:
    # Safe cleanup on exit
    set_traffic_light(0, 0, 0)
    alert_buzzer(False)
    print("\nSystem Monitoring Halted.")