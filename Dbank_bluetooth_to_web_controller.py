import bluetooth
import time
import neopixel
from machine import Pin, PWM
from micropython import const

# ==========================================
# HARDWARE CONFIGURATION
# ==========================================

# 1. NeoPixel Ring Light
LED_RING_PIN = 14
PIR_PIN = 27
SERVO_PIN = 13
TRAFFIC_RED_PIN = 25
TRAFFIC_YELLOW_PIN = 26
TRAFFIC_GREEN_PIN = 33

NUM_LEDS = 8
ring = neopixel.NeoPixel(Pin(LED_RING_PIN, Pin.OUT), NUM_LEDS)

def set_ring_color(r, g, b):
    for i in range(NUM_LEDS):
        ring[i] = (r, g, b)
    ring.write()

def turn_off_ring():
    set_ring_color(0, 0, 0)

turn_off_ring()

# 2. PIR Motion Sensor
pir_sensor = Pin(PIR_PIN, Pin.IN, Pin.PULL_DOWN)

# 3. SG90 Servo Motor (PWM at 50Hz)
servo_pwm = PWM(Pin(SERVO_PIN), freq=50)

def set_servo_angle(angle):
    """Maps 0 to 180 degrees to duty cycle values for SG90 (approx 0.5ms - 2.5ms pulse)."""
    angle = max(0, min(180, angle))
    # Standard ESP32 10-bit PWM duty (0-1023): ~26 for 0 deg, ~123 for 180 deg
    duty = int(26 + (angle / 180.0) * 97)
    servo_pwm.duty(duty)

set_servo_angle(0)

# 4. Traffic Light LEDs (PWM for Fading support)

tl_pins = {
    "RED": PWM(Pin(TRAFFIC_RED_PIN), freq=1000, duty=0),
    "YELLOW": PWM(Pin(TRAFFIC_YELLOW_PIN), freq=1000, duty=0),
    "GREEN": PWM(Pin(TRAFFIC_GREEN_PIN), freq=1000, duty=0)
}

def set_traffic_light(color_state):
    """Activates the requested light state (RED, YELLOW, GREEN) and turns off others."""
    for color, pwm_obj in tl_pins.items():
        if color == color_state:
            pwm_obj.duty(1023)
        else:
            pwm_obj.duty(0)

def fade_traffic_light(color, direction):
    """Fades a specified light IN (0->1023) or OUT (1023->0) smoothly."""
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

_FLAG_WRITE = const(0x0008)
_FLAG_NOTIFY = const(0x0010)

_UART_UUID = bluetooth.UUID("6E400001-B5A3-F393-E0A9-E50E24DCCA9E")
_UART_RX = (bluetooth.UUID("6E400002-B5A3-F393-E0A9-E50E24DCCA9E"), _FLAG_WRITE)
_UART_TX = (bluetooth.UUID("6E400003-B5A3-F393-E0A9-E50E24DCCA9E"), _FLAG_NOTIFY)
_UART_SERVICE = (_UART_UUID, (_UART_TX, _UART_RX))

