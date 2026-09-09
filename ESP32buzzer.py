from machine import Pin, PWM
import time

# Set up GPIO 15 as a PWM pin
buzzer = PWM(Pin(13))

def play_tone(frequency, duration):
    buzzer.freq(frequency)  # Set tone pitch (Hz)
    buzzer.duty_u16(32768)  # Set 50% duty cycle (turns sound on)
    time.sleep(duration)
    buzzer.duty_u16(0)      # Set 0% duty cycle (turns sound off)

while True:
    # Turn sound on (1000 Hz tone for 1 second)
    play_tone(1000, 1.0)

    time.sleep(0.5) # Short pause

    # Play a higher pitch sound (2000 Hz tone for 0.5 seconds)
    play_tone(2000, 0.5)

    # Turn sound on (1000 Hz tone for 1 second)
    play_tone(1000, 1.0)

    time.sleep(0.5) # Short pause

    # Play a higher pitch sound (2000 Hz tone for 0.5 seconds)
    play_tone(2000, 0.5)

# Ensure buzzer is completely off
buzzer.deinit()