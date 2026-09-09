import paho.mqtt.client as mqtt
import json

# MQTT settings
BROKER = "193.194.163.11"
PORT = 1883
TOPIC = "msc"

def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        textmessage = data["textmessage"]
        print(textmessage)
        #temp = data["temperature"]
        #hum = data["humidity"]
        #print(f"Temperature: {temp}C, Humidity: {hum}%")
    except:
        print(f"Raw data: {msg.payload.decode()}")

client = mqtt.Client(protocol=mqtt.MQTTv5)
client.on_message = on_message
client.connect(BROKER, PORT)
client.subscribe(TOPIC)
print(f"Listening for sensor data on topic {TOPIC}...")
client.loop_forever()