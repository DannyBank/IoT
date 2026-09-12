import os
import sys

# Force current directory into Windows PATH before importing pydub
current_dir = os.path.dirname(os.path.abspath(__file__))
os.environ["PATH"] = current_dir + os.pathsep + os.environ.get("PATH", "")

import socket
import time
from pydub import AudioSegment

# --- CONFIGURATION ---
ESP32_IP = '192.168.8.140'  # Replace with your ESP32's Wi-Fi IP address
PORT = 5000
AUDIO_FILE = 'Koffee_Rapture.mp3'

def stream_audio_wifi(ip, port, filename):
    print(f"Loading and processing {filename}...")
    
    # Load audio using pydub/ffmpeg
    audio = AudioSegment.from_file(filename)
    audio = audio.set_frame_rate(8000).set_channels(1).set_sample_width(1)
    raw_samples = audio.raw_data

    print(f"Connecting to ESP32 at {ip}:{port} over Wi-Fi...")
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((ip, port))
    print("Connected! Streaming audio...")

    chunk_size = 512
    sample_delay = 1.0 / 8000.0  # Timing control for 8kHz pacing

    try:
        for i in range(0, len(raw_samples), chunk_size):
            chunk = raw_samples[i:i + chunk_size]
            client_socket.sendall(chunk)
            time.sleep(len(chunk) * sample_delay)
            
    except Exception as e:
        print("Streaming error:", e)
    finally:
        print("Finished playing.")
        client_socket.close()

if __name__ == "__main__":
    stream_audio_wifi(ESP32_IP, PORT, AUDIO_FILE)