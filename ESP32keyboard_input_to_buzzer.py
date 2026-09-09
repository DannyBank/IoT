from machine import Pin, PWM
import time
import sys
import select

# ---------------------------------------------------------
# BUZZER SETUP
# ---------------------------------------------------------
BUZZER_PIN = 13            # change to whichever GPIO your buzzer is wired to

buzzer = PWM(Pin(BUZZER_PIN))
buzzer.duty(0)              # start silent


# ---------------------------------------------------------
# FREQUENCY "PHYSICS" -- same easing shape as the tachometer:
# fast climb while held, slower coast back down on release.
# ---------------------------------------------------------
IDLE_FREQ = 200              # Hz, resting tone
MAX_FREQ = 2000              # Hz, full "gas pedal" tone
ACCEL_RATE = 0.06           # fraction of remaining gap closed per tick while held
DECAY_RATE = 0.035          # fraction of gap-to-idle closed per tick while released
DT_MS = 25

ON_DUTY = 512                # ~50% duty (range is 0-1023 on ESP32 MicroPython)

current_freq = IDLE_FREQ
accelerating = False


# ---------------------------------------------------------
# NON-BLOCKING SERIAL INPUT
#
# The host PC sends single characters over the same USB
# serial connection used for the REPL:
#   '1'  -> spacebar/button pressed   (start accelerating)
#   '0'  -> spacebar/button released  (start decaying)
# ---------------------------------------------------------
poll = select.poll()
poll.register(sys.stdin, select.POLLIN)


def read_commands():
    global accelerating
    while poll.poll(0):
        ch = sys.stdin.read(1)
        if ch == "1":
            accelerating = True
        elif ch == "0":
            accelerating = False


# ---------------------------------------------------------
# MAIN LOOP
# ---------------------------------------------------------
try:
    while True:
        read_commands()

        if accelerating:
            current_freq += (MAX_FREQ - current_freq) * ACCEL_RATE
            current_freq = min(current_freq, MAX_FREQ)
        else:
            current_freq -= (current_freq - IDLE_FREQ) * DECAY_RATE
            current_freq = max(current_freq, IDLE_FREQ)

        if current_freq <= IDLE_FREQ + 2:
            buzzer.duty(0)                    # effectively silent at rest
        else:
            buzzer.freq(int(current_freq))
            buzzer.duty(ON_DUTY)

        time.sleep_ms(DT_MS)

except KeyboardInterrupt:
    buzzer.duty(0)