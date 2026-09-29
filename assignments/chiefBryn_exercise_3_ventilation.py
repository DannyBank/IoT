from machine import Pin, I2C, PWM
from time import ticks_ms, ticks_diff, sleep_ms
from env_sensors import AHT20, BMP280

button = Pin(27, Pin.IN, Pin.PULL_UP)
servo = PWM(Pin(13), freq=50)
OPEN_ABOVE, CLOSE_AT = 28.0, 26.0
mode = 0  # AUTO -> MANUAL OPEN -> MANUAL CLOSED -> AUTO
names = ('Automatic', 'Manual open', 'Manual closed')
auto_open, angle = False, None
aht, bmp = None, None
t, h, p = None, None, None
fault = True
last_raw = stable = button.value()
changed = ticks_ms()
last_read = ticks_ms() - 2000
last_print = ticks_ms() - 2000

def move(degrees):
    # Conservative SG90 travel: 1.0 ms to 1.5 ms.
    pulse_us = 1000 + degrees * 1000 // 180
    servo.duty_u16(pulse_us * 65535 // 20000)

try:
    move(0)
    i2c = I2C(0, sda=Pin(21), scl=Pin(22), freq=100000)
    print('I2C:', [hex(a) for a in i2c.scan()])
    while True:
        now = ticks_ms()
        raw = button.value()
        if raw != last_raw:
            last_raw, changed = raw, now
        if ticks_diff(now, changed) >= 40 and raw != stable:
            stable = raw
            if stable == 0:
                mode = (mode + 1) % 3
                print('Mode:', names[mode])

        if ticks_diff(now, last_read) >= 2000:
            last_read = now
            try:
                if aht is None:
                    aht = AHT20(i2c)
                if bmp is None:
                    bmp = BMP280(i2c)
                t, h = aht.read()
                p = bmp.pressure_hpa()
                fault = False
                if t > OPEN_ABOVE:
                    auto_open = True
                elif t <= CLOSE_AT:
                    auto_open = False
            except (OSError, ValueError) as err:
                fault = True
                t, h, p = None, None, None
                aht, bmp = None, None
                print('SENSOR FAULT:', err)

        opened = (auto_open or fault) if mode == 0 else mode == 1
        target = 90 if opened else 0
        if target != angle:
            move(target)
            angle = target
        if ticks_diff(now, last_print) >= 2000:
            last_print = now
            if fault:
                print('Readings unavailable | %d deg | %s' %
                      (angle, names[mode]))
            else:
                print('T=%.1f C RH=%.1f%% P=%.1f hPa | %d deg | %s' %
                      (t, h, p, angle, names[mode]))
        sleep_ms(10)
finally:
    servo.deinit()
