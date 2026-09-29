from machine import Pin, ADC
from time import sleep_ms
from neopixel import NeoPixel

# ESP32: TEMT6000 S=34, PIR OUT=19, ring DI=18.
light = ADC(Pin(34))
light.atten(ADC.ATTN_11DB)
ring = NeoPixel(Pin(18, Pin.OUT), 8)
pir = Pin(19, Pin.IN)

# Relative ADC counts, not lux. Tune in your room.
VERY_DARK = 10000
DARK_ON = 25000
BRIGHT_OFF = 29000
dark = False

def paint(rgb):
    ring.fill(rgb)
    ring.write()

paint((0, 0, 0))
print('PIR settling: keep clear for 30 seconds')
sleep_ms(30000)

try:
    while True:
        raw = sum(light.read_u16() for _ in range(16)) // 16
        if raw < DARK_ON:
            dark = True
        elif raw >= BRIGHT_OFF:
            dark = False

        motion = pir.value()
        if motion and dark:
            if raw < VERY_DARK:
                colour, label = (0, 0, 32), 'BLUE: very dark'
            else:
                colour, label = (32, 12, 0), 'AMBER: dim'
        else:
            colour, label = (0, 0, 0), 'OFF'
        paint(colour)
        print('ADC=%d Light=%.1f%% Motion=%d %s' %
              (raw, raw * 100 / 65535, motion, label))
        sleep_ms(200)
finally:
    paint((0, 0, 0))
