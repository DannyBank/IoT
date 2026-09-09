import network
import socket
import select
import sys
import time
from machine import Pin, PWM

# ---------------------------------------------------------
# WI-FI SETUP
# ---------------------------------------------------------
WIFI_SSID = "DBANK_WIFI"
WIFI_PASS = "D@@nn33ll1234"

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(WIFI_SSID, WIFI_PASS)

print("Connecting to Wi-Fi...", end="")
while not wlan.isconnected():
    time.sleep(0.5)
    print(".", end="")

ip_address = wlan.ifconfig()[0]
print(f"\nConnected! ESP32 IP Address: {ip_address}")

# Setup UDP Socket listening on port 5005
UDP_PORT = 5005
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("0.0.0.0", UDP_PORT))
sock.setblocking(False)  # Non-blocking so the loop isn't delayed

# ---------------------------------------------------------
# BUZZER SETUP
# ---------------------------------------------------------
BUZZER_PIN = 13              # GPIO wired to buzzer
buzzer = PWM(Pin(BUZZER_PIN))
buzzer.duty(0)

# ---------------------------------------------------------
# FREQUENCY "PHYSICS"
# ---------------------------------------------------------
IDLE_FREQ = 200
MAX_FREQ = 2000
ACCEL_RATE = 0.06
DECAY_RATE = 0.035
DT_MS = 25
ON_DUTY = 512

current_freq = IDLE_FREQ
accelerating = False

# ---------------------------------------------------------
# MAIN LOOP
# ---------------------------------------------------------
try:
    while True:
        try:
            # Check for incoming UDP network packets
            data, addr = sock.recvfrom(1024)
            cmd = data.decode('utf-8')
            if cmd == '1':
                accelerating = True
            elif cmd == '0':
                accelerating = False
        except OSError:
            pass  # No packet received this tick

        if accelerating:
            current_freq += (MAX_FREQ - current_freq) * ACCEL_RATE
            current_freq = min(current_freq, MAX_FREQ)
        else:
            current_freq -= (current_freq - IDLE_FREQ) * DECAY_RATE
            current_freq = max(current_freq, IDLE_FREQ)

        if current_freq <= IDLE_FREQ + 2:
            buzzer.duty(0)
        else:
            buzzer.freq(int(current_freq))
            buzzer.duty(ON_DUTY)

        time.sleep_ms(DT_MS)

except KeyboardInterrupt:
    buzzer.duty(0)
    sock.close()