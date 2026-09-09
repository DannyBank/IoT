# -----------------------------------------------------------------------------
# IoTConnect Device Application
#
# Project   : Traffic1
# Generated : Automatically by IoTConnect
# Platform  : MicroPython
# Copyright : 2026 IoTDevLab
# License   : MIT (SPDX-License-Identifier: MIT)
#
# This file was generated automatically.
# Changes made directly to this file may be overwritten when regenerated.
#
# Required drivers:
#   - Traffic light, WS2812 RGB LED Ring
#
# Device configuration:
#   Sensors   : None
#   Actuators : Traffic light, WS2812 RGB LED Ring
#   Network   : Configured
# -----------------------------------------------------------------------------
# MQTT protocol: 3.1.1 compatibility (umqtt.simple does not implement MQTT 5).
# Install any hardware driver modules named below before uploading this file.
# Traffic light (Traffic light): {"wires":{"redPin":{"source":{"x":229.6667445310908,"y":107.4999942751081},"target":{"x":342,"y":315},"waypoints":[{"x":277.6667445310908,"y":107.4999942751081},{"x":277.6667445310908,"y":315}]},"greenPin":{"source":{"x":229.6667445310908,"y":149.500007168442},"target":{"x":342,"y":336},"waypoints":[{"x":256,"y":149.500007168442},{"x":256,"y":336}]},"groundPin":{"source":{"x":229.6667445310908,"y":86.5000276790957},"target":{"x":342,"y":273},"waypoints":[{"x":294,"y":86.5000276790957},{"x":294,"y":273}]},"yellowPin":{"source":{"x":229.6667445310908,"y":128.5000140053266},"target":{"x":342,"y":294},"waypoints":[{"x":304,"y":128.5000140053266},{"x":304,"y":294}]}},"viewport":{"x":84.54132715041328,"y":174.917988271987,"zoom":0.5743491774985174},"interface":"GPIO","wireModes":{"redPin":"auto","greenPin":"auto","groundPin":"auto","yellowPin":"auto"},"wireColors":{},"portAnchors":{"redPin":"left:3","greenPin":"left:4","groundPin":"left:1","yellowPin":"left:2"},"groundPin":"GND","redPin":"12","yellowPin":"13","greenPin":"14"}
# WS2812 RGB LED Ring (WS2812 RGB LED Ring): {"wires":{},"viewport":{"x":19.87464013869453,"y":180.2513012602683,"zoom":0.5743491774985174},"interface":"WS2812","ringCount":"1","wireModes":{"dataPin":"auto","powerPin":"auto","groundPin":"auto"},"wireColors":{},"ledsPerRing":"8","portAnchors":{"dataPin":"right:7","powerPin":"right:0","groundPin":"right:1"},"powerPin":"3V3","groundPin":"GND","dataPin":"25"}
import json, time, network, ssl
from umqtt.simple import MQTTClient
from machine import Pin, PWM
import neopixel
import random

# USER CONFIGURATION: set these values before uploading to the board.
TRAFFIC_LIGHT_1_GROUNDPIN = "GND"
TRAFFIC_LIGHT_1_REDPIN = 12
TRAFFIC_LIGHT_1_YELLOWPIN = 13
TRAFFIC_LIGHT_1_GREENPIN = 14
WS2812_RGB_LED_RING_1_POWERPIN = "3V3"
WS2812_RGB_LED_RING_1_GROUNDPIN = "GND"
WS2812_RGB_LED_RING_1_DATAPIN = 25
WIFI_SSID = "DBANK_WIFI"
WIFI_PASSWORD = "D@@nn33ll1234"
MQTT_HOST = "mqtt.iotworkshop.africa"
MQTT_PORT = 8883
MQTT_USER = "device_dev_leohiCc-bnwe0sbM".encode()
MQTT_PASSWORD = "pN_zNVwovV3-XJrXJRnatvYr-Wv7WrdJkjshy0iiWrE".encode()
MQTT_CA_FILE = "mqtt-ca.crt"
TELEMETRY_TOPIC = "dev_leohiCc-bnwe0sbM/data".encode()
COMMAND_TOPIC = "dev_leohiCc-bnwe0sbM/cmd".encode()
RESULT_TOPIC = "dev_leohiCc-bnwe0sbM/result".encode()

