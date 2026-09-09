import paho.mqtt.client as mqtt
import random
import time
import json

#mosquitto_pub -h 193.194.163.90 -p 1883 -t iketemp -m "Testing Mosquitto 1"
# MQTT settings

BROKER = "193.194.163.11"
PORT = 1883
TOPIC = "home/kitchen/temperature"

client = mqtt.Client(protocol=mqtt.MQTTv5)
client.connect(BROKER, PORT)

while True:
    message = input("enter your text\n")
    data = {
        "temperature": message
        }
    client.publish(TOPIC, json.dumps(data))
    print(f"Published: {data}")
    time.sleep(5)