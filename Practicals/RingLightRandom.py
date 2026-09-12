from machine import Pin
from neopixel import NeoPixel
from time import sleep
import random

leds = NeoPixel(Pin(13), 8)

while True:
    for i in range(8):
        leds[i] = (0,0,0)
    number = random.randint(1, 8)
    
    for n in range(number):
        i = random.randint(0, 7)
        
        red = random.randint(0, 255)
        green = random.randint(0, 255)
        blue = random.randint(0, 255)
        
        leds[i] = (red, green, blue)
        
    leds.write()
    
    delay = random.randint(5, 90)/100
    sleep(delay)