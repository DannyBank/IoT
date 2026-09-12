from machine import Pin, I2C

i2c = I2C(0, scl=Pin(22), sda=Pin(21))

devices = i2c.scan()

print("I2C devices found:", devices)

for device in devices:
    print("Decimal: ", device, "Hex:", hex(device))