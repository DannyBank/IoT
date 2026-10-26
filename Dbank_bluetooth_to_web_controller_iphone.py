import bluetooth
import time
import neopixel
from machine import Pin, PWM
from micropython import const

# ==========================================
# HARDWARE CONFIGURATION
# ==========================================

LED_RING_PIN = 14
PIR_PIN = 27
SERVO_PIN = 13
TRAFFIC_RED_PIN = 25
TRAFFIC_YELLOW_PIN = 26
TRAFFIC_GREEN_PIN = 33

NUM_LEDS = 8

# FIX 4 (brownouts): cap ring brightness (0.0 - 1.0) to reduce current draw.
# Also power the servo and ring from a separate 5V supply with a COMMON GROUND.
RING_BRIGHTNESS = 0.3

ring = neopixel.NeoPixel(Pin(LED_RING_PIN, Pin.OUT), NUM_LEDS)

def set_ring_color(r, g, b):
    r = int(max(0, min(255, r)) * RING_BRIGHTNESS)
    g = int(max(0, min(255, g)) * RING_BRIGHTNESS)
    b = int(max(0, min(255, b)) * RING_BRIGHTNESS)
    for i in range(NUM_LEDS):
        ring[i] = (r, g, b)
    ring.write()


def turn_off_ring():
    for i in range(NUM_LEDS):
        ring[i] = (0, 0, 0)
    ring.write()


turn_off_ring()

pir_sensor = Pin(PIR_PIN, Pin.IN, Pin.PULL_DOWN)

servo_pwm = PWM(Pin(SERVO_PIN), freq=50)


def set_servo_angle(angle):
    """Maps 0-180 degrees to SG90 duty (ESP32 10-bit: ~26 = 0deg, ~123 = 180deg)."""
    angle = max(0, min(180, angle))
    duty = int(26 + (angle / 180.0) * 97)
    servo_pwm.duty(duty)

set_servo_angle(0)

tl_pins = {
    "RED": PWM(Pin(TRAFFIC_RED_PIN), freq=1000, duty=0),
    "YELLOW": PWM(Pin(TRAFFIC_YELLOW_PIN), freq=1000, duty=0),
    "GREEN": PWM(Pin(TRAFFIC_GREEN_PIN), freq=1000, duty=0),
}


def set_traffic_light(color_state):
    """Turns on the requested light (RED/YELLOW/GREEN); anything else turns all off."""
    for color, pwm_obj in tl_pins.items():
        pwm_obj.duty(1023 if color == color_state else 0)


def fade_traffic_light(color, direction):
    """Fades a light IN (0->1023) or OUT (1023->0). Blocking (~0.5s)."""
    if color not in tl_pins:
        return
    target_pwm = tl_pins[color]
    if direction == "IN":
        for duty in range(0, 1024, 32):
            target_pwm.duty(duty)
            time.sleep_ms(15)
        target_pwm.duty(1023)
    elif direction == "OUT":
        for duty in range(1023, -1, -32):
            target_pwm.duty(duty)
            time.sleep_ms(15)
        target_pwm.duty(0)


# ==========================================
# BLE & MQTT BROKER CONFIGURATION
# ==========================================
_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_WRITE = const(3)

_FLAG_WRITE_NO_RESPONSE = const(0x0004)
_FLAG_WRITE = const(0x0008)
_FLAG_NOTIFY = const(0x0010)

_UART_UUID = bluetooth.UUID("6E400001-B5A3-F393-E0A9-E50E24DCCA9E")
_UART_TX = (bluetooth.UUID("6E400003-B5A3-F393-E0A9-E50E24DCCA9E"), _FLAG_NOTIFY)
# FIX 2: allow both "write" and "write without response" (standard Nordic UART RX)
_UART_RX = (
    bluetooth.UUID("6E400002-B5A3-F393-E0A9-E50E24DCCA9E"),
    _FLAG_WRITE | _FLAG_WRITE_NO_RESPONSE,
)
_UART_SERVICE = (_UART_UUID, (_UART_TX, _UART_RX))

MAX_CONNECTIONS = 4
NOTIFY_CHUNK = const(20)  # safe size with default ATT MTU (23 - 3)
MAX_QUEUE = const(16)


