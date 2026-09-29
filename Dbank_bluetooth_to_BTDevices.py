import bluetooth
import time
from micropython import const

# BLE Flag Constants
_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_WRITE = const(3)

_FLAG_WRITE = const(0x0008)
_FLAG_NOTIFY = const(0x0010)

# Nordic UART Service (NUS) UUIDs
_UART_UUID = bluetooth.UUID("6E400001-B5A3-F393-E0A9-E50E24DCCA9E")
_UART_RX = (bluetooth.UUID("6E400002-B5A3-F393-E0A9-E50E24DCCA9E"), _FLAG_WRITE)
_UART_TX = (bluetooth.UUID("6E400003-B5A3-F393-E0A9-E50E24DCCA9E"), _FLAG_NOTIFY)
_UART_SERVICE = (_UART_UUID, (_UART_TX, _UART_RX))


class BLEMQTTBroker:
    def __init__(self, name="ESP32-MQTT-BLE"):
        self._ble = bluetooth.BLE()
        self._ble.active(True)
        self._ble.irq(self._irq)
        
        # Register GATT Nordic UART Service
        ((self._handle_tx, self._handle_rx),) = self._ble.gatts_register_services((_UART_SERVICE,))
        
        self._connections = set()
        self._subscriptions = {}  # Format: {"topic_name": [connection_handles]}
        self._name = name
        self._advertise()

    def _advertise(self, interval_us=100000):
        """Broadcast BLE advertisements with device name."""
        name_bytes = self._name.encode("utf-8")
        # Structure payload: Flags + Complete Local Name
        payload = b"\x02\x01\x06" + bytes([len(name_bytes) + 1, 0x09]) + name_bytes
        self._ble.gap_advertise(interval_us, adv_data=payload)
        print(f"[+] BLE MQTT Broker Advertising as '{self._name}'")

    def _irq(self, event, data):
        """Handle BLE Events."""
        if event == _IRQ_CENTRAL_CONNECT:
            conn_handle, _, _ = data
            self._connections.add(conn_handle)
            print(f"[+] Client connected: handle {conn_handle}")

        elif event == _IRQ_CENTRAL_DISCONNECT:
            conn_handle, _, _ = data
            self._connections.remove(conn_handle)
            # Remove connection handle from topic subscriptions
            for topic in self._subscriptions:
                if conn_handle in self._subscriptions[topic]:
                    self._subscriptions[topic].remove(conn_handle)
            print(f"[-] Client disconnected: handle {conn_handle}")
            self._advertise()

        elif event == _IRQ_GATTS_WRITE:
            conn_handle, value_handle = data
            if value_handle == self._handle_rx:
                # Read incoming payload sent to RX characteristic
                payload = self._ble.gatts_read(self._handle_rx).decode("utf-8").strip()
                self._parse_mqtt_packet(conn_handle, payload)

    def _parse_mqtt_packet(self, conn_handle, payload):
        """
        Parses encapsulated MQTT messages over BLE UART:
        - SUBSCRIBE: "SUB <topic>"
        - PUBLISH:   "PUB <topic> <message>"
        """
        parts = payload.split(" ", 2)
        command = parts[0].upper()

        if command == "SUB" and len(parts) >= 2:
            topic = parts[1]
            if topic not in self._subscriptions:
                self._subscriptions[topic] = set()
            self._subscriptions[topic].add(conn_handle)
            print(f"[SUB] Handle {conn_handle} subscribed to topic: '{topic}'")
            # Ack back to subscriber
            self.publish_to_client(conn_handle, f"ACK SUB {topic}")

        elif command == "PUB" and len(parts) >= 3:
            topic = parts[1]
            message = parts[2]
            print(f"[PUB] Message on '{topic}': {message}")
            self.publish(topic, message)

        else:
            print(f"[!] Invalid MQTT packet format: {payload}")

    def publish(self, topic, message):
        """
        Publishes an MQTT message over BLE to all subscribed handles.
        Format emitted: "MQTT:<topic>:<message>"
        """
        formatted_payload = f"MQTT:{topic}:{message}\n".encode("utf-8")
        
        if topic in self._subscriptions:
            for handle in self._subscriptions[topic]:
                try:
                    self._ble.gatts_notify(handle, self._handle_tx, formatted_payload)
                except Exception as e:
                    print(f"[!] Failed to notify handle {handle}: {e}")

    def publish_to_client(self, conn_handle, message):
        """Send direct notification to a specific client handle."""
        payload = f"{message}\n".encode("utf-8")
        try:
            self._ble.gatts_notify(conn_handle, self._handle_tx, payload)
        except Exception as e:
            print(f"[!] Notification error: {e}")


# ==========================================
# MAIN EXECUTION DEMO
# ==========================================
if __name__ == "__main__":
    broker = BLEMQTTBroker(name="ESP32-MQTT-BLE")

    counter = 0
    try:
        while True:
            # Periodically publish telemetry to subscribed BLE clients
            broker.publish("telemetry/status", f"uptime_sec={counter}")
            counter += 5
            time.sleep(5)

    except KeyboardInterrupt:
        print("\nStopping BLE MQTT Broker...")
        broker._ble.active(False)