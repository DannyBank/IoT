# -----------------------------------------------------------------------------
# IoTConnect Device Application
#
# Project   : AnotherDeviceController
# Generated : Automatically by IoTConnect
# Platform  : Python
# Copyright : 2026 IoTDevLab
# License   : MIT (SPDX-License-Identifier: MIT)
#
# This file was generated automatically.
# Changes made directly to this file may be overwritten when regenerated.
#
# Required drivers:
#   - PIR
#
# Device configuration:
#   Sensors   : PIR
#   Actuators : None
#   Network   : Configured
# -----------------------------------------------------------------------------
# MQTT 5. Install: pip install paho-mqtt
# PIR (PIR): {"wires":{},"viewport":{"x":-12.10835599202647,"y":243.6224668942903,"zoom":0.5743491774985174},"interface":"GPIO","wireModes":{"powerPin":"auto","groundPin":"auto"},"portAnchors":{"powerPin":"left:0","groundPin":"right:2"},"powerPin":"3V3","groundPin":"GND","dataPin":"2"}
import json, time
import paho.mqtt.client as mqtt
import ssl
import random

# USER CONFIGURATION: update network credentials and hardware settings.
PIR_1_POWERPIN = "3V3"
PIR_1_GROUNDPIN = "GND"
PIR_1_DATAPIN = 2
BROKER_URL = "mqtts://mqtt.iotworkshop.africa:8883"
USERNAME = "device_dev_NJY7pr-Pwc_M2nkp"
PASSWORD = "vRDNt5jIxl1sls9uz4hkntJXfxQKZqFN5dRm1_LAYvU"
TELEMETRY_TOPIC = "dev_NJY7pr-Pwc_M2nkp/data"

def read_components():
    # USER CODE: replace placeholders with readings from the listed hardware.
    boolround = round(random.uniform(0,1),0)
    return {
      "pir_1": {
        "motion": bool(boolround)
      }
    }

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="dev_NJY7pr-Pwc_M2nkp", protocol=mqtt.MQTTv5)
client.username_pw_set(USERNAME, PASSWORD)
client.tls_set(cert_reqs=ssl.CERT_NONE)
client.connect("mqtt.iotworkshop.africa", 8883)
client.loop_start()
while True:
    client.publish(TELEMETRY_TOPIC, json.dumps({"components": read_components()}), qos=1)
    time.sleep(10)