class BLEMQTTBroker:
    # FIX 3: iOS caches name/GATT. If you change the name or characteristics,
    # also change DEFAULT_NAME (or forget the device / toggle Bluetooth on the iPhone).
    DEFAULT_NAME = "ESP32-MQTT-Ring"

    def __init__(self, name=DEFAULT_NAME):
        self._ble = bluetooth.BLE()
        self._ble.active(True)
        self._ble.irq(self._irq)

        ((self._handle_tx, self._handle_rx),) = self._ble.gatts_register_services(
            (_UART_SERVICE,)
        )
        # Default RX buffer is only 20 bytes, which truncates longer commands
        # (e.g. "PUB ring/color 255,150,0"). Enlarge it.
        self._ble.gatts_set_buffer(self._handle_rx, 256)

        self.connections = set()
        self._subscriptions = {}
        self._name = name
        self.ring_state = "OFF"
        self.current_color = (255, 255, 255)
        self.last_pir_state = -1

        # Incoming commands are queued by the IRQ and handled in the main loop,
        # so slow work (fades, notifies, PWM) never blocks BLE events.
        self._rx_queue = []

        self._advertise()

    # ---------- Advertising ----------
    def _advertise(self, interval_us=100000):
        if len(self.connections) >= MAX_CONNECTIONS:
            return

        name_bytes = self._name.encode("utf-8")

        flags = b"\x02\x01\x06"
        name_payload = bytes([len(name_bytes) + 1, 0x09]) + name_bytes

        # FIX 1: 128-bit UUID goes in the scan response (adv packet alone would be
        # 38 bytes, over the 31-byte limit).
        uuid_bytes = bytes(reversed(bytes.fromhex("6E400001B5A3F393E0A9E50E24DCCA9E")))
        uuid_payload = bytes([len(uuid_bytes) + 1, 0x07]) + uuid_bytes

        adv_data = flags + name_payload       # 20 bytes for the default name
        resp_data = uuid_payload              # 18 bytes

        try:
            self._ble.gap_advertise(interval_us, adv_data=adv_data, resp_data=resp_data)
            print("[+] Advertising as '{}'".format(self._name))
        except Exception as e:
            print("[!] Advertising failed: {}".format(e))

    # ---------- BLE IRQ (keep minimal) ----------
    def _irq(self, event, data):
        if event == _IRQ_CENTRAL_CONNECT:
            conn_handle, _, _ = data
            self.connections.add(conn_handle)
            print("[+] Client connected: handle", conn_handle)
            self._advertise()

        elif event == _IRQ_CENTRAL_DISCONNECT:
            conn_handle, _, _ = data
            self.connections.discard(conn_handle)
            for topic in self._subscriptions:
                self._subscriptions[topic].discard(conn_handle)
            print("[-] Client disconnected: handle", conn_handle)
            self._advertise()

        elif event == _IRQ_GATTS_WRITE:
            conn_handle, value_handle = data
            if value_handle == self._handle_rx:
                raw = self._ble.gatts_read(self._handle_rx)
                if len(self._rx_queue) < MAX_QUEUE:
                    self._rx_queue.append((conn_handle, raw))

    # ---------- Main-loop processing ----------
    def process_queue(self):
        if not self._rx_queue:
            return

        # Grab everything waiting, then decode.
        batch, self._rx_queue = self._rx_queue, []
        decoded = []
        for conn_handle, raw in batch:
            try:
                payload = raw.decode("utf-8").strip()
            except Exception:
                print("[!] Undecodable packet ignored")
                continue
            if payload:
                decoded.append((conn_handle, payload))

        # Servo coalescing: if several servo/angle commands arrived together
        # (e.g. a slider being dragged), only act on the newest one.
        last_servo = -1
        for i, (_, p) in enumerate(decoded):
            if p.upper().startswith("PUB SERVO/ANGLE"):
                last_servo = i

        for i, (conn_handle, payload) in enumerate(decoded):
            if payload.upper().startswith("PUB SERVO/ANGLE") and i != last_servo:
                continue
            self._parse_mqtt_packet(conn_handle, payload)

    def _parse_mqtt_packet(self, conn_handle, payload):
        parts = payload.split(" ", 2)
        command = parts[0].strip().upper()

        if command == "SUB" and len(parts) >= 2:
            topic = parts[1].strip()
            if topic not in self._subscriptions:
                self._subscriptions[topic] = set()
            self._subscriptions[topic].add(conn_handle)
            print("[SUB] Handle {} subscribed to: '{}'".format(conn_handle, topic))
            self.publish_to_handle(conn_handle, "ACK SUB " + topic)

        elif command == "PUB" and len(parts) >= 3:
            topic = parts[1].strip()
            message = parts[2].strip().upper()
            print("[PUB] Received on '{}': {}".format(topic, message))

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

            elif topic == "servo/angle":
                try:
                    angle = int(message)
                    set_servo_angle(angle)
                    self.publish("servo/status", "ANGLE: {}".format(angle))
                except ValueError:
                    print("[!] Invalid Servo Angle payload")

            elif topic == "traffic/state":
                set_traffic_light(message)
                self.publish("traffic/status", "STATE: {}".format(message))

            elif topic == "traffic/fade":
                if ":" in message:
                    action, color = message.split(":", 1)
                    action, color = action.strip(), color.strip()
                    # Safe here: runs in the main loop, not the BLE IRQ
                    fade_traffic_light(color, action)
                    self.publish("traffic/status", "FADE {}: {}".format(action, color))

            # Re-broadcast payload to topic subscribers
            self.publish(topic, message)

    def _handle_color_command(self, color_str):
        color_map = {
            "RED": (255, 0, 0),
            "GREEN": (0, 255, 0),
            "BLUE": (0, 0, 255),
            "WHITE": (255, 255, 255),
            "YELLOW": (255, 150, 0),
            "PURPLE": (180, 0, 255),
        }

        if color_str in color_map:
            self.current_color = color_map[color_str]
        else:
            try:
                rgb = tuple(int(v) for v in color_str.split(","))
                if len(rgb) == 3:
                    self.current_color = rgb
                else:
                    print("[!] RGB needs exactly 3 values")
                    return
            except Exception:
                print("[!] Invalid RGB color payload.")
                return

        if self.ring_state == "ON":
            set_ring_color(*self.current_color)

        self.publish("ring/status", "COLOR: {}".format(self.current_color))

    def check_pir_sensor(self):
        current_state = pir_sensor.value()
        if current_state != self.last_pir_state:
            self.last_pir_state = current_state
            state_text = "TRUE" if current_state == 1 else "FALSE"
            print("[PIR] State Changed ->", state_text)
            self.publish("motion/state", state_text)

    # ---------- Notify helpers ----------
    def _notify(self, handle, data):
        """Send in chunks so messages longer than the MTU aren't truncated."""
        try:
            for i in range(0, len(data), NOTIFY_CHUNK):
                self._ble.gatts_notify(handle, self._handle_tx, data[i:i + NOTIFY_CHUNK])
                if i + NOTIFY_CHUNK < len(data):
                    time.sleep_ms(2)
        except Exception as e:
            print("[!] Notify error handle {}: {}".format(handle, e))

    def publish(self, topic, message):
        formatted = "MQTT:{}:{}\n".format(topic, message).encode("utf-8")
        if topic in self._subscriptions:
            for handle in list(self._subscriptions[topic]):
                self._notify(handle, formatted)

    def publish_to_handle(self, conn_handle, message):
        self._notify(conn_handle, "{}\n".format(message).encode("utf-8"))

    def shutdown(self):
        try:
            self._ble.gap_advertise(None)
        except Exception:
            pass
        self._ble.active(False)


# ==========================================
# MAIN LOOP  (save this file as main.py on the ESP32)
# ==========================================
if __name__ == "__main__":
    broker = BLEMQTTBroker()

    try:
        while True:
            broker.process_queue()
            broker.check_pir_sensor()
            time.sleep_ms(1)

    except KeyboardInterrupt:
        print("\nShutting down...")
        turn_off_ring()
        set_traffic_light("OFF")
        servo_pwm.deinit()
        broker.shutdown()