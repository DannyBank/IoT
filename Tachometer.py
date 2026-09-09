import tkinter as tk
import math
import random


# =========================================================
# WINDOW
# =========================================================

root = tk.Tk()
root.title("SidraCodes - Tachometer")

WIDTH = 360
HEIGHT = 660

root.geometry(f"{WIDTH}x{HEIGHT}")
root.resizable(False, False)
root.configure(bg="#02060d")


# =========================================================
# CANVAS
# =========================================================

canvas = tk.Canvas(
    root,
    width=WIDTH,
    height=HEIGHT,
    bg="#02060d",
    highlightthickness=0
)

canvas.pack()


# =========================================================
# COLORS
# =========================================================

BG = "#02060d"
CYAN = "#00dfff"
PURPLE = "#8b20ff"
GREEN = "#8cff35"
WHITE = "#eeeeee"
MUTED = "#aaa4d0"
RED = "#ff3b55"
ORANGE = "#ff9a2e"


# =========================================================
# BACKGROUND
# =========================================================

def draw_background():

    for y in range(0, HEIGHT, 10):
        canvas.create_line(0, y, WIDTH, y, fill="#030a12")

    random.seed(15)

    for i in range(45):
        x = random.randint(5, WIDTH - 5)
        y = random.randint(560, HEIGHT - 20)

        if random.random() > 0.7:
            size, color = 3, PURPLE
        else:
            size, color = 1, CYAN

        canvas.create_oval(x - size, y - size, x + size, y + size,
                            fill=color, outline="")


draw_background()


# =========================================================
# HEADER
# =========================================================

canvas.create_text(20, 43, text="TACHOMETER", anchor="w", fill=GREEN,
                    font=("Arial", 14, "bold"))

canvas.create_text(WIDTH - 25, 43, text=">_", fill=GREEN,
                    font=("Courier New", 16, "bold"))

canvas.create_line(0, 63, WIDTH, 63, fill="#26313b", width=1)


# =========================================================
# GAUGE GEOMETRY HELPERS
#
# We use an angle PHI (degrees) where:
#   PHI = 0    -> 3 o'clock (right)
#   PHI = 90   -> 6 o'clock (bottom)
#   PHI = 180  -> 9 o'clock (left)
#   PHI = -90  -> 12 o'clock (top)
# increasing PHI sweeps clockwise on screen.
#
# The gauge idles at PHI=135 (down-left) and sweeps clockwise,
# up over the top, to PHI=405 (=45, down-right) at max RPM.
# That's a 270 degree sweep, which is the classic car-tach look.
# =========================================================

CX = WIDTH // 2
CY = 210
RADIUS = 128

IDLE_PHI = 135
SWEEP = 270


def point(r, phi_deg):
    rad = math.radians(phi_deg)
    return CX + r * math.cos(rad), CY + r * math.sin(rad)


def tk_arc_params(phi_a, phi_b):
    """Convert a PHI sweep [phi_a, phi_b] (phi_a < phi_b) into the
    (start, extent) pair create_arc expects."""
    start = (-phi_b) % 360
    extent = phi_b - phi_a
    return start, extent


# =========================================================
# RPM SETTINGS
# =========================================================

IDLE_RPM = 900
MAX_RPM = 8000
REDLINE_RPM = 6500
TICK_STEP = 1000

ACCEL_RATE = 0.06   # fraction of remaining gap closed per tick while held
DECAY_RATE = 0.035  # fraction of gap-to-idle closed per tick while released
DT_MS = 25          # physics/redraw tick interval


def rpm_to_phi(rpm):
    frac = max(0.0, min(1.0, rpm / MAX_RPM))
    return IDLE_PHI + frac * SWEEP


# =========================================================
# STATIC GAUGE FACE
# =========================================================

