import socket
import time
import wave

ESP32_IP = '192.168.8.140'
PORT = 5000
AUDIO_FILE = 'Koffee_Rapture.wav'

def stream_wav_wifi(ip, port, filename):
    print(f"Loading {filename}...")
    with wave.open(filename, 'rb') as wf:
        raw_samples = wf.readframes(wf.getnframes())

    print(f"Connecting to ESP32 at {ip}:{port}...")
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((ip, port))
    print("Streaming WAV audio...")

    chunk_size = 512
    sample_delay = 1.0 / 8000.0

    try:
        for i in range(0, len(raw_samples), chunk_size):
            chunk = raw_samples[i:i + chunk_size]
            client_socket.sendall(chunk)
            time.sleep(len(chunk) * sample_delay)
    finally:
        client_socket.close()

if __name__ == "__main__":
    stream_wav_wifi(ESP32_IP, PORT, AUDIO_FILE)