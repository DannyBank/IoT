from machine import Pin, I2C
from time import sleep_ms
from env_sensors import AHT20, BMP280

red = Pin(25, Pin.OUT, value=0)
yellow = Pin(26, Pin.OUT, value=0)
green = Pin(32, Pin.OUT, value=0)
buzzer = Pin(33, Pin.OUT, value=1)  # LOW = sound

def show(level):
    green.value(level == 0)
    yellow.value(level == 1)
    red.value(level == 2)
    buzzer.value(0 if level == 2 else 1)

def severity(t, h, p):
    # Classroom thresholds for a low-altitude location.
    if t < 10 or t >= 35 or h < 20 or h >= 80:
        return 2
    if p < 980 or p > 1040:
        return 2
    if t < 18 or t > 28 or h < 30 or h > 65:
        return 1
    if p < 1000 or p > 1025:
        return 1
    return 0

try:
    i2c = I2C(0, sda=Pin(21), scl=Pin(22), freq=100000)
    print('I2C:', [hex(a) for a in i2c.scan()])
    aht, bmp = None, None
    while True:
        try:
            if aht is None:
                aht = AHT20(i2c)
            if bmp is None:
                bmp = BMP280(i2c)
            t, h = aht.read()
            p = bmp.pressure_hpa()
            level = severity(t, h, p)
            show(level)
            print('T=%.1f C RH=%.1f%% P=%.1f hPa %s' %
                  (t, h, p, ('NORMAL', 'WARNING', 'CRITICAL')[level]))
        except (OSError, ValueError) as err:
            show(2)
            print('SENSOR FAULT:', err)
            aht, bmp = None, None
        sleep_ms(2000)
finally:
    red.off()
    yellow.off()
    green.off()
    buzzer.on()