def draw_gauge_face():

    # Outer glow rings
    glow_colors = ["#031923", "#04222c", "#062b38", "#08333f", "#0a3a46"]
    for i, color in enumerate(glow_colors):
        r = RADIUS + 6 + i * 2
        canvas.create_oval(CX - r, CY - r, CX + r, CY + r,
                            outline=color, width=2)

    # Main ring, cyan portion (idle -> redline)
    redline_phi = rpm_to_phi(REDLINE_RPM)
    max_phi = rpm_to_phi(MAX_RPM)

    s, e = tk_arc_params(IDLE_PHI, redline_phi)
    canvas.create_arc(CX - RADIUS, CY - RADIUS, CX + RADIUS, CY + RADIUS,
                       start=s, extent=e, style=tk.ARC, outline=CYAN, width=3)

    # Redline portion of the ring, in red
    s, e = tk_arc_params(redline_phi, max_phi)
    canvas.create_arc(CX - RADIUS, CY - RADIUS, CX + RADIUS, CY + RADIUS,
                       start=s, extent=e, style=tk.ARC, outline=RED, width=4)

    # Faint purple accent arc across the top, purely decorative
    canvas.create_arc(CX - RADIUS, CY - RADIUS, CX + RADIUS, CY + RADIUS,
                       start=60, extent=60, style=tk.ARC, outline=PURPLE, width=2)

    # Ticks + labels
    n_ticks = MAX_RPM // TICK_STEP
    for i in range(n_ticks + 1):
        rpm_val = i * TICK_STEP
        phi = rpm_to_phi(rpm_val)

        is_major = True
        outer = RADIUS - 8
        inner = RADIUS - 22 if is_major else RADIUS - 16

        x1, y1 = point(inner, phi)
        x2, y2 = point(outer, phi)

        tick_color = RED if rpm_val >= REDLINE_RPM else CYAN
        canvas.create_line(x1, y1, x2, y2, fill=tick_color, width=2)

        # minor tick halfway to next major tick
        if rpm_val < MAX_RPM:
            mid_phi = rpm_to_phi(rpm_val + TICK_STEP / 2)
            mx1, my1 = point(RADIUS - 12, mid_phi)
            mx2, my2 = point(RADIUS - 8, mid_phi)
            mid_color = RED if (rpm_val + TICK_STEP / 2) >= REDLINE_RPM else CYAN
            canvas.create_line(mx1, my1, mx2, my2, fill=mid_color, width=1)

        # numeric label every other tick to avoid clutter
        if i % 2 == 0:
            lx, ly = point(RADIUS - 36, phi)
            canvas.create_text(lx, ly, text=str(i), fill=WHITE,
                                font=("Arial", 10, "bold"))

    # "x1000 RPM" caption
    cap_x, cap_y = point(RADIUS - 58, 90)
    canvas.create_text(cap_x, cap_y, text="x1000 RPM", fill=MUTED,
                        font=("Arial", 9))


draw_gauge_face()


# =========================================================
# DYNAMIC NEEDLE + READOUT
# =========================================================

current_rpm = IDLE_RPM
accelerating = False


def draw_needle(rpm):

    canvas.delete("needle")

    phi = rpm_to_phi(rpm)

    # light vibration, more pronounced at higher rpm
    jitter = random.uniform(-1, 1) * (rpm / MAX_RPM) * 1.6
    phi_j = phi + jitter

    needle_color = RED if rpm >= REDLINE_RPM else CYAN

    # tail counterweight
    tx, ty = point(28, phi_j + 180)
    canvas.create_line(CX, CY, tx, ty, fill=PURPLE, width=5, tags="needle")

    # glow underlay for the needle (wide + dim, then narrow + bright)
    tip_x, tip_y = point(RADIUS - 26, phi_j)
    canvas.create_line(CX, CY, tip_x, tip_y, fill="#0a3a46", width=9,
                        tags="needle")
    canvas.create_line(CX, CY, tip_x, tip_y, fill=needle_color, width=4,
                        tags="needle")

    # hub
    canvas.create_oval(CX - 9, CY - 9, CX + 9, CY + 9,
                        fill="#101826", outline=needle_color, width=2,
                        tags="needle")


