from machine import Pin
from neopixel import NeoPixel
from time import sleep
import random

leds = NeoPixel(Pin(13), 8)

while True:
    i = random.randint(0, 7)
    
    red   = random.randint(0, 255)
    green = random.randint(0, 255)
    blue  = random.randint(0, 255)
    
    leds[i] = (red, green, blue)
    leds.write()
    
    sleep(0.3)
    
    leds[i] = (0, 0, 0)

