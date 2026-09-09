import machine
import time
import random
import neopixel

# --- PIN CONFIGURATION ---
PIR_PIN = 32
BUZZER_PIN = 33
BUTTON_PIN = 26
NEOPIXEL_PIN = 14
NUM_LEDS = 8

# --- INITIALIZATION ---
pir = machine.Pin(PIR_PIN, machine.Pin.IN)
button = machine.Pin(BUTTON_PIN, machine.Pin.IN, machine.Pin.PULL_UP)
np = neopixel.NeoPixel(machine.Pin(NEOPIXEL_PIN), NUM_LEDS)

# Global tracking for active buzzer instance
active_buzzer = None

def silence_buzzer():
    """Forces active buzzer PWM to 0 duty cycle before deiniting."""
    global active_buzzer
    if active_buzzer is not None:
        try:
            active_buzzer.duty(0)
        except (AttributeError, ValueError):
            try:
                active_buzzer.duty_u16(0)
            except (AttributeError, ValueError):
                pass
        active_buzzer.deinit()
        active_buzzer = None

def turn_off_everything():
    """Clears ring light and silences the buzzer immediately."""
    silence_buzzer()
    for i in range(NUM_LEDS):
        np[i] = (0, 0, 0)
    np.write()

def check_off_button():
    """Checks if the kill switch button is pressed."""
    if button.value() == 0:
        turn_off_everything()
        return True
    return False

def show():
    np.write()

# --- BUZZER AUDIO SYSTEM ---
def play_note(freq, duration_ms):
    global active_buzzer
    if check_off_button():
        return
        
    silence_buzzer() # Clean up any existing instance
    
    active_buzzer = machine.PWM(machine.Pin(BUZZER_PIN), freq=1000)
    active_buzzer.freq(freq)
    try:
        active_buzzer.duty(512)
    except (AttributeError, ValueError):
        active_buzzer.duty_u16(32768)
    
    # Sleep in 10ms increments to stay responsive to button presses
    steps = max(1, duration_ms // 10)
    for _ in range(steps):
        if check_off_button():
            return
        time.sleep_ms(10)
        
    silence_buzzer()

def sound_coin():
    play_note(988, 80)
    play_note(1319, 250)

def sound_happy():
    for note in [523, 659, 784]:
        play_note(note, 100)

sounds = [sound_coin, sound_happy]

# --- LIGHT ANIMATIONS ---

def arc_reactor():
    for i in range(8):
        np[i] = (0, 150, 255)
    show()
    for _ in range(20):
        if check_off_button(): return
        idx = random.randint(0,7)
        np[idx] = (255,255,255)
        show()
        time.sleep_ms(50)
        np[idx] = (0,150,255)

def eye():
    for pos in range(8):
        if check_off_button(): return
        turn_off_everything()
        np[pos] = (255, 255, 0)
        np[(pos-1)%8] = (30,30,30)
        np[(pos+1)%8] = (30,30,30)
        show()
        time.sleep_ms(120)

def fire():
    for _ in range(40):
        if check_off_button(): return
        for i in range(8):
            flicker = random.randint(100,255)
            np[i] = (flicker, flicker//3, 0)
        show()
        time.sleep_ms(60)

def heartbeat():
    for _ in range(3):
        if check_off_button(): return
        for i in range(8): np[i] = (255,0,0)
        show()
        time.sleep_ms(120)
        turn_off_everything()
        time.sleep_ms(80)
        for i in range(8): np[i] = (255,0,0)
        show()
        time.sleep_ms(120)
        turn_off_everything()
        time.sleep_ms(400)

def portal():
    for _ in range(25):
        if check_off_button(): return
        for i in range(8):
            for j in range(8): np[j] = (10,0,30)
            np[i] = (150, 0, 255)
            np[(i+4)%8] = (150, 0, 255)
            show()
            time.sleep_ms(50)

animations = [arc_reactor, eye, fire, heartbeat, portal]

# --- MAIN RUNTIME ---
turn_off_everything()
print("Calibrating PIR...")
time.sleep(10)
print("System Ready! Waiting for motion...")

while True:
    if button.value() == 0:
        turn_off_everything()
        print("System turned off via button.")
        while button.value() == 0:
            time.sleep_ms(50)
        time.sleep_ms(200) # Debounce
        
    elif pir.value() == 1:
        print("Motion detected!")
        random.choice(sounds)()
        
        if not check_off_button():
            random.choice(animations)()
        
        turn_off_everything()
        
        while pir.value() == 1:
            if check_off_button():
                break
            time.sleep_ms(100)
            
    time.sleep_ms(20)