def draw_readout(rpm):

    canvas.delete("readout")

    rpm_text = f"{int(round(rpm)):>5}"
    rpm_color = RED if rpm >= REDLINE_RPM else CYAN

    canvas.create_text(CX, CY + RADIUS + 34, text=rpm_text, fill=rpm_color,
                        font=("Courier New", 30, "bold"), tags="readout")

    canvas.create_text(CX, CY + RADIUS + 62, text="RPM", fill=MUTED,
                        font=("Arial", 12), tags="readout")

    if rpm >= REDLINE_RPM:
        status = "REDLINE!"
        status_color = RED
    elif accelerating:
        status = "ACCELERATING"
        status_color = ORANGE
    elif rpm > IDLE_RPM + 50:
        status = "DECELERATING"
        status_color = MUTED
    else:
        status = "IDLE"
        status_color = GREEN

    canvas.create_text(CX, CY + RADIUS + 84, text=status, fill=status_color,
                        font=("Arial", 11, "bold"), tags="readout")


# =========================================================
# PHYSICS LOOP
# =========================================================

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
# INFORMATION CARD
# =========================================================

CARD_X1 = 33
CARD_Y1 = CY + RADIUS + 110
CARD_X2 = WIDTH - 33
CARD_Y2 = CARD_Y1 + 220

canvas.create_rectangle(CARD_X1 + 2, CARD_Y1 + 3, CARD_X2 + 2, CARD_Y2 + 3,
                         fill="#010409", outline="")


def rounded_rectangle(x1, y1, x2, y2, radius, **kwargs):
    points = [
        x1 + radius, y1, x2 - radius, y1, x2, y1, x2, y1 + radius,
        x2, y2 - radius, x2, y2, x2 - radius, y2,
        x1 + radius, y2, x1, y2, x1, y2 - radius,
        x1, y1 + radius, x1, y1
    ]
    return canvas.create_polygon(points, smooth=True, **kwargs)


rounded_rectangle(CARD_X1, CARD_Y1, CARD_X2, CARD_Y2, 18,
                   fill="#0a101b", outline="#202b3a", width=1)

canvas.create_text(CX, CARD_Y1 + 27, text="GAS PEDAL", fill=CYAN,
                    font=("Arial", 18, "bold"))

canvas.create_text(CX, CARD_Y1 + 51, text="Hold to accelerate, release to coast",
                    fill=WHITE, font=("Arial", 10))


# =========================================================
# THE "PUSH BUTTON" (mouse hold or spacebar)
# =========================================================

def on_press(event=None):
    global accelerating
    accelerating = True
    pedal_btn.config(bg="#123", fg=ORANGE)


def on_release(event=None):
    global accelerating
    accelerating = False
    pedal_btn.config(bg="#0a101b", fg=CYAN)


pedal_btn = tk.Button(
    root,
    text="HOLD\n(or press SPACE)",
    font=("Arial", 13, "bold"),
    bg="#0a101b",
    fg=CYAN,
    activebackground="#123",
    activeforeground=ORANGE,
    relief="flat",
    bd=0,
    highlightthickness=2,
    highlightbackground=CYAN,
)

pedal_btn.bind("<ButtonPress-1>", on_press)
pedal_btn.bind("<ButtonRelease-1>", on_release)

canvas.create_window(CX, CARD_Y1 + 100, window=pedal_btn, width=190, height=64)

root.bind("<KeyPress-space>", on_press)
root.bind("<KeyRelease-space>", on_release)
root.focus_set()


# =========================================================
# FEATURE ROWS
# =========================================================

def feature_row(y, symbol, title, icon_color):
    canvas.create_oval(51, y - 8, 66, y + 7, outline=icon_color, width=1)
    canvas.create_text(58.5, y - 1, text=symbol, fill=icon_color,
                        font=("Arial", 9, "bold"))
    canvas.create_text(80, y, text=title, anchor="w", fill="#e6e6e6",
                        font=("Arial", 10))


feature_row(CARD_Y1 + 150, "◷", "Eased accel / slow decay", CYAN)
feature_row(CARD_Y1 + 178, "⚠", f"Redline warning at {REDLINE_RPM} RPM", RED)
feature_row(CARD_Y1 + 206, "⌨", "Mouse hold or spacebar", "#a277ff")


# =========================================================
# START
# =========================================================

update_gauge()
root.mainloop()