import socket
import network
import time
from machine import Pin, PWM

# --- CONFIGURATION ---
WIFI_SSID = "DBANK_WIFI"
WIFI_PASS = "D@@nn33ll1234"
PORT = 5000
AUDIO_PIN = 16

# Setup High-Speed PWM for Audio Output
pwm = PWM(Pin(AUDIO_PIN))
pwm.freq(100000)  # 100 kHz PWM carrier
pwm.duty_u16(0)

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print(f"Connecting to {WIFI_SSID}...")
        wlan.connect(WIFI_SSID, WIFI_PASS)
        while not wlan.isconnected():
            time.sleep(0.5)
    print("Wi-Fi Connected!")
    print("ESP32 IP Address:", wlan.ifconfig()[0])
    return wlan.ifconfig()[0]

def start_audio_server():
    ip = connect_wifi()
    
    # Create TCP Socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('0.0.0.0', PORT))
    server_socket.listen(1)
    
    print(f"Audio server listening on {ip}:{PORT}...")

    while True:
        conn, addr = server_socket.accept()
        print(f"Connection received from {addr[0]}")
        
        try:
            while True:
                # Receive audio byte chunks over Wi-Fi
                chunk = conn.recv(512)
                if not chunk:
                    break
                
                for sample in chunk:
                    # Convert 8-bit sample (0-255) to 16-bit PWM duty cycle
                    pwm.duty_u16(sample * 257)
                    
        except Exception as e:
            print("Client disconnected or error:", e)
        finally:
            conn.close()
            pwm.duty_u16(0)
            print("Waiting for next connection...")

if __name__ == "__main__":
    try:
        start_audio_server()
    except KeyboardInterrupt:
        pwm.duty_u16(0)
        pwm.deinit()