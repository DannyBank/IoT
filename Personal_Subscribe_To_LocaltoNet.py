import time
import network
from umqtt.simple import MQTTClient
from machine import Pin
import neopixel

# --- Network & Broker Settings ---
SSID = "DBANK_WIFI"
PASSWORD = "D@@nn33ll1234"

SERVER = "hicxgzuqcf.localto.net"
PORT = 4953
CLIENT_ID = "esp32_subscriber"
TOPIC = b"public/dbank"  # Topic must be bytes
USERNAME = "device_dev_Y7WP9mnveSUzKJdA"
PASSWORD_MQTT = "bQFn2lYoWadS98E86K7w0nD_n5V7Cja6IbAhAGav9rQ"

# Pin Definitions
RED_PIN = 12
AMBER_PIN = 13
GREEN_PIN = 14

# Initialize Pins as Outputs
red_led = Pin(RED_PIN, Pin.OUT)
amber_led = Pin(AMBER_PIN, Pin.OUT)
green_led = Pin(GREEN_PIN, Pin.OUT)

np = neopixel.NeoPixel(Pin(25, Pin.OUT), 8)

def show():
    np.write()

def off():
    for i in range(8):
        np[i] = (0,0,0)
    show()

# 1. ARC REACTOR - Iron Man
def arc_reactor():
    while True:
        for i in range(8):
            np[i] = (0, 150, 255)
        show()
        for _ in range(30):
            # random sparkle
            idx = random.randint(0,7)
            np[idx] = (255,255,255)
            show()
            time.sleep_ms(50)
            np[idx] = (0,150,255)
        off()
        
def run_ringlight():
    while True:
            # Random creative idle mode
            mode = random.choice([arc_reactor])
            print("Mode:", mode.__name__)
            mode()
            time.sleep_ms(500)

def turn_off_all():
    """Utility function to reset all LEDs to off state."""
    red_led.value(0)
    amber_led.value(0)
    green_led.value(0)

def run_traffic():
    while True:
        # 1. STOP: Red Light ON
        turn_off_all()
        red_led.value(1)
        print("State: RED (Stop)")
        time.sleep(0.5)  # Hold Red for 5 seconds

        # 2. GO: Green Light ON
        turn_off_all()
        green_led.value(1)
        print("State: GREEN (Go)")
        time.sleep(0.5)  # Hold Green for 5 seconds

        # 3. CAUTION: Amber Light ON
        turn_off_all()
        amber_led.value(1)
        print("State: AMBER (Prepare to Stop)")
        time.sleep(1)  # Hold Amber for 2 seconds

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


# Callback function triggered when a message arrives
def on_message_received(topic, msg):
    print(f"\n📩 Message received!")
    print(f"   Topic:   {topic.decode()}")
    print(f"   Payload: {msg.decode()}")
    if msg.decode() == "traffic":
        run_traffic()
    if msg.decode() == "ring":
        run_ringlight()

def main():
    connect_wifi()

    client = MQTTClient(
        client_id=CLIENT_ID,
        server=SERVER,
        port=PORT,
        user=USERNAME,
        password=PASSWORD_MQTT,
        ssl=False,
    )

    # Attach the callback function to handle incoming messages
    client.set_callback(on_message_received)

    try:
        print(f"Connecting to {SERVER}:{PORT}...")
        client.connect()
        print("Connected successfully!")

        # Subscribe to the topic
        client.subscribe(TOPIC)
        print(f"Subscribed to topic: '{TOPIC.decode()}'")
        print("Waiting for messages... (Press Ctrl+C to stop)")

        # Continuous listening loop
        while True:
            client.check_msg()  # Non-blocking check for new messages
            time.sleep(0.1)  # Keeps CPU load low

    except KeyboardInterrupt:
        print("\nStopping subscriber...")
        client.disconnect()
    except Exception as e:
        print(f"Connection error: {e}")


if __name__ == "__main__":
    main()