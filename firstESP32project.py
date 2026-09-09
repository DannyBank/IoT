import json
import time
import network
import ssl
from umqtt.simple import MQTTClient
from random import uniform

# --- CONFIGURATION ---
SSID = "DBANK_WIFI"
PASSWORD = "D@@nn33ll1234"

SERVER = "mqtt.iotworkshop.africa"
PORT = 8883
CLIENT_ID = "dev_Y7WP9mnveSUzKJdA"
USERNAME = "device_dev_Y7WP9mnveSUzKJdA"
PASSWORD_MQTT = "bQFn2lYoWadS98E86K7w0nD_n5V7Cja6IbAhAGav9rQ"
TELEMETRY_TOPIC = "dev_Y7WP9mnveSUzKJdA/data"

# --- HELPER FUNCTIONS ---
def connect_wifi():
    """Establishes connection to the Wi-Fi network."""
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    if not wlan.isconnected():
        print(f"Connecting to {SSID}...")
        wlan.connect(SSID, PASSWORD)
        
        timeout = 10
        start_time = time.time()
        
        while not wlan.isconnected():
            if time.time() - start_time > timeout:
                print("\nConnection failed: Timed out.")
                return False
            time.sleep(0.5)
            print(".", end="")
            
    print("\nConnected to Wi-Fi successfully!")
    print("Network config:", wlan.ifconfig())
    return True

def read_components():
    """Generates dummy telemetry data (Replace with actual sensor reads)."""
    return {
      "dhtx_1": {
        "temperature": round(uniform(10.5, 100.5), 2),
        "humidity": round(uniform(50.1, 500.9), 2)
      }
    }

# --- MAIN EXECUTION ---
def main():
    # Step 1: Ensure Wi-Fi is connected
    if not connect_wifi():
        print("Aborting: Could not connect to Wi-Fi.")
        return

    # Step 2: Initialize MQTT Client
    client = MQTTClient(
        client_id=CLIENT_ID,
        server=SERVER,
        port=PORT,
        user=USERNAME,
        password=PASSWORD_MQTT,
        ssl=True,
        ssl_params={"server_hostname": SERVER}
    )

    # Step 3: Connect to Broker & Publish Loop
    try:
        print("Connecting to MQTT broker(IOTConnect)...")
        client.connect()
        print("Connection Established!")

        while True:
            payload = json.dumps({"components": read_components()})
            client.publish(TELEMETRY_TOPIC, payload, qos=1)
            print("Published telemetry:", payload)
            time.sleep(10)

    except KeyboardInterrupt:
        print("\nStopping script...")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
    finally:
        print("Disconnecting MQTT client...")
        try:
            client.disconnect()
        except Exception:
            pass
        print("Done.")

if __name__ == "__main__":
    main()