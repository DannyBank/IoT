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
#   - Traffic light
#
# Device configuration:
#   Sensors   : None
#   Actuators : Traffic light
#   Network   : Configured
# -----------------------------------------------------------------------------
import json
import network
import ssl
import time
from machine import PWM, Pin
from umqtt.simple import MQTTClient

# USER CONFIGURATION: set these values before uploading to the board.
TRAFFIC_LIGHT_1_GROUNDPIN = "GND"
TRAFFIC_LIGHT_1_REDPIN = 12
TRAFFIC_LIGHT_1_YELLOWPIN = 13
TRAFFIC_LIGHT_1_GREENPIN = 14
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

# Load the CA Certificate from local storage
ca_bytes = None
try:
    with open(MQTT_CA_FILE, "rb") as f:
        ca_bytes = f.read()
    print(f"[SSL] Loaded certificate: {MQTT_CA_FILE}")
except Exception as e:
    print(f"[SSL] Error loading {MQTT_CA_FILE}: {e}")

# USER CODE: add custom setup, readings, or control logic in the marked sections.
ACTUATOR_STATE = {}
traffic_0_red = Pin(12, Pin.OUT, value=0)
traffic_0_yellow = Pin(13, Pin.OUT, value=0)
traffic_0_green = Pin(14, Pin.OUT, value=0)
ACTUATOR_STATE["traffic_light_1"] = {"red": False, "yellow": False, "green": False}


def read_components():
    return {"traffic_light_1": dict(ACTUATOR_STATE["traffic_light_1"])}


def apply_command(command):
    component = command.get("component")
    action = command.get("action")
    value = (command.get("parameters") or {}).get("value")
    if component == "traffic_light_1":
        if action not in ("red", "yellow", "green"):
            raise ValueError("Unsupported traffic-light action")
        ACTUATOR_STATE[component][action] = bool(value)
        traffic_0_red.value(ACTUATOR_STATE[component]["red"])
        traffic_0_yellow.value(ACTUATOR_STATE[component]["yellow"])
        traffic_0_green.value(ACTUATOR_STATE[component]["green"])
    else:
        raise ValueError("Unknown actuator component")
    return {"components": ACTUATOR_STATE}


def on_command(topic, message):
    print("[MQTT] Received on", topic, ":", message)
    command = json.loads(message)
    try:
        state = apply_command(command)
        result = {
            "commandId": command.get("commandId"),
            "status": "SUCCEEDED",
            "state": state,
        }
        print(
            "[DEVICE] Applied",
            command.get("component"),
            command.get("action"),
            (command.get("parameters") or {}).get("value"),
        )
    except Exception as error:
        result = {
            "commandId": command.get("commandId"),
            "status": "FAILED",
            "error": str(error),
        }
        print("[DEVICE] Command failed:", error)
    client.publish(RESULT_TOPIC, json.dumps(result))
    print("[MQTT] Result published:", result)


# Connect Wi-Fi
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

# Initialize and Connect MQTT Client
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
    now = time.ticks_ms()
    if time.ticks_diff(now, last_telemetry) >= 10000:
        telemetry = {"components": read_components()}
        client.publish(TELEMETRY_TOPIC, json.dumps(telemetry))
        print("[MQTT] Telemetry published:", telemetry)
        last_telemetry = now
    time.sleep_ms(20)