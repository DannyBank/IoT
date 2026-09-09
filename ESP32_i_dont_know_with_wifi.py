import tkinter as tk
import math
import random
import socket  # Uses built-in socket module instead of pyserial

# =========================================================
# NETWORK CONFIGURATION
# =========================================================
ESP32_IP = "192.168.8.140"  # CHANGE THIS to your ESP32 IP address
UDP_PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# =========================================================
# WINDOW & CANVAS
# =========================================================
root = tk.Tk()
root.title("SidraCodes - Tachometer")
WIDTH, HEIGHT = 360, 660
root.geometry(f"{WIDTH}x{HEIGHT}")
root.resizable(False, False)
root.configure(bg="#02060d")

canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="#02060d", highlightthickness=0)
canvas.pack()

# =========================================================
# COLORS & BACKGROUND
# =========================================================
BG, CYAN, PURPLE, GREEN, WHITE, MUTED, RED, ORANGE = (
    "#02060d", "#00dfff", "#8b20ff", "#8cff35", "#eeeeee", "#aaa4d0", "#ff3b55", "#ff9a2e"
)

def draw_background():
    for y in range(0, HEIGHT, 10):
        canvas.create_line(0, y, WIDTH, y, fill="#030a12")
    random.seed(15)
    for i in range(45):
        x = random.randint(5, WIDTH - 5)
        y = random.randint(560, HEIGHT - 20)
        size, color = (3, PURPLE) if random.random() > 0.7 else (1, CYAN)
        canvas.create_oval(x - size, y - size, x + size, y + size, fill=color, outline="")

draw_background()

# =========================================================
# HEADER & GAUGE GEOMETRY
# =========================================================
canvas.create_text(20, 43, text="TACHOMETER", anchor="w", fill=GREEN, font=("Arial", 14, "bold"))
canvas.create_text(WIDTH - 25, 43, text=">_", fill=GREEN, font=("Courier New", 16, "bold"))
canvas.create_line(0, 63, WIDTH, 63, fill="#26313b", width=1)

CX, CY, RADIUS = WIDTH // 2, 210, 128
IDLE_PHI, SWEEP = 135, 270

def point(r, phi_deg):
    rad = math.radians(phi_deg)
    return CX + r * math.cos(rad), CY + r * math.sin(rad)

def tk_arc_params(phi_a, phi_b):
    return (-phi_b) % 360, phi_b - phi_a

IDLE_RPM, MAX_RPM, REDLINE_RPM, TICK_STEP = 900, 8000, 6500, 1000
ACCEL_RATE, DECAY_RATE, DT_MS = 0.06, 0.035, 25

def rpm_to_phi(rpm):
    return IDLE_PHI + max(0.0, min(1.0, rpm / MAX_RPM)) * SWEEP

