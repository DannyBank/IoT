import machine
import time
import random

# Hardware Configuration
PIR_PIN = 32
BUZZER_PIN = 33

# PIR Sensor Input Pin
pir = machine.Pin(PIR_PIN, machine.Pin.IN)

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

print("Warming up PIR sensor...")
time.sleep(15)  # PIR sensor warmup delay
print("System Ready! Waiting for motion...")

while True:
    # PIR outputs HIGH (1) when motion is detected
    if pir.value() == 1:
        print("Motion detected! Playing sound...")
        random.choice(sounds)()
        
        # Debounce/Cooldown: Wait until motion signal goes LOW or hold briefly
        while pir.value() == 1:
            time.sleep_ms(100)
            
    time.sleep_ms(20)