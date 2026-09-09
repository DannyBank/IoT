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
# -----------------------------------------------------------------------------
# MQTT 5. Install: pip install paho-mqtt
# Rain sensor (Rain sensor): {"interface":"ADC","powerPin":"3V3","groundPin":"GND"}
# Water-flow sensor (Water-flow sensor): {"wires":{},"interface":"GPIO","wireModes":{"powerPin":"auto","groundPin":"auto"},"portAnchors":{"powerPin":"left:0","groundPin":"right:2"},"powerPin":"3V3","groundPin":"GND","dataPin":"2"}
# GPS / GNSS receiver (GPS / GNSS receiver): {"baudRate":"9600","interface":"UART","powerPin":"3V3","groundPin":"GND"}
# MQ-2 gas sensor (MQ-2 gas sensor): {"interface":"ADC","powerPin":"3V3","groundPin":"GND"}
import json, time
import paho.mqtt.client as mqtt
import ssl
import random

# USER CONFIGURATION: update network credentials and hardware settings.
RAIN_SENSOR_1_POWERPIN = "3V3"
RAIN_SENSOR_1_GROUNDPIN = "GND"
BROKER_URL = "mqtts://mqtt.iotworkshop.africa:8883"
USERNAME = "device_dev_NJY7pr-Pwc_M2nkp"
PASSWORD = "4VeSofqqKwxMeYjZmJ0mCJbrW2_QSrb5SUyOih7-2i0"
TELEMETRY_TOPIC = "dev_NJY7pr-Pwc_M2nkp/data"

def read_components():
    # USER CODE: replace placeholders with readings from the listed hardware.
    return {
      "rain_sensor_1": {
        "rain_level": round(random.uniform(0,100.0), 3),
        "raining": round(random.uniform(0,1), 0)
      },
      "infrared_1": {
        "distance": round(random.uniform(0.1,1000.0), 2)
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
