import bluetooth
import time
from micropython import const

_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_WRITE = const(3)

_FLAG_WRITE = const(0x0008)
_FLAG_NOTIFY = const(0x0010)

# Nordic UART Service UUIDs
_UART_UUID = bluetooth.UUID("6E400001-B5A3-F393-E0A9-E50E24DCCA9E")
_UART_RX = (bluetooth.UUID("6E400002-B5A3-F393-E0A9-E50E24DCCA9E"), _FLAG_WRITE)
_UART_TX = (bluetooth.UUID("6E400003-B5A3-F393-E0A9-E50E24DCCA9E"), _FLAG_NOTIFY)
_UART_SERVICE = (_UART_UUID, (_UART_TX, _UART_RX))

# ESP32 hardware hardware limits (usually up to 4-7 concurrent connections)
MAX_CONNECTIONS = 4


class MultiClientBLEServer:
    def __init__(self, name="ESP32-Multi-BLE"):
        self._ble = bluetooth.BLE()
        self._ble.active(True)
        self._ble.irq(self._irq)

        # Register GATT services
        ((self._handle_tx, self._handle_rx),) = self._ble.gatts_register_services((_UART_SERVICE,))

        # Store all connected central handles
        self.connections = set()
        self._name = name
        self._advertise()

    def _advertise(self, interval_us=100000):
        """Starts BLE advertising if connection limits have not been reached."""
        if len(self.connections) >= MAX_CONNECTIONS:
            print("[!] Maximum connection limit reached. Pausing advertising.")
            return

        name_bytes = self._name.encode("utf-8")
        payload = b"\x02\x01\x06" + bytes([len(name_bytes) + 1, 0x09]) + name_bytes
        
        # Start advertising
        self._ble.gap_advertise(interval_us, adv_data=payload)
        print(f"[+] Advertising as '{self._name}' (Active connections: {len(self.connections)})")

    def _irq(self, event, data):
        if event == _IRQ_CENTRAL_CONNECT:
            conn_handle, addr_type, addr = data
            mac_str = ":".join("{:02X}".format(b) for b in addr)
            
            self.connections.add(conn_handle)
            print(f"\n[+] NEW CONNECTION! Handle: {conn_handle} | MAC: {mac_str}")
            print(f"    Total Connected Devices: {len(self.connections)}")

            # CRITICAL STEP: Restart advertising so other devices can discover and connect!
            self._advertise()

        elif event == _IRQ_CENTRAL_DISCONNECT:
            conn_handle, addr_type, addr = data
            if conn_handle in self.connections:
                self.connections.remove(conn_handle)
            
            print(f"\n[-] DISCONNECTED! Handle: {conn_handle}")
            print(f"    Remaining Connected Devices: {len(self.connections)}")

            # Resume advertising if a slot freed up
            self._advertise()

        elif event == _IRQ_GATTS_WRITE:
            conn_handle, value_handle = data
            if value_handle == self._handle_rx:
                payload = self._ble.gatts_read(self._handle_rx).decode("utf-8").strip()
                print(f"[RX from Handle {conn_handle}]: {payload}")
                
                # Echo message back to ALL connected clients
                self.broadcast(f"Handle {conn_handle} says: {payload}")

    def broadcast(self, message):
        """Send a notification message to EVERY connected central device."""
        if not self.connections:
            return

        payload = (message + "\n").encode("utf-8")
        
        # Iterate over a copy of the connection handle set
        for handle in list(self.connections):
            try:
                self._ble.gatts_notify(handle, self._handle_tx, payload)
            except Exception as e:
                print(f"[!] Failed to send to handle {handle}: {e}")

    def send_to_handle(self, conn_handle, message):
        """Send a direct message to ONE specific connected central device."""
        if conn_handle in self.connections:
            payload = (message + "\n").encode("utf-8")
            try:
                self._ble.gatts_notify(conn_handle, self._handle_tx, payload)
            except Exception as e:
                print(f"[!] Target send error (Handle {conn_handle}): {e}")


# ==========================================
# MAIN EXECUTION DEMO
# ==========================================
if __name__ == "__main__":
    ble_server = MultiClientBLEServer(name="ESP32-Multi-BLE")

    counter = 0
    try:
        while True:
            # Periodically broadcast uptime tick to all connected phones
            if ble_server.connections:
                ble_server.broadcast(f"Server Uptime: {counter}s")
            
            counter += 5
            time.sleep(5)

    except KeyboardInterrupt:
        print("\nShutting down BLE Server...")
        ble_server._ble.active(False)