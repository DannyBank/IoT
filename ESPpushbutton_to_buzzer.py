from machine import Pin, PWM
import time

# Set up GPIO 15 as PWM output for the buzzer
buzzer = PWM(Pin(12))

# Set up GPIO 14 as input with an internal pull-up resistor
# Pin reads 1 (HIGH) when unpressed, 0 (LOW) when pressed
button = Pin(15, Pin.IN, Pin.PULL_UP)

# Define the frequency pitch (in Hz)
TONE_FREQ = 1000  

try:
    while True:
        if button.value() == 0:  # Button is pressed
            buzzer.freq(TONE_FREQ)
            buzzer.duty_u16(32768)  # Turn sound ON (50% duty cycle)
        else:  # Button is released
            buzzer.duty_u16(0)      # Turn sound OFF
            
        time.sleep(0.01)  # Small delay to prevent high CPU usage

except KeyboardInterrupt:
    # Clean up and ensure buzzer turns off when stopping the script
    buzzer.duty_u16(0)
    buzzer.deinit()