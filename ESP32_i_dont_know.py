from machine import Pin, PWM
import time
import sys
import select

# ---------------------------------------------------------
# BUZZER SETUP
# ---------------------------------------------------------
BUZZER_PIN = 13              # GPIO wired to buzzer

buzzer = PWM(Pin(BUZZER_PIN))
buzzer.duty(0)                # Start silent

# ---------------------------------------------------------
# FREQUENCY "PHYSICS"
# ---------------------------------------------------------
IDLE_FREQ = 200               # Hz, resting tone
MAX_FREQ = 2000               # Hz, full "gas pedal" tone
ACCEL_RATE = 0.06            # fraction of remaining gap closed per tick
DECAY_RATE = 0.035           # fraction of gap-to-idle closed per tick
DT_MS = 25
ON_DUTY = 512                 # ~50% duty cycle

current_freq = IDLE_FREQ
accelerating = False

# ---------------------------------------------------------
# MAIN LOOP
# ---------------------------------------------------------
try:
    while True:
        # Non-blocking check for serial commands sent from PC over USB
        if select.select([sys.stdin], [], [], 0)[0]:
            cmd = sys.stdin.read(1)
            if cmd == '1':
                accelerating = True
            elif cmd == '0':
                accelerating = False

        if accelerating:
            current_freq += (MAX_FREQ - current_freq) * ACCEL_RATE
            current_freq = min(current_freq, MAX_FREQ)
        else:
            current_freq -= (current_freq - IDLE_FREQ) * DECAY_RATE
            current_freq = max(current_freq, IDLE_FREQ)

        if current_freq <= IDLE_FREQ + 2:
            buzzer.duty(0)                     # Silent at rest
        else:
            buzzer.freq(int(current_freq))
            buzzer.duty(ON_DUTY)

        time.sleep_ms(DT_MS)

except KeyboardInterrupt:
    buzzer.duty(0)