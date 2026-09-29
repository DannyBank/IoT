import machine
import time

# Pin Definition (Use an ADC1 pin like GPIO 34, 35, 36, or 39)
TEMT6000_PIN = 34

# Configure ADC Pin
adc = machine.ADC(machine.Pin(TEMT6000_PIN))

# Configure ADC Attenuation (11dB allows reading full 0V to 3.3V range)
adc.atten(machine.ADC.ATTN_11DB)

# Configure 12-bit Resolution (0 to 4095 range)
adc.width(machine.ADC.WIDTH_12BIT)

def read_light():
    """Reads raw ADC value and converts it to voltage and estimated Lux percentage."""
    # Read raw 12-bit analog value (0 - 4095)
    raw_val = adc.read()
    
    # Calculate input voltage (3.3V reference)
    voltage = (raw_val / 4095.0) * 3.3
    
    # Calculate relative light level percentage
    light_percent = (raw_val / 4095.0) * 100
    
    return raw_val, voltage, light_percent

print("Starting TEMT6000 Light Sensor Test...")
print("--------------------------------------")

while True:
    raw, volt, percent = read_light()
    
    # Print readings formatted
    print("Raw: {:4d} | Voltage: {:.2f}V | Brightness: {:.1f}%".format(raw, volt, percent))
    
    time.sleep(0.5)