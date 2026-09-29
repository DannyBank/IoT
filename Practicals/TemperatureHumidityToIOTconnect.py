import json, time, network, ssl
import dht
from machine import Pin, I2C
from umqtt.simple import MQTTClient
import ahtx0
import bmp280

# USER CONFIGURATION: set these values before uploading to the board.
DHTX_1_POWERPIN = "3V3"
DHTX_1_GROUNDPIN = "GND"
DHTX_1_DATAPIN = 32

PUSH_BUTTON_1_GROUNDPIN = "GND"
PUSH_BUTTON_1_DATAPIN = 26

BUZZER_1_GROUNDPIN = "GND"
BUZZER_1_CONTROLPIN = 33

WIFI_SSID = "DBANK-WIFI"
WIFI_PASSWORD = "D@@nn33ll1234"
MQTT_HOST = "mqtt.iotworkshop.africa"
MQTT_PORT = 8883
MQTT_USER = "device_dev_5OZSZ22waF6xn0eF".encode()
MQTT_PASSWORD = "cHM5sreChkeYBQgx3fMN0LchMDCxTUn0x-MhN48gMyQ".encode()
TELEMETRY_TOPIC = "dev_5OZSZ22waF6xn0eF/data".encode()
COMMAND_TOPIC = "dev_5OZSZ22waF6xn0eF/cmd".encode()
RESULT_TOPIC = "dev_5OZSZ22waF6xn0eF/result".encode()
MQTT_CA_CERT = """-----BEGIN CERTIFICATE-----
MIIFTzCCAzegAwIBAgIUW2cDxTCTlyzl3FEHsxzcFnVVcZgwDQYJKoZIhvcNAQEL
BQAwNzEgMB4GA1UEAwwXSW9UQ29ubmVjdCBNUVRUIFJvb3QgQ0ExEzARBgNVBAoM
CklvVENvbm5lY3QwHhcNMjYwNzIxMjEwODE2WhcNMzYwNzE4MjEwODE2WjA3MSAw
HgYDVQQDDBdJb1RDb25uZWN0IE1RVFQgUm9vdCBDQTETMBEGA1UECgwKSW9UQ29u
bmVjdDCCAiIwDQYJKoZIhvcNAQEBBQADggIPADCCAgoCggIBAMIUJrFi4bpa314w
Zey63SzzAy4PHu+T2nVaXbuqavrfQtdlFfM6iAII6ISNuT9WPvXGPRNAfeJ0JzR/
NVKhNVWexhyYu9EMgE/+fTvsoalhAs2QMMr9no1RmxmrW04SyOLdWdtjhqh7xpcZ
PWFD+CrfgP0mGKMOsmcdUmAW+a7KG2bO0fylRPKcBvyo/nX6jDQt2mvK0omv8thQ
wdbaM/Sf4QHPTA7ZM2Vd8AIz75jlVfsQIKYNZt7xyGOL9igOtl16PBw16i1B9Vik
94eFJ1SGQLhDfynQWXOh0tcSClwIjbUjFRfxjFHt8fi6rPrdiwRecLX//GPDXDQ8
+UMXM2SpMLx0mLJGToJ5CaxjXF2OmD9UQ4oTe7wGshmxO3aj2fixRkMqNNS5Hj3l
bzbusZl1dMUzaZxXhVU2q2LIdemO/YVu45P8TMKbiOTdRvH/YwtGMuYIWdjg3vUL
H24ig0e7Lb1Ab/+CvPBilR1Qp63++BFLOqvHCJALgLfT7hsMXEABQ8uWJQ0gPayQ
HpkZQOcVEPd/ViVBuazCvh7w9/op7FBllhnaHZeL7b8INMAHH0wmgWYeZrD55H+R
qSmVFYlQrRp2rTEuVeph+WYBEUGlKdGjLXQQpuP7jUVHy1lF+eiLLeUFmCLzU2s0
NGdYSb+t/q4FFX4Tx6veb/OXIDDnAgMBAAGjUzBRMB0GA1UdDgQWBBR+bjbz+Tjr
LaLF035EoKnLJ/aWBTAfBgNVHSMEGDAWgBR+bjbz+TjrLaLF035EoKnLJ/aWBTAP
BgNVHRMBAf8EBTADAQH/MA0GCSqGSIb3DQEBCwUAA4ICAQDAmXCehI5LQaOFYOKi
Gne1Yc2VvLIW8vkYntMwcMVOaRtPSNE+tGjsqC/DOPmdY0kylFLRkjg7th3IqN9y
40gj19efA8Cxd0lZO7VFjwpvxYkW6NYWHbd2Y7dgy/D0hAOjLvLUmY7PF3/97P1K
/H3i1rW9gEVxO+xD0zyBe1Gn/P+X6CXEaDVR+obUk2pzB+iHTGC6XxTB5aLjeUbh
E+QXfhGjN63ccx7MPbh9W6NMANlbMpHMzWtT4LSnm3UBb2qgM8nJstwzYRPmZKwJ
l0BxsZFKkFrEld6S7LhU7Y6qQVmNO1wcS41Eldbf8YmOD9X9yC/aVYeF9xUe7vUI
zUCK3fmvWLUIX26LolMflYZfOVZUcI8MmqtoxsjS97i0aAWFz9LvNncA48pt1h46
hQslPTqEurXRkArGO7XL7bvWC3jPOrPGUwIg36JV/E59jDYO5zJngx5pwS20c5pG
vCbZfKR3qoX/Uc+haxav5BWxtqHrO25CNU5CQmFKBioS5A2YZaAYOS5FR5yLSxwB
5qkfHkiODM5uHncrCDyYFWBl4xxfxYzMxmMrXD92J+8W0EnQIMLpjjnXUPG/n44N
TeIJV1n3w3mhwpx4c7fZKCI+KwcJu48ezSonnMgPvwZP7Q/wqd3wCJdeIEtJwlX/
lm9gtTo4bhRLYjk4meM9lHjxvQ==
-----END CERTIFICATE-----
"""
ca_cert_data = MQTT_CA_CERT.encode()

