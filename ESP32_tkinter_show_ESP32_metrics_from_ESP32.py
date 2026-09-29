import gc
import json
import socket
import time
import network
import machine
import esp
import esp32

# --- 1. Access Point Configuration ---
AP_SSID = "DBANK_WIFI_ESP32"
AP_PASSWORD = "D@@nn33ll12345"  # Minimum 8 characters
PORT = 5000

# Setup Wi-Fi AP Mode
ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid=AP_SSID, password=AP_PASSWORD)

print("Access Point Started!")
print("SSID    :", AP_SSID)
print("IP Addr :", ap.ifconfig()[0])  # Default is usually 192.168.4.1


# --- 2. Metric Gathering Helper ---
def get_metrics_json():
    gc.collect()

    free_ram = gc.mem_free()
    total_ram = free_ram + gc.mem_alloc()
    cpu_freq = machine.freq() // 1000000

    try:
        temp_f = esp32.raw_temperature()
        temp_c = (temp_f - 32) * 5 / 9
    except Exception:
        temp_c = 0.0

    metrics = {
        "temp_c": round(temp_c, 1),
        "cpu_freq": cpu_freq,
        "free_ram_kb": round(free_ram / 1024, 1),
        "total_ram_kb": round(total_ram / 1024, 1),
        "flash_mb": round(esp.flash_size() / (1024 * 1024), 2),
    }

    return json.dumps(metrics) + "\n"


# --- 3. TCP Server Setup ---
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(("0.0.0.0", PORT))
server_socket.listen(1)

print(f"Metrics Socket Server listening on port {PORT}...")

while True:
    try:
        conn, addr = server_socket.accept()
        print("Dashboard connected from:", addr)

        while True:
            # Generate and stream metric payload every 1 second
            data = get_metrics_json()
            conn.send(data.encode("utf-8"))
            time.sleep(1)

    except Exception as e:
        print("Connection closed or dropped:", e)
        try:
            conn.close()
        except Exception:
            pass