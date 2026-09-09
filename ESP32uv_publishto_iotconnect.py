import json
import machine
import network
import ssl
import time
from umqtt.simple import MQTTClient

# --- CONFIGURATION ---
SSID = "DBANK_WIFI"
PASSWORD = "D@@nn33ll1234"

SERVER = "mqtt.iotworkshop.africa"
PORT = 8883
CLIENT_ID = "dev_Y7WP9mnveSUzKJdA"
USERNAME = "device_dev_Y7WP9mnveSUzKJdA"
PASSWORD_MQTT = "bQFn2lYoWadS98E86K7w0nD_n5V7Cja6IbAhAGav9rQ"
TELEMETRY_TOPIC = "dev_Y7WP9mnveSUzKJdA/data"

# PEM CA Certificate String
CA_CERT = """MIIFTzCCAzegAwIBAgIUW2cDxTCTlyzl3FEHsxzcFnVVcZgwDQYJKoZIhvcNAQEL
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
lm9gtTo4bhRLYjk4meM9lHjxvQ=="""

# --- HARDWARE SETUP ---
# Shifted from GPIO 14 (ADC2) to GPIO 34 (ADC1) to prevent Wi-Fi interference
TEMT6000_PIN = 35

adc = machine.ADC(machine.Pin(TEMT6000_PIN))
adc.atten(machine.ADC.ATTN_11DB)  # Full 0V to 3.3V range
adc.width(machine.ADC.WIDTH_12BIT)  # 0 to 4095 range


def connect_wifi():
    """Establishes connection to the Wi-Fi network."""
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    if not wlan.isconnected():
        print(f"Connecting to {SSID}...")
        wlan.connect(SSID, PASSWORD)

        timeout = 10
        start_time = time.time()

        while not wlan.isconnected():
            if time.time() - start_time > timeout:
                print("\nConnection failed: Timed out.")
                return False
            time.sleep(0.5)
            print(".", end="")

    print("\nConnected to Wi-Fi successfully!")
    print("Network config:", wlan.ifconfig())
    return True


def read_components():
    """Reads raw ADC value and converts it to voltage and Lux percentage."""
    raw_val = adc.read()
    voltage = round((raw_val / 4095.0) * 3.3, 2)
    light_percent = round((raw_val / 4095.0) * 100, 1)

    return {
        "temt6000_ambient_light_sensor_1": {
            "ambient_light": light_percent,
            "raw_level": raw_val,
            "signal_voltage": voltage,
        }
    }


def main():
    print("Testing ADC reading before Wi-Fi connection:")
    print(read_components())

    if not connect_wifi():
        print("Aborting: Could not connect to Wi-Fi.")
        return

    print("Testing ADC reading after Wi-Fi connection:")
    print(read_components())

    # SSL parameters with inline certificate string
    ssl_params = {
        "server_hostname": SERVER,
        "cert_reqs": ssl.CERT_NONE
    }

    client = MQTTClient(
        client_id=CLIENT_ID,
        server=SERVER,
        port=PORT,
        user=USERNAME,
        password=PASSWORD_MQTT,
        ssl=True,
        ssl_params=ssl_params,
    )

    try:
        print("Connecting to MQTT broker (IoTConnect)...")
        client.connect()
        print("Connection Established!")

        while True:
            sensor_data = read_components()
            print("Sensor Data:", sensor_data)

            payload = json.dumps({"components": sensor_data})
            client.publish(TELEMETRY_TOPIC, payload, qos=1)
            print("Published telemetry successfully!")

            time.sleep(5)

    except KeyboardInterrupt:
        print("\nStopping script...")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
    finally:
        print("Disconnecting MQTT client...")
        try:
            client.disconnect()
        except Exception:
            pass
        print("Done.")


if __name__ == "__main__":
    main()