MAX_CONNECTIONS = 4


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
        self.last_pir_state = -1
        
        self._advertise()

    def _advertise(self, interval_us=100000):
        if len(self.connections) >= MAX_CONNECTIONS:
            return

        name_bytes = self._name.encode("utf-8")
        
        # 1. Flags: General Discoverable Mode & BR/EDR Not Supported (0x02, 0x01, 0x06)
        flags = b"\x02\x01\x06"
        
        # 2. Complete Local Name (Type 0x09)
        name_payload = bytes([len(name_bytes) + 1, 0x09]) + name_bytes
        
        # 3. Complete 128-bit Service UUID (Type 0x07) - Reversed via reversed() for MicroPython
        uuid_raw = bytes.fromhex("6E400001B5A3F393E0A9E50E24DCCA9E")
        uuid_bytes = bytes(reversed(uuid_raw))
        uuid_payload = bytes([len(uuid_bytes) + 1, 0x07]) + uuid_bytes

        # Combine payload (31 bytes max)
        payload = flags + name_payload + uuid_payload
        
        try:
            self._ble.gap_advertise(interval_us, adv_data=payload)
            print(f"[+] Advertising as '{self._name}' (iOS Compatible)")
        except Exception as e:
            # Fallback if payload exceeds 31 bytes limit
            fallback_payload = flags + name_payload
            self._ble.gap_advertise(interval_us, adv_data=fallback_payload)
            print(f"[!] Full UUID payload too long, using standard fallback: {e}")

    def _irq(self, event, data):
        if event == _IRQ_CENTRAL_CONNECT:
            conn_handle, _, _ = data
            self.connections.add(conn_handle)
            print(f"[+] Client connected: handle {conn_handle}")
            self._advertise()

        elif event == _IRQ_CENTRAL_DISCONNECT:
            conn_handle, _, _ = data
            if conn_handle in self.connections:
                self.connections.remove(conn_handle)
            for topic in self._subscriptions:
                if conn_handle in self._subscriptions[topic]:
                    self._subscriptions[topic].remove(conn_handle)
            print(f"[-] Client disconnected: handle {conn_handle}")
            self._advertise()

        elif event == _IRQ_GATTS_WRITE:
            conn_handle, value_handle = data
            if value_handle == self._handle_rx:
                dats = self._ble.gatts_read(self._handle_rx).decode("utf-8")
                payload = dats.strip()
                self._parse_mqtt_packet(conn_handle, payload)

    def _parse_mqtt_packet(self, conn_handle, payload):
        # 1. Strip raw string to clear leading/trailing \r or \n
        payload = payload.strip()
        parts = payload.split(" ", 2)
        command = parts[0].strip().upper()

        if command == "SUB" and len(parts) >= 2:
            topic = parts[1].strip()
            if topic not in self._subscriptions:
                self._subscriptions[topic] = set()
            self._subscriptions[topic].add(conn_handle)
            print(f"[SUB] Handle {conn_handle} subscribed to: '{topic}'")
            self.publish_to_handle(conn_handle, f"ACK SUB {topic}")

        elif command == "PUB" and len(parts) >= 3:
            topic = parts[1].strip()
            # 2. Explicitly strip parts[2] to remove hidden \r or \n from the payload message

            message = parts[2].strip().upper()
            print(f"[PUB] Received on '{topic}': {message}")
            
            # --- Hardware Command Routing ---
            
            # NeoPixel Controls
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

            # Servo Controls
            elif topic == "servo/angle":
                try:
                    angle = int(message)
                    set_servo_angle(angle)
                    self.publish("servo/status", f"ANGLE: {angle}")
                except ValueError:
                    print("[!] Invalid Servo Angle payload")

            # Traffic Light Controls
            elif topic == "traffic/state":
                set_traffic_light(message)
                self.publish("traffic/status", f"STATE: {message}")

            elif topic == "traffic/fade":
                if ":" in message:
                    action, color = message.split(":", 1)
                    fade_traffic_light(color.strip(), action.strip())
                    self.publish("traffic/status", f"FADE {action}: {color}")

            # Re-broadcast payload to topic subscribers
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

    def check_pir_sensor(self):
        """Polls PIR Pin state and publishes telemetry on state change."""
        current_state = pir_sensor.value()
        if current_state != self.last_pir_state:
            self.last_pir_state = current_state
            state_text = "TRUE" if current_state == 1 else "FALSE"
            print(f"[PIR] State Changed -> {state_text}")
            self.publish("motion/state", state_text)

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
            # Poll hardware telemetry (PIR sensor)
            broker.check_pir_sensor()
            time.sleep_ms(100)

    except KeyboardInterrupt:
        print("\nShutting down...")
        turn_off_ring()
        set_traffic_light("OFF")
        servo_pwm.deinit()
        broker._ble.active(False)