from machine import ADC, Pin
from time import sleep

adc = ADC(Pin(34))
adc.atten(ADC.ATTN_11DB)

while True:
    raw_value = adc.read()
    voltage = raw_value * (3.3 / 4095.0)
    print(f"Raw Value: {raw_value}, Voltage: {voltage:.2f}V")
    sleep(1)