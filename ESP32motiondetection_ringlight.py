import machine
import time
import random
import neopixel

# Hardware Configuration
PIR_PIN = 32      # PIR Motion Sensor Output Pin
NEOPIXEL_PIN = 14 # NeoPixel DIN Pin
NUM_LEDS = 8      # 8-LED Ring Light

# Initialize Hardware
pir = machine.Pin(PIR_PIN, machine.Pin.IN)
np = neopixel.NeoPixel(machine.Pin(NEOPIXEL_PIN), NUM_LEDS)

# Helper Functions
def show():
    np.write()

def off():
    for i in range(NUM_LEDS):
        np[i] = (0, 0, 0)
    show()

# --- ANIMATION FUNCTIONS ---

# 1. ARC REACTOR - Iron Man
def arc_reactor():
    for i in range(8):
        np[i] = (0, 150, 255)
    show()
    for _ in range(30):
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

# 5. WATER RIPPLE - drop and spread
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

# 6. SPINNING LOADERS - like loading icon
def portal():
    for _ in range(40):
        for i in range(8):
            for j in range(8):
                np[j] = (10,0,30)
            np[i] = (150, 0, 255)
            np[(i+4)%8] = (150, 0, 255)
            show()
            time.sleep_ms(50)
    off()

# List of animation functions to choose from randomly
animations = [arc_reactor, eye, fire, heartbeat, ripple, portal]

# Turn off LEDs at launch
off()

print("Calibrating PIR Sensor...")
time.sleep(15)  # PIR sensor warmup delay
print("System Ready! Waiting for motion...")

# Main Loop
while True:
    if pir.value() == 1:
        print("Motion detected! Triggering random animation...")
        # Pick and run a random animation from the list
        random_anim = random.choice(animations)
        random_anim()
        
        # Debounce delay so the animation doesn't immediately re-trigger
        time.sleep(1)
        
    time.sleep(0.1)