# USER CODE: add custom setup, readings, or control logic in the marked sections.
ACTUATOR_STATE = {}
RING_PIXELS = {}
RING_LAST_CHANGE = {}
RING_STEP = {}
traffic_0_red = Pin(12, Pin.OUT, value=0)
traffic_0_yellow = Pin(13, Pin.OUT, value=0)
traffic_0_green = Pin(14, Pin.OUT, value=0)
ACTUATOR_STATE["traffic_light_1"] = {"red": False, "yellow": False, "green": False}
ring_1_total = 8
ring_1 = neopixel.NeoPixel(Pin(25), ring_1_total)
RING_PIXELS["ws2812_rgb_led_ring_1"] = [(255, 255, 255)] * ring_1_total
RING_LAST_CHANGE["ws2812_rgb_led_ring_1"] = time.ticks_ms()
RING_STEP["ws2812_rgb_led_ring_1"] = 0
ACTUATOR_STATE["ws2812_rgb_led_ring_1"] = {"power": False, "brightness": 50, "color": "#ffffff", "pixel_index": 0, "pixel_color": "#ffffff", "effect": "SOLID", "random": False, "interval": 0.15}

# Load the CA Certificate from local storage
ca_bytes = None
try:
    with open(MQTT_CA_FILE, "rb") as f:
        ca_bytes = f.read()
    print(f"[SSL] Loaded certificate: {MQTT_CA_FILE}")
except Exception as e:
    print(f"[SSL] Error loading {MQTT_CA_FILE}: {e}")

def parse_ring_color_1(value):
    color = str(value)
    if len(color) != 7 or color[0] != "#": raise ValueError("Color must use #RRGGBB")
    number = int(color[1:], 16)
    return color.lower(), ((number >> 16) & 255, (number >> 8) & 255, number & 255)
def write_ring_1():
    state = ACTUATOR_STATE["ws2812_rgb_led_ring_1"]
    scale = state["brightness"] / 100 if state["power"] else 0
    for led_index, rgb in enumerate(RING_PIXELS["ws2812_rgb_led_ring_1"]):
        ring_1[led_index] = tuple(int(level * scale) for level in rgb)
    ring_1.write()
write_ring_1()
def ring_wheel(position):
    position %= 256
    if position < 85: return (255 - position * 3, position * 3, 0)
    if position < 170:
        position -= 85
        return (0, 255 - position * 3, position * 3)
    position -= 170
    return (position * 3, 0, 255 - position * 3)

def update_actuators():
    now = time.ticks_ms()

    state = ACTUATOR_STATE["ws2812_rgb_led_ring_1"]
    animated = state["random"] or state["effect"] in ("RAINBOW", "CHASE", "SPARKLE", "DISCO", "COMET")
    if state["power"] and animated and time.ticks_diff(now, RING_LAST_CHANGE["ws2812_rgb_led_ring_1"]) >= int(state["interval"] * 1000):
        if state["random"]:
            RING_PIXELS["ws2812_rgb_led_ring_1"] = [(random.getrandbits(8), random.getrandbits(8), random.getrandbits(8)) for unused in range(ring_1_total)]
        elif state["effect"] == "RAINBOW":
            RING_PIXELS["ws2812_rgb_led_ring_1"] = [ring_wheel(int(led * 256 / ring_1_total) + RING_STEP["ws2812_rgb_led_ring_1"]) for led in range(ring_1_total)]
        elif state["effect"] == "CHASE":
            unused, rgb = parse_ring_color_1(state["color"])
            RING_PIXELS["ws2812_rgb_led_ring_1"] = [(0, 0, 0)] * ring_1_total
            RING_PIXELS["ws2812_rgb_led_ring_1"][RING_STEP["ws2812_rgb_led_ring_1"] % ring_1_total] = rgb
        elif state["effect"] == "SPARKLE":
            RING_PIXELS["ws2812_rgb_led_ring_1"] = [(0, 0, 0)] * ring_1_total
            RING_PIXELS["ws2812_rgb_led_ring_1"][random.getrandbits(16) % ring_1_total] = (random.getrandbits(8), random.getrandbits(8), random.getrandbits(8))
        elif state["effect"] == "DISCO":
            palette = ((255, 0, 100), (0, 255, 220), (255, 210, 0), (120, 0, 255), (0, 255, 40), (255, 45, 0))
            RING_PIXELS["ws2812_rgb_led_ring_1"] = [palette[random.getrandbits(8) % len(palette)] if random.getrandbits(2) else (0, 0, 0) for unused in range(ring_1_total)]
        elif state["effect"] == "COMET":
            unused, rgb = parse_ring_color_1(state["color"])
            head = RING_STEP["ws2812_rgb_led_ring_1"] % ring_1_total
            RING_PIXELS["ws2812_rgb_led_ring_1"] = [tuple(int(level * max(0, 1 - ((led - head) % ring_1_total) / 5)) for level in rgb) for led in range(ring_1_total)]
        RING_STEP["ws2812_rgb_led_ring_1"] = (RING_STEP["ws2812_rgb_led_ring_1"] + 1) % 256
        RING_LAST_CHANGE["ws2812_rgb_led_ring_1"] = now
        write_ring_1()

