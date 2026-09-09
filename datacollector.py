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
import paho.mqtt.client as mqtt
import random
import ssl

# USER CONFIGURATION: update network credentials and hardware settings.
DHTX_1_POWERPIN = "3V3"
DHTX_1_GROUNDPIN = "GND"
DHTX_1_DATAPIN = 2
BROKER_URL = "mqtts://mqtt.iotworkshop.africa:8883"
USERNAME = "device_dev_Y7WP9mnveSUzKJdA"
PASSWORD = "bQFn2lYoWadS98E86K7w0nD_n5V7Cja6IbAhAGav9rQ"
TELEMETRY_TOPIC = "dev_Y7WP9mnveSUzKJdA/data"

# DATA READING
def read_components():
    
    # USER CODE: replace placeholders with readings from the listed hardware.
    return {
      "dhtx_1": {
        "temperature": round(random.uniform(30.0, 65.0), 2),
        "humidity": round(random.uniform(40.0, 80.0), 2)
      }
    }

#ESTABLISH BROKER CONNECTION
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="dev_Y7WP9mnveSUzKJdA", protocol=mqtt.MQTTv5)
client.username_pw_set(USERNAME, PASSWORD)
client.tls_set(cert_reqs=ssl.CERT_NONE)
client.tls_insecure_set(True)
client.connect("mqtt.iotworkshop.africa", 8883)
client.loop_start()

#SEND DATA TO THE BROKER
while True:
    client.publish(TELEMETRY_TOPIC, json.dumps({"components": read_components()}), qos=1)
    time.sleep(10)
