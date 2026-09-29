import json
import socket
import threading
import time
import tkinter as tk
import customtkinter as ctk

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class CircularGauge(tk.Canvas):
    """Custom circular gauge UI component."""

    def __init__(self, parent, size=160, min_val=0, max_val=100, unit=""):
        super().__init__(
            parent,
            width=size,
            height=size,
            bg="#2b2b2b",
            highlightthickness=0,
        )
        self.size = size
        self.min_val = min_val
        self.max_val = max_val
        self.unit = unit
        self.value = min_val
        self.padding = 15
        self.arc_bbox = (
            self.padding,
            self.padding,
            self.size - self.padding,
            self.size - self.padding,
        )
        self.draw_gauge()

    def draw_gauge(self):
        self.delete("all")
        self.create_arc(
            self.arc_bbox,
            start=-30,
            extent=-240,
            outline="#3a3a3a",
            width=12,
            style="arc",
        )
        sweep = -240 * (
            (self.value - self.min_val) / (self.max_val - self.min_val)
        )
        color = "#3B82F6" if self.value < (self.max_val * 0.75) else "#EF4444"
        self.create_arc(
            self.arc_bbox,
            start=-30,
            extent=sweep,
            outline=color,
            width=12,
            style="arc",
        )
        self.create_text(
            self.size / 2,
            self.size / 2 - 5,
            text=f"{self.value:.1f}{self.unit}",
            fill="white",
            font=("Helvetica", 16, "bold"),
        )

    def set_value(self, new_val):
        self.value = max(self.min_val, min(self.max_val, new_val))
        self.draw_gauge()


class ESP32RemoteDashboard(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("ESP32 Wi-Fi Remote Dashboard")
        self.geometry("720x480")
        self.resizable(False, False)

        # Network Target (Default ESP32 AP IP)
        self.esp_ip = "192.168.4.1"
        self.esp_port = 5000

        # UI Layout
        self.header = ctk.CTkLabel(
            self,
            text="ESP32 AP Telemetry Monitor",
            font=ctk.CTkFont(size=22, weight="bold"),
        )
        self.header.pack(pady=(15, 2))

        self.status_label = ctk.CTkLabel(
            self, text="● Connecting to ESP32 AP...", text_color="#F59E0B"
        )
        self.status_label.pack(pady=(0, 15))

        self.grid_frame = ctk.CTkFrame(self)
        self.grid_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        self.grid_frame.columnconfigure((0, 1), weight=1)
        self.grid_frame.rowconfigure((0, 1), weight=1)

        # Metric Cards
        self.temp_card = ctk.CTkFrame(self.grid_frame)
        self.temp_card.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        ctk.CTkLabel(
            self.temp_card,
            text="Die Temperature",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(pady=(10, 0))
        self.temp_gauge = CircularGauge(
            self.temp_card, min_val=20, max_val=90, unit="°C"
        )
        self.temp_gauge.pack(pady=10)

        self.cpu_card = ctk.CTkFrame(self.grid_frame)
        self.cpu_card.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        ctk.CTkLabel(
            self.cpu_card,
            text="CPU Frequency",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(pady=(10, 5))
        self.cpu_freq_label = ctk.CTkLabel(
            self.cpu_card,
            text="-- MHz",
            font=ctk.CTkFont(size=24, weight="bold"),
        )
        self.cpu_freq_label.pack(pady=30)

        self.ram_card = ctk.CTkFrame(self.grid_frame)
        self.ram_card.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        ctk.CTkLabel(
            self.ram_card,
            text="Heap Memory",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(pady=(15, 5))
        self.ram_val_label = ctk.CTkLabel(self.ram_card, text="Free: -- KB")
        self.ram_val_label.pack(pady=2)
        self.ram_bar = ctk.CTkProgressBar(self.ram_card, width=220)
        self.ram_bar.pack(pady=15)

        self.flash_card = ctk.CTkFrame(self.grid_frame)
        self.flash_card.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        ctk.CTkLabel(
            self.flash_card,
            text="Flash Memory",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(pady=(15, 5))
        self.flash_val_label = ctk.CTkLabel(self.flash_card, text="Size: -- MB")
        self.flash_val_label.pack(pady=2)
        self.flash_bar = ctk.CTkProgressBar(
            self.flash_card, width=220, progress_color="#8B5CF6"
        )
        self.flash_bar.pack(pady=15)
        self.flash_bar.set(1.0)

        # Threading for background network communication
        self.running = True
        self.client_thread = threading.Thread(
            target=self.network_client_loop, daemon=True
        )
        self.client_thread.start()

    def update_ui_controls(self, data):
        """Safely updates UI controls with JSON telemetry."""
        self.temp_gauge.set_value(data.get("temp_c", 0))
        self.cpu_freq_label.configure(
            text=f"{data.get('cpu_freq', '--')} MHz"
        )

        free_ram = data.get("free_ram_kb", 0)
        total_ram = data.get("total_ram_kb", 1)
        used_ratio = 1.0 - (free_ram / total_ram)

        self.ram_val_label.configure(
            text=f"Free: {free_ram:.1f} KB / {total_ram:.1f} KB"
        )
        self.ram_bar.set(used_ratio)
        self.flash_val_label.configure(
            text=f"Size: {data.get('flash_mb', 0)} MB"
        )

    def network_client_loop(self):
        """Continuously attempts to connect and stream telemetry from the ESP32."""
        while self.running:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(3.0)
                s.connect((self.esp_ip, self.esp_port))

                self.status_label.configure(
                    text=f"● Connected to ESP32 ({self.esp_ip})",
                    text_color="#10B981",
                )

                buffer = ""
                while self.running:
                    chunk = s.recv(1024).decode("utf-8")
                    if not chunk:
                        break

                    buffer += chunk
                    while "\n" in buffer:
                        line, buffer = buffer.split("\n", 1)
                        if line.strip():
                            data = json.loads(line)
                            # Schedule UI updates back on the main thread
                            self.after(0, self.update_ui_controls, data)

            except Exception:
                self.status_label.configure(
                    text="● Disconnected. Retrying connection...",
                    text_color="#EF4444",
                )
                time.sleep(2)
            finally:
                try:
                    s.close()
                except Exception:
                    pass


if __name__ == "__main__":
    app = ESP32RemoteDashboard()
    app.mainloop()