import machine
import time
import random

BUTTON_PIN = 26
BUZZER_PIN = 33

button = machine.Pin(BUTTON_PIN, machine.Pin.IN, machine.Pin.PULL_UP)

def play_note(freq, duration_ms):
    # Create PWM on demand
    buzzer = machine.PWM(machine.Pin(BUZZER_PIN), freq=1000)
    buzzer.freq(freq)
    try:
        buzzer.duty(512) # Try legacy 10-bit duty
    except AttributeError:
        buzzer.duty_u16(32768) # Fallback to 16-bit
    
    time.sleep_ms(duration_ms)
    buzzer.deinit() # Completely release GPIO pin to turn sound off

def sound_coin():
    play_note(988, 80)
    play_note(1319, 250)

def sound_happy():
    for note in [523, 659, 784]:
        play_note(note, 100)

sounds = [sound_coin, sound_happy]

while True:
    if button.value() == 0:
        random.choice(sounds)()
        while button.value() == 0:
            time.sleep_ms(10)
    time.sleep_ms(20)