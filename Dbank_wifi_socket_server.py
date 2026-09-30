import socket
import select
import network
import time

# 1. Setup ESP32 as Wi-Fi Access Point
ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid="ESP32-Hub", password="password123")

while not ap.active():
    pass

print("AP Active. IP:", ap.ifconfig()[0])

# 2. Initialize TCP Server (Hub / Broker)
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(('0.0.0.0', 1234))
server.listen(5)
server.setblocking(False)

clients = []

print("TCP Pub/Sub Server listening on port 1234...")

# Main loop to handle routing and local execution
def run_hub():
    while True:
        # Check for new incoming subscriber/publisher connections
        r, _, _ = select.select([server] + clients, [], [], 0.1)
        
        for sock in r:
            if sock == server:
                conn, addr = server.accept()
                conn.setblocking(False)
                clients.append(conn)
                print(f"New client connected: {addr}")
            else:
                try:
                    data = sock.recv(1024)
                    if data:
                        message = data.decode('utf-8').strip()
                        print(f"[Subscriber Received]: {message}")
                        
                        # Broadcast message to all connected clients
                        for client in clients:
                            if client != sock:
                                client.sendall(data)
                    else:
                        clients.remove(sock)
                        sock.close()
                except Exception:
                    if sock in clients:
                        clients.remove(sock)
                        sock.close()
                        
        time.sleep(0.1)

# Run loop
run_hub()