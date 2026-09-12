from machine import Pin
from neopixel import NeoPixel
from time import sleep

leds = NeoPixel(Pin(13), 8)

while True:
    try:
        for i in range(8):
            leds[i] = (255, 0, 0)
        leds.write()
        sleep(1)
        for i in range(8):
            leds[i] = (0, 255, 0)
        leds.write()
        sleep(1)
        for i in range(8):
            leds[i] = (0, 0, 255)
        leds.write()
        sleep(1)
    except:
        for i in range(8):
            leds[i] = (0, 0, 0)
        leds.write()