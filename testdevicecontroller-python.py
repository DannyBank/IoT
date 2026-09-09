# -----------------------------------------------------------------------------
# IoTConnect Device Application
#
# Project   : TestDeviceController
# Generated : Automatically by IoTConnect
# Platform  : Python
# Copyright : 2026 IoTDevLab
# License   : MIT (SPDX-License-Identifier: MIT)
#
# This file was generated automatically.
# Changes made directly to this file may be overwritten when regenerated.
#
# Required drivers:
#   - DHTx
#
# Device configuration:
#   Sensors   : DHTx
#   Actuators : None
#   Network   : Configured
# -----------------------------------------------------------------------------
# MQTT 5. Install: pip install paho-mqtt
# DHTx (DHTx): {"interface":"GPIO","powerPin":"3V3","groundPin":"GND","dataPin":"2"}
import json, time
#import paho.mqtt.client as mqtt
from random import uniform
import ssl
from umqtt.simple import MQTTClient as mqtt

# USER CONFIGURATION: update network credentials and hardware settings.
DHTX_1_POWERPIN = "3V3"
DHTX_1_GROUNDPIN = "GND"
DHTX_1_DATAPIN = 2
BROKER_URL = "mqtts://mqtt.iotworkshop.africa:8883"
USERNAME = "device_dev_Y7WP9mnveSUzKJdA"
PASSWORD = "bQFn2lYoWadS98E86K7w0nD_n5V7Cja6IbAhAGav9rQ"
TELEMETRY_TOPIC = "dev_Y7WP9mnveSUzKJdA/data"

def read_components():
    # USER CODE: replace placeholders with readings from the listed hardware.
    return {
      "dhtx_1": {
        "temperature": round(uniform(10.5, 100.5), 2),
        "humidity": round(uniform(50.1, 500.9), 2)
      }
    }

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="dev_Y7WP9mnveSUzKJdA", protocol=mqtt.MQTTv5)
client.username_pw_set(USERNAME, PASSWORD)
client.tls_set(cert_reqs=ssl.CERT_NONE)
client.connect("mqtt.iotworkshop.africa", 8883)
client.loop_start()
while True:
    client.publish(TELEMETRY_TOPIC, json.dumps({"components": read_components()}), qos=1)
    time.sleep(10)
