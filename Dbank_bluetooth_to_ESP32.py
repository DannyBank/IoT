import bluetooth
import time
import neopixel
import struct
import micropython
from machine import Pin
from micropython import const

# Allocate emergency exception buffer for IRQ debugging
micropython.alloc_emergency_exception_buf(100)

# --- Hardware Configuration ---
LED_RING_PIN = 14      # GPIO pin connected to Data In (DIN)
NUM_LEDS = 8           # Number of LEDs in the ringlight

# Initialize NeoPixel Ring
ring = neopixel.NeoPixel(Pin(LED_RING_PIN, Pin.OUT), NUM_LEDS)

def set_ring_color(r, g, b):
    """Sets all 8 LEDs to the given RGB tuple and writes to ring."""
    for i in range(NUM_LEDS):
        ring[i] = (r, g, b)
    ring.write()

def turn_off_ring():
    set_ring_color(0, 0, 0)

# Default startup state: Ring off
turn_off_ring()


# --- BLE Constants ---
_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_WRITE = const(3)

_FLAG_WRITE = const(0x0008)
_FLAG_NOTIFY = const(0x0010)

_UART_UUID = bluetooth.UUID("6E400001-B5A3-F393-E0A9-E50E24DCCA9E")
_UART_RX = (bluetooth.UUID("6E400002-B5A3-F393-E0A9-E50E24DCCA9E"), _FLAG_WRITE)
_UART_TX = (bluetooth.UUID("6E400003-B5A3-F393-E0A9-E50E24DCCA9E"), _FLAG_NOTIFY)
_UART_SERVICE = (_UART_UUID, (_UART_TX, _UART_RX))

MAX_CONNECTIONS = 4


def build_ble_payloads(name, service_uuid=None):
    """
    Builds Web BLE compliant Advertising Payload (adv_data) 
    and Scan Response Payload (resp_data).
    """
    # 1. Primary Advertisement Packet (adv_data)
    adv_payload = bytearray()
    
    # Flags: General Discoverable Mode (0x02) + BR/EDR Not Supported (0x04) = 0x06
    adv_payload += b"\x02\x01\x06"

    # Complete List of 128-bit Service Class UUIDs (0x07)
    if service_uuid:
        uuid_bytes = bytes(service_uuid)
        if len(uuid_bytes) == 16:
            adv_payload += struct.pack("BB", len(uuid_bytes) + 1, 0x07) + uuid_bytes

    # 2. Scan Response Packet (resp_data) -> Holds the Device Name
    resp_payload = bytearray()
    name_bytes = name.encode("utf-8")
    resp_payload += struct.pack("BB", len(name_bytes) + 1, 0x09) + name_bytes

    return adv_payload, resp_payload


class BLEMQTTBroker:
    def __init__(self, name="ESP32-MQTT-Ring"):
        self._ble = bluetooth.BLE()
        self._ble.active(True)
        self._ble.irq(self._irq)

        ((self._handle_tx, self._handle_rx),) = self._ble.gatts_register_services((_UART_SERVICE,))

        self.connections = set()
        self._subscriptions = {}
        self._name = name
        self.ring_state = "OFF"
        self.current_color = (255, 255, 255)

        # Build Web BLE discovery payloads
        self._adv_payload, self._resp_payload = build_ble_payloads(self._name, service_uuid=_UART_UUID)
        self._advertise()

    def _advertise(self, interval_us=100000):
        if len(self.connections) >= MAX_CONNECTIONS:
            return

        try:
            # Broadcast advertising payload and scan response payload
            self._ble.gap_advertise(interval_us, adv_data=self._adv_payload, resp_data=self._resp_payload)
            print(f"[+] Web BLE Discoverable: '{self._name}'")
        except OSError as e:
            print(f"[!] Advertising error: {e}")

    def _safe_advertise(self, _):
        """Safely restart advertising outside IRQ context."""
        time.sleep_ms(100)
        self._advertise()

    def _irq(self, event, data):
        if event == _IRQ_CENTRAL_CONNECT:
            conn_handle, _, _ = data
            self.connections.add(conn_handle)
            print(f"[+] Client connected: handle {conn_handle}")
            micropython.schedule(self._safe_advertise, 0)

        elif event == _IRQ_CENTRAL_DISCONNECT:
            conn_handle, _, _ = data
            if conn_handle in self.connections:
                self.connections.remove(conn_handle)
            for topic in self._subscriptions:
                if conn_handle in self._subscriptions[topic]:
                    self._subscriptions[topic].remove(conn_handle)
            print(f"[-] Client disconnected: handle {conn_handle}")
            micropython.schedule(self._safe_advertise, 0)

        elif event == _IRQ_GATTS_WRITE:
            conn_handle, value_handle = data
            if value_handle == self._handle_rx:
                payload = self._ble.gatts_read(self._handle_rx).decode("utf-8").strip()
                self._parse_mqtt_packet(conn_handle, payload)

    def _parse_mqtt_packet(self, conn_handle, payload):
        parts = payload.split(" ", 2)
        command = parts[0].upper()

        if command == "SUB" and len(parts) >= 2:
            topic = parts[1]
            if topic not in self._subscriptions:
                self._subscriptions[topic] = set()
            self._subscriptions[topic].add(conn_handle)
            print(f"[SUB] Handle {conn_handle} subscribed to: '{topic}'")
            self.publish_to_handle(conn_handle, f"ACK SUB {topic}")

        elif command == "PUB" and len(parts) >= 3:
            topic = parts[1]
            message = parts[2].upper()
            print(f"[PUB] Received on '{topic}': {message}")

            if topic == "ring/power":
                if message == "ON":
                    self.ring_state = "ON"
                    set_ring_color(*self.current_color)
                    self.publish("ring/status", "POWER: ON")
                elif message == "OFF":
                    self.ring_state = "OFF"
                    turn_off_ring()
                    self.publish("ring/status", "POWER: OFF")

            elif topic == "ring/color":
                self._handle_color_command(message)

            self.publish(topic, message)

    def _handle_color_command(self, color_str):
        color_map = {
            "RED": (255, 0, 0),
            "GREEN": (0, 255, 0),
            "BLUE": (0, 0, 255),
            "WHITE": (255, 255, 255),
            "YELLOW": (255, 150, 0),
            "PURPLE": (180, 0, 255)
        }

        if color_str in color_map:
            self.current_color = color_map[color_str]
        else:
            try:
                rgb = tuple(map(int, color_str.split(",")))
                if len(rgb) == 3:
                    self.current_color = rgb
            except Exception:
                print("[!] Invalid RGB color payload.")
                return

        if self.ring_state == "ON":
            set_ring_color(*self.current_color)

        self.publish("ring/status", f"COLOR: {self.current_color}")

    def publish(self, topic, message):
        formatted = f"MQTT:{topic}:{message}\n".encode("utf-8")
        if topic in self._subscriptions:
            for handle in list(self._subscriptions[topic]):
                try:
                    self._ble.gatts_notify(handle, self._handle_tx, formatted)
                except Exception as e:
                    print(f"[!] Notify error handle {handle}: {e}")

    def publish_to_handle(self, conn_handle, message):
        payload = f"{message}\n".encode("utf-8")
        try:
            self._ble.gatts_notify(conn_handle, self._handle_tx, payload)
        except Exception as e:
            print(f"[!] Direct send error: {e}")


# ==========================================
# MAIN LOOP
# ==========================================
if __name__ == "__main__":
    broker = BLEMQTTBroker(name="ESP32-MQTT-Ring")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down...")
        turn_off_ring()
        broker._ble.active(False)