def draw_gauge_face():
    glow_colors = ["#031923", "#04222c", "#062b38", "#08333f", "#0a3a46"]
    for i, color in enumerate(glow_colors):
        r = RADIUS + 6 + i * 2
        canvas.create_oval(CX - r, CY - r, CX + r, CY + r, outline=color, width=2)

    redline_phi, max_phi = rpm_to_phi(REDLINE_RPM), rpm_to_phi(MAX_RPM)
    s, e = tk_arc_params(IDLE_PHI, redline_phi)
    canvas.create_arc(CX - RADIUS, CY - RADIUS, CX + RADIUS, CY + RADIUS, start=s, extent=e, style=tk.ARC, outline=CYAN, width=3)
    s, e = tk_arc_params(redline_phi, max_phi)
    canvas.create_arc(CX - RADIUS, CY - RADIUS, CX + RADIUS, CY + RADIUS, start=s, extent=e, style=tk.ARC, outline=RED, width=4)

    for i in range((MAX_RPM // TICK_STEP) + 1):
        rpm_val = i * TICK_STEP
        phi = rpm_to_phi(rpm_val)
        x1, y1 = point(RADIUS - 22, phi)
        x2, y2 = point(RADIUS - 8, phi)
        canvas.create_line(x1, y1, x2, y2, fill=RED if rpm_val >= REDLINE_RPM else CYAN, width=2)
        if i % 2 == 0:
            lx, ly = point(RADIUS - 36, phi)
            canvas.create_text(lx, ly, text=str(i), fill=WHITE, font=("Arial", 10, "bold"))

draw_gauge_face()

# =========================================================
# DYNAMIC NEEDLE & READOUT
# =========================================================
current_rpm = IDLE_RPM
accelerating = False

def draw_needle(rpm):
    canvas.delete("needle")
    phi = rpm_to_phi(rpm) + random.uniform(-1, 1) * (rpm / MAX_RPM) * 1.6
    needle_color = RED if rpm >= REDLINE_RPM else CYAN
    tx, ty = point(28, phi + 180)
    canvas.create_line(CX, CY, tx, ty, fill=PURPLE, width=5, tags="needle")
    tip_x, tip_y = point(RADIUS - 26, phi)
    canvas.create_line(CX, CY, tip_x, tip_y, fill="#0a3a46", width=9, tags="needle")
    canvas.create_line(CX, CY, tip_x, tip_y, fill=needle_color, width=4, tags="needle")
    canvas.create_oval(CX - 9, CY - 9, CX + 9, CY + 9, fill="#101826", outline=needle_color, width=2, tags="needle")

def draw_readout(rpm):
    canvas.delete("readout")
    rpm_color = RED if rpm >= REDLINE_RPM else CYAN
    canvas.create_text(CX, CY + RADIUS + 34, text=f"{int(round(rpm)):>5}", fill=rpm_color, font=("Courier New", 30, "bold"), tags="readout")
    canvas.create_text(CX, CY + RADIUS + 62, text="RPM", fill=MUTED, font=("Arial", 12), tags="readout")

def update_gauge():
    global current_rpm
    if accelerating:
        current_rpm += (MAX_RPM - current_rpm) * ACCEL_RATE
        current_rpm = min(current_rpm, MAX_RPM)
    else:
        current_rpm -= (current_rpm - IDLE_RPM) * DECAY_RATE
        current_rpm = max(current_rpm, IDLE_RPM)

    draw_needle(current_rpm)
    draw_readout(current_rpm)
    root.after(DT_MS, update_gauge)

# =========================================================
# KEY/BUTTON CONTROLS (WI-FI UDP SENDING)
# =========================================================
def send_wifi_signal(state):
    try:
        sock.sendto(state.encode('utf-8'), (ESP32_IP, UDP_PORT))
    except Exception as e:
        print(f"Network error: {e}")

def on_press(event=None):
    global accelerating
    if not accelerating:
        accelerating = True
        pedal_btn.config(bg="#123", fg=ORANGE)
        send_wifi_signal("1")  # Transmit press over Wi-Fi

def on_release(event=None):
    global accelerating
    if accelerating:
        accelerating = False
        pedal_btn.config(bg="#0a101b", fg=CYAN)
        send_wifi_signal("0")  # Transmit release over Wi-Fi

pedal_btn = tk.Button(
    root, text="HOLD\n(or press SPACE)", font=("Arial", 13, "bold"),
    bg="#0a101b", fg=CYAN, activebackground="#123", activeforeground=ORANGE,
    relief="flat", bd=0, highlightthickness=2, highlightbackground=CYAN,
)

pedal_btn.bind("<ButtonPress-1>", on_press)
pedal_btn.bind("<ButtonRelease-1>", on_release)
canvas.create_window(CX, CY + RADIUS + 210, window=pedal_btn, width=190, height=64)

root.bind("<KeyPress-space>", on_press)
root.bind("<KeyRelease-space>", on_release)
root.focus_set()

# =========================================================
# START
# =========================================================
update_gauge()
root.mainloop()
sock.close()