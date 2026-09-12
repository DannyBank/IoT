from machine import Pin, I2C
from time import sleep
import ahtx0
import bmp280

i2c = I2C(0, scl=Pin(22), sda=Pin(21))

print("I2C devices:", [hex(x) for x in i2c.scan()])

aht20 = ahtx0.AHT20(i2c)
bmp = bmp280.BMP280(i2c, addr=0x77)

while True:
    temperature = aht20.temperature
    humidity = aht20.relative_humidity
    pressure = bmp.pressure / 100
    
    print("Temperature:", temperature, "C")
    print("Humidity:", humidity, "%")
    print("Pressure:", pressure, "hPa")
    print("-------------------------")
    
    sleep(2)