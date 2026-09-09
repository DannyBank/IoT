# -----------------------------------------------------------------------------
# IoTConnect Device Application
#
# Project   : BuzzerController
# Generated : Automatically by IoTConnect
# Platform  : MicroPython
# Copyright : 2026 IoTDevLab
# License   : MIT (SPDX-License-Identifier: MIT)
#
# This file was generated automatically.
# Changes made directly to this file may be overwritten when regenerated.
#
# Required drivers:
#   - Buzzer
#
# Device configuration:
#   Sensors   : None
#   Actuators : Buzzer
#   Network   : Configured
# -----------------------------------------------------------------------------
# MQTT protocol: 3.1.1 compatibility (umqtt.simple does not implement MQTT 5).
# Install any hardware driver modules named below before uploading this file.
# Buzzer (Buzzer): {"interface":"GPIO","groundPin":"GND","controlPin":"12"}
import json, time, network, ssl
from umqtt.simple import MQTTClient
import ntptime

def sync_time():
    for attempt in range(5):
        try:
            ntptime.settime()  # sets RTC to UTC via NTP
            print("[NTP] Time synced:", time.localtime())
            return True
        except OSError as e:
            print("[NTP] Sync failed, retrying:", e)
            time.sleep(1)
    return False


# USER CONFIGURATION: set these values before uploading to the board.
BUZZER_1_GROUNDPIN = "GND"
BUZZER_1_CONTROLPIN = 12
WIFI_SSID = "DBANK_WIFI"
WIFI_PASSWORD = "D@@nn33ll1234"
MQTT_HOST = "mqtt.iotworkshop.africa"
MQTT_PORT = 8883
MQTT_USER = "device_dev_uF26u7YeRtihbwuz".encode()
MQTT_PASSWORD = "Y4_iEAgBtXu3YZYuL15_C9V16OcvaREa8AA_wMiSyBA".encode()
MQTT_CA_FILE = "mqtt-ca.crt"
TELEMETRY_TOPIC = "dev_uF26u7YeRtihbwuz/data".encode()
COMMAND_TOPIC = "dev_uF26u7YeRtihbwuz/cmd".encode()
RESULT_TOPIC = "dev_uF26u7YeRtihbwuz/result".encode()

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

# USER CODE: add custom setup, readings, or control logic in the marked sections.


def read_components():
    return {
        "buzzer_1": {
          "active": False
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

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
print("[WIFI] Connecting to", WIFI_SSID)
wlan.connect(WIFI_SSID, WIFI_PASSWORD)
while not wlan.isconnected():
    time.sleep_ms(250)
print("[WIFI] Connected:", wlan.ifconfig())

sync_time()

client = MQTTClient(
    "dev_uF26u7YeRtihbwuz".encode(),
    MQTT_HOST,
    port=MQTT_PORT,
    user=MQTT_USER,
    password=MQTT_PASSWORD,
    ssl=True,
    ssl_params={
        "server_hostname": MQTT_HOST,
        "cert_reqs": ssl.CERT_REQUIRED,
        "cadata": ca_cert_data
    }
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