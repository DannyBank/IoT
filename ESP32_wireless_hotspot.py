import network
import time

def start_hotspot(ssid="ESP32-Hotspot", password="password123"):
    # Initialize the Access Point interface
    ap = network.WLAN(network.AP_IF)
    
    # Activate the AP interface
    ap.active(True)
    
    # Configure SSID, Password, and Security
    # WPA2 Security requires a password with at least 8 characters
    if password:
        ap.config(essid=ssid, password=password, authmode=network.AUTH_WPA_WPA2_PSK)
    else:
        ap.config(essid=ssid, authmode=network.AUTH_OPEN)
        
    # Wait until the interface is active
    while not ap.active():
        time.sleep(0.1)
        
    print(f"Hotspot active!")
    print(f"SSID: {ssid}")
    print(f"IP Configuration: {ap.ifconfig()}")

# Run the function
start_hotspot()