i2c = I2C(0, scl=Pin(22), sda=Pin(21))

#print("I2C devices:", [hex(x) for x in i2c.scan()])

aht20 = ahtx0.AHT20(i2c)
bmp = bmp280.BMP280(i2c, addr=0x77)

def read_components():    
    return {
        "aht20_bmp280_1": {
            "temperature": round(float(aht20.temperature), 2),
            "humidity": round(float(aht20.relative_humidity), 2),
            "pressure": round(float(bmp.pressure) / 100, 2)
        }
    }
        
def apply_command(command):
    raise ValueError("No supported actuator is configured")

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

# NETWORK SETUP
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
print("[WIFI] Connecting to", WIFI_SSID)
wlan.connect(WIFI_SSID, WIFI_PASSWORD)
while not wlan.isconnected():
    time.sleep_ms(250)
print("[WIFI] Connected:", wlan.ifconfig())

ssl_params = {
    "server_hostname": MQTT_HOST,
    "cert_reqs": ssl.CERT_NONE
}

client = MQTTClient(
    "dev_1R1IhUQNUYQ-g06u".encode(),
    MQTT_HOST, port=MQTT_PORT, user=MQTT_USER,
    password=MQTT_PASSWORD, ssl=True, ssl_params=ssl_params)
client.set_callback(on_command)
print("[MQTT] Connecting to {}:{}".format(MQTT_HOST, MQTT_PORT))
client.connect()
print("[MQTT] Connected")
client.subscribe(COMMAND_TOPIC)
print("[MQTT] Subscribed:", COMMAND_TOPIC)

last_telemetry = time.ticks_ms() - 10000

# MAIN LOOP
while True:
    client.check_msg()
    
    now = time.ticks_ms()
    if time.ticks_diff(now, last_telemetry) >= 5000:
        telemetry = {"components": read_components()}
        client.publish(TELEMETRY_TOPIC, json.dumps(telemetry))
        print("[MQTT] Telemetry published:", telemetry)
        last_telemetry = now
        
    time.sleep_ms(5)