def read_components():
    return {
        "traffic_light_1": dict(ACTUATOR_STATE["traffic_light_1"]),
        "ws2812_rgb_led_ring_1": dict(ACTUATOR_STATE["ws2812_rgb_led_ring_1"])
    }

def apply_command(command):
    component = command.get("component")
    action = command.get("action")
    value = (command.get("parameters") or {}).get("value")
    if component == "traffic_light_1":
        if action not in ("red", "yellow", "green"): raise ValueError("Unsupported traffic-light action")
        ACTUATOR_STATE[component][action] = bool(value)
        traffic_0_red.value(ACTUATOR_STATE[component]["red"])
        traffic_0_yellow.value(ACTUATOR_STATE[component]["yellow"])
        traffic_0_green.value(ACTUATOR_STATE[component]["green"])
    elif component == "ws2812_rgb_led_ring_1":
        state = ACTUATOR_STATE[component]
        if action == "power":
            state["power"] = bool(value)
        elif action == "brightness":
            state["brightness"] = max(0, min(100, float(value)))
        elif action == "color":
            color, rgb = parse_ring_color_1(value)
            state["color"] = color
            state["effect"] = "SOLID"
            state["random"] = False
            RING_PIXELS[component] = [rgb] * ring_1_total
        elif action == "pixel_index":
            state["pixel_index"] = max(0, min(ring_1_total - 1, int(value)))
        elif action == "pixel_color":
            color, rgb = parse_ring_color_1(value)
            state["pixel_color"] = color
            state["effect"] = "CUSTOM"
            state["random"] = False
            RING_PIXELS[component][state["pixel_index"]] = rgb
        elif action == "effect":
            effect = str(value).upper()
            if effect not in ("SOLID", "CUSTOM", "RAINBOW", "CHASE", "SPARKLE", "DISCO", "COMET"): raise ValueError("Unsupported WS2812 effect")
            state["effect"] = effect
            state["random"] = False
            RING_STEP[component] = 0
            RING_LAST_CHANGE[component] = time.ticks_ms() - int(state["interval"] * 1000)
            if effect == "SOLID":
                unused, rgb = parse_ring_color_1(state["color"])
                RING_PIXELS[component] = [rgb] * ring_1_total
        elif action == "random":
            state["random"] = bool(value)
            RING_LAST_CHANGE[component] = time.ticks_ms() - int(state["interval"] * 1000)
        elif action == "interval":
            state["interval"] = max(0.05, min(60, float(value)))
        else:
            raise ValueError("Unsupported WS2812 ring action")
        write_ring_1()
    else:
        raise ValueError("Unknown actuator component")
    return {"components": ACTUATOR_STATE}

def on_command(topic, message):
    print("[MQTT] Received on", topic, ":", message)
    command = json.loads(message)
    try:
        state = apply_command(command)
        result = {"commandId": command.get("commandId"), "status": "SUCCEEDED", "state": state}
        print("[DEVICE] Applied", command.get("component"), command.get("action"), (command.get("parameters") or {}).get("value"))
    except Exception as error:
        result = {"commandId": command.get("commandId"), "status": "FAILED", "error": str(error)}
        print("[DEVICE] Command failed:", error)
    client.publish(RESULT_TOPIC, json.dumps(result))
    print("[MQTT] Result published:", result)

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
print("[WIFI] Connecting to", WIFI_SSID)
wlan.connect(WIFI_SSID, WIFI_PASSWORD)
while not wlan.isconnected():
    time.sleep_ms(250)
print("[WIFI] Connected:", wlan.ifconfig())

# Prepare SSL Parameters
ssl_params = {
    "server_hostname": MQTT_HOST,
    "cert_reqs": ssl.CERT_REQUIRED if ca_bytes else ssl.CERT_NONE,
}

if ca_bytes:
    ssl_params["cadata"] = ca_bytes

client = MQTTClient(
    "dev_leohiCc-bnwe0sbM".encode(),
    MQTT_HOST,
    port=MQTT_PORT,
    user=MQTT_USER,
    password=MQTT_PASSWORD,
    ssl=True,
    ssl_params=ssl_params,
)
client.set_callback(on_command)
print("[MQTT] Connecting to {}:{}".format(MQTT_HOST, MQTT_PORT))
client.connect()
print("[MQTT] Connected")
client.subscribe(COMMAND_TOPIC)
print("[MQTT] Subscribed:", COMMAND_TOPIC)
last_telemetry = time.ticks_ms() - 10000
while True:
    client.check_msg()
    update_actuators()
    now = time.ticks_ms()
    if time.ticks_diff(now, last_telemetry) >= 10000:
        telemetry = {"components": read_components()}
        client.publish(TELEMETRY_TOPIC, json.dumps(telemetry))
        print("[MQTT] Telemetry published:", telemetry)
        last_telemetry = now
    time.sleep_ms(20)
