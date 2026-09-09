from machine import Pin
import neopixel
import time
import math
import random

np = neopixel.NeoPixel(Pin(14, Pin.OUT), 8)

def show():
    np.write()

def off():
    for i in range(8):
        np[i] = (0,0,0)
    show()

# 1. ARC REACTOR - Iron Man
def arc_reactor():
    for i in range(8):
        np[i] = (0, 150, 255)
    show()
    for _ in range(30):
        # random sparkle
        idx = random.randint(0,7)
        np[idx] = (255,255,255)
        show()
        time.sleep_ms(50)
        np[idx] = (0,150,255)
    off()

# 2. EYE - Looks around
def eye():
    for pos in range(8):
        off()
        np[pos] = (255, 255, 0) # pupil yellow
        # eyelid white dim
        np[(pos-1)%8] = (30,30,30)
        np[(pos+1)%8] = (30,30,30)
        show()
        time.sleep_ms(120)
    off()

# 3. FIRE TORCH - flickering
def fire():
    for _ in range(80):
        for i in range(8):
            flicker = random.randint(100,255)
            np[i] = (flicker, flicker//3, 0)
        show()
        time.sleep_ms(60)
    off()

# 4. HEARTBEAT - 2 quick beats
def heartbeat():
    for _ in range(4):
        # Lub
        for i in range(8):
            np[i] = (255,0,0)
        show()
        time.sleep_ms(150)
        off()
        time.sleep_ms(100)
        # Dub - stronger
        for i in range(8):
            np[i] = (255,0,0)
        show()
        time.sleep_ms(150)
        off()
        time.sleep_ms(600)

# 6. WATER RIPPLE - drop and spread
def ripple():
    off()
    center = random.randint(0,7)
    np[center] = (0, 100, 255)
    show()
    time.sleep_ms(200)
    for r in range(1,4):
        off()
        np[(center+r)%8] = (0, int(100/r), int(255/r))
        np[(center-r)%8] = (0, int(100/r), int(255/r))
        show()
        time.sleep_ms(200)
    off()

# 7. SPINNING LOADERS - like loading icon
def portal():
    for _ in range(40):
        for i in range(8):
            # dim all
            for j in range(8):
                np[j] = (10,0,30)
            # 2 bright dots opposite each other spinning
            np[i] = (150, 0, 255)
            np[(i+4)%8] = (150, 0, 255)
            show()
            time.sleep_ms(50)

print("CREATIVE RING - Watch it")
time.sleep(2)

while True:
        # Random creative idle mode
        mode = random.choice([arc_reactor, eye, fire, heartbeat, ripple, portal])
        print("Mode:", mode.__name__)
        mode()
        time.sleep_ms(500)