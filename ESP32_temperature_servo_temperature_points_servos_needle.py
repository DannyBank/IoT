import time
from machine import I2C, PWM, Pin

# --- Configuration ---
SCL_PIN = 22  # I2C SCL Pin (e.g., GPIO22 on ESP32, GP5 on Pico)
SDA_PIN = 21  # I2C SDA Pin (e.g., GPIO21 on ESP32, GP4 on Pico)
SERVO_PIN = 25  # PWM Pin connected to SG90 Signal wire

# Temperature Mapping Range (°C)
TEMP_MIN = 32.1  # Maps to 0 degrees (Left)
TEMP_MAX = 35.1  # Maps to 180 degrees (Right)

# SG90 Calibration Duty Cycles (for 16-bit PWM at 50Hz)
# 50Hz = 20ms period. 0.5ms pulse = 0 deg (~1638), 2.5ms pulse = 180 deg (~8192)
DUTY_MIN = 8192  # 0 degrees
DUTY_MAX = 1638  # 180 degrees

# Hardware Setup
i2c = I2C(0, scl=Pin(SCL_PIN), sda=Pin(SDA_PIN))
servo_pwm = PWM(Pin(SERVO_PIN))
servo_pwm.freq(50)  # Standard 50Hz frequency for RC servos

# I2C Sensor Addresses
AHT20_ADDR = 0x38
BMP280_ADDR = 0x77  # Might be 0x76 depending on your board SDO pin connection


# --- Helper Drivers ---
def init_aht20():
    """Initializes and calibrates the AHT20 temperature sensor."""
    time.sleep_ms(40)
    # Trigger AHT20 initialization
    i2c.writeto(AHT20_ADDR, bytes([0xBE, 0x08, 0x00]))
    time.sleep_ms(10)


def read_aht20():
    """Reads temperature in °C and humidity in % from AHT20."""
    # Trigger measurement
    i2c.writeto(AHT20_ADDR, bytes([0xAC, 0x33, 0x00]))
    time.sleep_ms(80)

    data = i2c.readfrom(AHT20_ADDR, 7)

    # Convert raw 20-bit temperature data
    raw_temp = ((data[3] & 0x0F) << 16) | (data[4] << 8) | data[5]
    temp_c = (raw_temp / 1048576.0) * 200.0 - 50.0

    # Convert raw 20-bit humidity data
    raw_humidity = ((data[1] << 16) | (data[2] << 8) | data[3]) >> 4
    humidity = (raw_humidity / 1048576.0) * 100.0

    return temp_c, humidity


def read_bmp280_pressure():
    """Reads raw pressure register from BMP280 in Pascals (hPa)."""
    # Force measurement / read pressure registers (0xF7 to 0xF9)
    try:
        data = i2c.readfrom_mem(BMP280_ADDR, 0xF7, 3)
        raw_press = (data[0] << 12) | (data[1] << 4) | (data[2] >> 4)
        # Approximate uncalibrated pressure reading in hPa for quick telemetry
        press_hpa = raw_press / 256.0
        return press_hpa
    except Exception:
        return 0.0


def set_servo_angle(angle):
    """Calibrates and sets SG90 servo position from 0 to 180 degrees."""
    # Clamp angle between 0 and 180
    angle = max(0.0, min(180.0, angle))

    # Map angle (0-180) to duty cycle (DUTY_MIN to DUTY_MAX)
    duty = int(DUTY_MIN + (angle / 180.0) * (DUTY_MAX - DUTY_MIN))
    servo_pwm.duty_u16(duty)


# --- Startup Sequence ---
print("Initializing I2C Sensors & Servo Calibration...")
init_aht20()

# Sweep servo once to test mechanical endpoints
print("Testing Servo endpoints: 0° -> 180° -> 90°")
set_servo_angle(0)
time.sleep(1)
set_servo_angle(180)
time.sleep(1)
set_servo_angle(90)
time.sleep(1)

# --- Main Loop ---
while True:
    try:
        # 1. Fetch sensor readings
        temp_c, humidity = read_aht20()
        pressure_hpa = read_bmp280_pressure()

        # 2. Map temperature (°C) to target Servo Angle (0 to 180 degrees)
        # 15°C or below -> 0 degrees (Far Left)
        # 35°C or above -> 180 degrees (Far Right)
        temp_ratio = (temp_c - TEMP_MIN) / (TEMP_MAX - TEMP_MIN)
        target_angle = temp_ratio * 180.0

        # Clamp angle between 0° and 180°
        target_angle = max(0.0, min(180.0, target_angle))

        # 3. Move Servo
        set_servo_angle(target_angle)

        print(
            f"Temp: {temp_c:.1f}°C | Hum: {humidity:.1f}% | Press: {pressure_hpa:.1f} hPa | Servo Angle: {target_angle:.1f}°"
        )

    except OSError as e:
        print("I2C Communication Error:", e)

    time.sleep(0.5)