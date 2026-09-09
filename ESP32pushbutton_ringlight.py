from machine import Pin
import neopixel
import time
import random

# Hardware Configuration
BUTTON_PIN = 26
NEOPIXEL_PIN = 14
NUM_LEDS = 8  # Matched to your 8-LED ring functions

# Hardware Initialization
button = Pin(BUTTON_PIN, Pin.IN, Pin.PULL_UP)
np = neopixel.NeoPixel(Pin(NEOPIXEL_PIN), NUM_LEDS)

# Basic Display Helpers
def show():
    np.write()

def off():
    for i in range(NUM_LEDS):
        np[i] = (0, 0, 0)
    show()

# -------------------------------------------------------------
# ANIMATION FUNCTIONS
# -------------------------------------------------------------

# 1. ARC REACTOR - Iron Man
def arc_reactor():
    print("Animation: Arc Reactor")
    for i in range(8):
        np[i] = (0, 150, 255)
    show()
    for _ in range(30):
        # random sparkle
        idx = random.randint(0, 7)
        np[idx] = (255, 255, 255)
        show()
        time.sleep_ms(50)
        np[idx] = (0, 150, 255)
    off()

# 2. EYE - Looks around
def eye():
    print("Animation: Eye")
    for pos in range(8):
        off()
        np[pos] = (255, 255, 0) # pupil yellow
        # eyelid white dim
        np[(pos - 1) % 8] = (30, 30, 30)
        np[(pos + 1) % 8] = (30, 30, 30)
        show()
        time.sleep_ms(120)
    off()

# 3. FIRE TORCH - flickering
def fire():
    print("Animation: Fire Torch")
    for _ in range(80):
        for i in range(8):
            flicker = random.randint(100, 255)
            np[i] = (flicker, flicker // 3, 0)
        show()
        time.sleep_ms(60)
    off()

# 4. HEARTBEAT - 2 quick beats
def heartbeat():
    print("Animation: Heartbeat")
    for _ in range(4):
        # Lub
        for i in range(8):
            np[i] = (255, 0, 0)
        show()
        time.sleep_ms(150)
        off()
        time.sleep_ms(100)
        # Dub - stronger
        for i in range(8):
            np[i] = (255, 0, 0)
        show()
        time.sleep_ms(150)
        off()
        time.sleep_ms(600)

# 5. WATER RIPPLE - drop and spread
def ripple():
    print("Animation: Water Ripple")
    off()
    center = random.randint(0, 7)
    np[center] = (0, 100, 255)
    show()
    time.sleep_ms(200)
    for r in range(1, 4):
        off()
        np[(center + r) % 8] = (0, int(100 / r), int(255 / r))
        np[(center - r) % 8] = (0, int(100 / r), int(255 / r))
        show()
        time.sleep_ms(200)
    off()

# 6. SPINNING LOADERS - like loading icon
def portal():
    print("Animation: Portal Loader")
    for _ in range(40):
        for i in range(8):
            # dim all
            for j in range(8):
                np[j] = (10, 0, 30)
            # 2 bright dots opposite each other spinning
            np[i] = (150, 0, 255)
            np[(i + 4) % 8] = (150, 0, 255)
            show()
            time.sleep_ms(50)
    off()

# List of available animations
animations = [arc_reactor, eye, fire, heartbeat, ripple, portal]

# -------------------------------------------------------------
# MAIN CONTROL LOOP
# -------------------------------------------------------------
last_button_state = 1
off()

print("System Ready! Press the red button to trigger a random animation.")

while True:
    current_button_state = button.value()
    
    # Check for button press transition (HIGH to LOW)
    if last_button_state == 1 and current_button_state == 0:
        # Pick and execute a random animation from the list
        selected_animation = random.choice(animations)
        selected_animation()
        
        # Debounce delay
        time.sleep(0.2)
        
    last_button_state = current_button_state
    time.sleep(0.01)