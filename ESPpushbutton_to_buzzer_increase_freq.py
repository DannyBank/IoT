from machine import Pin, PWM
import time

# ---------------------------------------------------------
# PUSH BUTTON SETUP
#
# Wire one leg of the button to this GPIO, the other leg to
# GND. The internal pull-up resistor holds the pin HIGH when
# the button is not pressed, and pressing it pulls the pin
# LOW (this is why "pressed" == value() == 0 below).
# ---------------------------------------------------------
BUTTON_PIN = 15               # change to whichever GPIO your button is wired to

button = Pin(BUTTON_PIN, Pin.IN, Pin.PULL_UP)


# ---------------------------------------------------------
# BUZZER SETUP
# ---------------------------------------------------------
BUZZER_PIN = 13              # change to whichever GPIO your buzzer is wired to

buzzer = PWM(Pin(BUZZER_PIN))
buzzer.duty(0)                # start silent


# ---------------------------------------------------------
# FREQUENCY "PHYSICS" -- fast climb while held,
# slower coast back down on release.
# ---------------------------------------------------------
IDLE_FREQ = 200               # Hz, resting tone
MAX_FREQ = 2000               # Hz, full "gas pedal" tone
ACCEL_RATE = 0.06            # fraction of remaining gap closed per tick while held
DECAY_RATE = 0.035           # fraction of gap-to-idle closed per tick while released
DT_MS = 25

ON_DUTY = 512                 # ~50% duty (range is 0-1023 on ESP32 MicroPython)
DEBOUNCE_MS = 15               # ignore button changes faster than this

current_freq = IDLE_FREQ
accelerating = False

last_raw_state = button.value()
last_change_ms = time.ticks_ms()


def read_button():
    """Debounced read: returns True while the button is held down."""
    global last_raw_state, last_change_ms

    raw = button.value()
    now = time.ticks_ms()

    if raw != last_raw_state and time.ticks_diff(now, last_change_ms) > DEBOUNCE_MS:
        last_raw_state = raw
        last_change_ms = now

    return last_raw_state == 0   # LOW means pressed (pull-up wiring)


# ---------------------------------------------------------
# MAIN LOOP
# ---------------------------------------------------------
try:
    while True:
        accelerating = read_button()

        if accelerating:
            current_freq += (MAX_FREQ - current_freq) * ACCEL_RATE
            current_freq = min(current_freq, MAX_FREQ)
        else:
            current_freq -= (current_freq - IDLE_FREQ) * DECAY_RATE
            current_freq = max(current_freq, IDLE_FREQ)

        if current_freq <= IDLE_FREQ + 2:
            buzzer.duty(0)                     # effectively silent at rest
        else:
            buzzer.freq(int(current_freq))
            buzzer.duty(ON_DUTY)

        time.sleep_ms(DT_MS)

except KeyboardInterrupt:
    buzzer.duty(0)