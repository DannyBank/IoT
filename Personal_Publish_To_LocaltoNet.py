import time
import network
from umqtt.simple import MQTTClient

# --- Network & Broker Settings ---
SSID = "DBANK_WIFI"
PASSWORD = "D@@nn33ll1234"

SERVER = "hicxgzuqcf.localto.net"
PORT = 5280
CLIENT_ID = "esp32_publisher"
TOPIC = b"public/dbank"  # Topic as bytes
USERNAME = "device_dev_Y7WP9mnveSUzKJdA"
PASSWORD_MQTT = "bQFn2lYoWadS98E86K7w0nD_n5V7Cja6IbAhAGav9rQ"


def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print(f"Connecting to {SSID}...")
        wlan.connect(SSID, PASSWORD)
        while not wlan.isconnected():
            time.sleep(0.5)
            print(".", end="")
    print("\nConnected to Wi-Fi!")


def publish_message(message):
    client = MQTTClient(
        client_id=CLIENT_ID,
        server=SERVER,
        port=PORT,
        user=USERNAME,
        password=PASSWORD_MQTT,
        ssl=False,  # Keep False for LocalToNet plain TCP tunnels
    )

    try:
        print(f"Connecting to {SERVER}:{PORT}...")
        client.connect()

        print(f"Publishing: '{message}' to topic '{TOPIC.decode()}'")
        client.publish(TOPIC, message)

        print("Message sent successfully!")

        # Always disconnect cleanly
        client.disconnect()

    except Exception as e:
        print(f"Failed to publish: {e}")


def main():
    connect_wifi()

    # Publish a test message
    payload = "Why was i not seeing it before!"
    publish_message(payload)


if __name__ == "__main__":
    main()