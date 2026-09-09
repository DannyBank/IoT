import uasyncio as asyncio
import time
import network
import random
import ubinascii
from machine import Pin
import neopixel
from umqtt.simple import MQTTClient

# --- WiFi & Broker Settings ---
SSID = "DBANK_WIFI"
PASSWORD = "D@@nn33ll1234"

SERVER = "hicxgzuqcf.localto.net"
PORT = 8800
USERNAME = "device_dev_Y7WP9mnveSUzKJdA"
PASSWORD_MQTT = "bQFn2lYoWadS98E86K7w0nD_n5V7Cja6IbAhAGav9rQ"

# --- Device & Command Topics ---
# Topic 1: Dedicated to Traffic Light commands
TOPIC_TRAFFIC = b"public/dbank/traffic"
# Topic 2: Dedicated to Ring Light commands
TOPIC_RING = b"public/dbank/ring"
# Topic 3: Global command (controls both)
TOPIC_ALL = b"public/dbank/all"

# Pin Definitions
RED_PIN = 12
AMBER_PIN = 13
GREEN_PIN = 14

red_led = Pin(RED_PIN, Pin.OUT)
amber_led = Pin(AMBER_PIN, Pin.OUT)
green_led = Pin(GREEN_PIN, Pin.OUT)

np = neopixel.NeoPixel(Pin(25, Pin.OUT), 8)

# State Control Flags & Async Tasks
traffic_running = False
ring_running = False
traffic_task = None
ring_task = None


def get_client_id():
    mac = ubinascii.hexlify(network.WLAN().config("mac")).decode()
    return f"esp32_dual_device_{mac[-6:]}"


# --- Traffic Light Logic (Non-blocking) ---
def turn_off_traffic():
    red_led.value(0)
    amber_led.value(0)
    green_led.value(0)

async def traffic_loop():
    global traffic_running
    print("🚦 Traffic Light sequence started...")
    try:
        while traffic_running:
            # RED
            turn_off_traffic()
            red_led.value(1)
            await asyncio.sleep(0.5)

            # GREEN
            turn_off_traffic()
            green_led.value(1)
            await asyncio.sleep(0.5)

            # AMBER
            turn_off_traffic()
            amber_led.value(1)
            await asyncio.sleep(1.0)
    finally:
        turn_off_traffic()
        print("🚦 Traffic Light stopped.")


# --- Ring Light Logic (Non-blocking) ---
def off_ring():
    for i in range(8):
        np[i] = (0, 0, 0)
    np.write()

async def ring_loop():
    global ring_running
    print("⭕ Ring Light Arc Reactor started...")
    try:
        while ring_running:
            for i in range(8):
                np[i] = (0, 150, 255)
            np.write()

            for _ in range(10):
                if not ring_running:
                    break
                idx = random.randint(0, 7)
                np[idx] = (255, 255, 255)
                np.write()
                await asyncio.sleep_ms(50)
                np[idx] = (0, 150, 255)
                np.write()
            await asyncio.sleep_ms(100)
    finally:
        off_ring()
        print("⭕ Ring Light stopped.")


# --- MQTT Message Handling ---
def on_message_received(topic, msg):
    global traffic_running, ring_running, traffic_task, ring_task

    topic_str = topic.decode()
    payload = msg.decode().strip().lower()
    print(f"\n📩 Topic: {topic_str} | Command: {payload}")

    # Handle Traffic Light commands
    if topic_str in ["public/dbank/traffic", "public/dbank/all"]:
        if payload == "start" and not traffic_running:
            traffic_running = True
            traffic_task = asyncio.create_task(traffic_loop())
        elif payload == "stop" and traffic_running:
            traffic_running = False

    # Handle Ring Light commands
    if topic_str in ["public/dbank/ring", "public/dbank/all"]:
        if payload == "start" and not ring_running:
            ring_running = True
            ring_task = asyncio.create_task(ring_loop())
        elif payload == "stop" and ring_running:
            ring_running = False


# --- Wi-Fi & Async MQTT Connection ---
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

async def mqtt_check_loop(client):
    """Periodically check for incoming MQTT messages without blocking tasks."""
    while True:
        try:
            client.check_msg()
        except Exception as e:
            print(f"MQTT Error: {e}")
        await asyncio.sleep_ms(100)  # Yield control back to asyncio loop


async def main():
    connect_wifi()

    client = MQTTClient(
        client_id=get_client_id(),
        server=SERVER,
        port=PORT,
        user=USERNAME,
        password=PASSWORD_MQTT,
        ssl=False,
    )

    client.set_callback(on_message_received)
    client.connect()
    print("Connected to Mosquitto Broker!")

    # Subscribe to separate target topics
    client.subscribe(TOPIC_TRAFFIC)
    client.subscribe(TOPIC_RING)
    client.subscribe(TOPIC_ALL)

    print("Subscribed to separate control topics.")

    # Start non-blocking MQTT loop
    await mqtt_check_loop(client)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Program stopped.")