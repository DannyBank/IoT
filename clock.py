import tkinter as tk
from datetime import datetime
import math
import random


# =========================================================
# WINDOW
# =========================================================

root = tk.Tk()

root.title("SidraCodes - Digital Clock")

WIDTH = 340
HEIGHT = 680

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


# =========================================================
# BACKGROUND
# =========================================================

def draw_background():

    # Very subtle horizontal background lines
    for y in range(0, HEIGHT, 10):
        canvas.create_line(
            0,
            y,
            WIDTH,
            y,
            fill="#030a12"
        )

    # Small glowing particles
    random.seed(15)

    for i in range(55):

        x = random.randint(5, WIDTH - 5)
        y = random.randint(500, HEIGHT - 20)

        if random.random() > 0.7:
            size = 3
            color = PURPLE
        else:
            size = 1
            color = CYAN

        canvas.create_oval(
            x - size,
            y - size,
            x + size,
            y + size,
            fill=color,
            outline=""
        )


draw_background()


# =========================================================
# HEADER
# =========================================================

canvas.create_text(
    20,
    43,
    text="OUTPUT",
    anchor="w",
    fill=GREEN,
    font=("Arial", 14, "bold")
)

canvas.create_text(
    WIDTH - 25,
    43,
    text=">_",
    fill=GREEN,
    font=("Courier New", 16, "bold")
)

canvas.create_line(
    0,
    63,
    WIDTH,
    63,
    fill="#26313b",
    width=1
)


# =========================================================
# CLOCK SETTINGS
# =========================================================

CX = WIDTH // 2
CY = 185

RADIUS = 104


# =========================================================
# NEON CLOCK RING
# =========================================================

def draw_neon_clock():

    # Outer glow
    glow_colors = [
        "#031923",
        "#04222c",
        "#062b38",
        "#08333f",
        "#0a3a46"
    ]

    for i, color in enumerate(glow_colors):

        r = RADIUS + 5 + i * 2

        canvas.create_oval(
            CX - r,
            CY - r,
            CX + r,
            CY + r,
            outline=color,
            width=2
        )

    # Main cyan circle
    canvas.create_oval(
        CX - RADIUS,
        CY - RADIUS,
        CX + RADIUS,
        CY + RADIUS,
        outline=CYAN,
        width=3
    )

    # Purple arc
    canvas.create_arc(
        CX - RADIUS,
        CY - RADIUS,
        CX + RADIUS,
        CY + RADIUS,
        start=300,
        extent=120,
        style=tk.ARC,
        outline=PURPLE,
        width=4
    )

    # Transition arc
    canvas.create_arc(
        CX - RADIUS,
        CY - RADIUS,
        CX + RADIUS,
        CY + RADIUS,
        start=250,
        extent=50,
        style=tk.ARC,
        outline="#433dff",
        width=3
    )

    # Clock ticks
    for i in range(60):

        angle = math.radians(i * 6 - 90)

        if i % 5 == 0:
            outer = RADIUS - 10
            inner = RADIUS - 21
            width = 2
        else:
            outer = RADIUS - 11
            inner = RADIUS - 18
            width = 1

        x1 = CX + math.cos(angle) * inner
        y1 = CY + math.sin(angle) * inner

        x2 = CX + math.cos(angle) * outer
        y2 = CY + math.sin(angle) * outer

        canvas.create_line(
            x1,
            y1,
            x2,
            y2,
            fill=CYAN,
            width=width
        )


draw_neon_clock()


# =========================================================
# DIGITAL CLOCK
# =========================================================

def update_clock():

    now = datetime.now()

    time_text = now.strftime("%I:%M:%S")
    period_text = now.strftime("%p")

    date_text = now.strftime("%A, %d %B %Y")

    # Delete old text
    canvas.delete("clock_time")
    canvas.delete("clock_period")
    canvas.delete("clock_date")

    # Digital time
    canvas.create_text(
        CX,
        CY + 2,
        text=time_text,
        fill=CYAN,
        font=("Courier New", 31, "bold"),
        tags="clock_time"
    )

    # AM / PM
    canvas.create_text(
        CX,
        CY + 45,
        text=period_text,
        fill=CYAN,
        font=("Arial", 15),
        tags="clock_period"
    )

    # Date
    canvas.create_text(
        CX,
        315,
        text=date_text,
        fill=MUTED,
        font=("Arial", 14),
        tags="clock_date"
    )

    # Run again after 1 second
    root.after(1000, update_clock)


# =========================================================
# INFORMATION CARD
# =========================================================

CARD_X1 = 43
CARD_Y1 = 340
CARD_X2 = WIDTH - 43
CARD_Y2 = 536


# Card shadow
canvas.create_rectangle(
    CARD_X1 + 2,
    CARD_Y1 + 3,
    CARD_X2 + 2,
    CARD_Y2 + 3,
    fill="#010409",
    outline=""
)

# Card
canvas.create_rounded_rectangle = None


# Tkinter Canvas does not have rounded_rectangle,
# so we create one manually.

def rounded_rectangle(x1, y1, x2, y2, radius, **kwargs):

    points = [
        x1 + radius, y1,
        x2 - radius, y1,
        x2, y1,
        x2, y1 + radius,

        x2, y2 - radius,
        x2, y2,
        x2 - radius, y2,

        x1 + radius, y2,
        x1, y2,
        x1, y2 - radius,

        x1, y1 + radius,
        x1, y1
    ]

    return canvas.create_polygon(
        points,
        smooth=True,
        **kwargs
    )


rounded_rectangle(
    CARD_X1,
    CARD_Y1,
    CARD_X2,
    CARD_Y2,
    18,
    fill="#0a101b",
    outline="#202b3a",
    width=1
)


# =========================================================
# BRANDING
# =========================================================

canvas.create_text(
    CX,
    367,
    text="SIDRACODES",
    fill=CYAN,
    font=("Arial", 18, "bold")
)

# Purple overlay on right side of brand
canvas.create_text(
    CX + 51,
    367,
    text="DES",
    fill=PURPLE,
    font=("Arial", 18, "bold")
)


canvas.create_text(
    CX,
    391,
    text="Digital Clock",
    fill=WHITE,
    font=("Arial", 11)
)


# =========================================================
# FEATURE ROW FUNCTION
# =========================================================

def feature_row(y, symbol, title, icon_color):

    # Icon circle
    canvas.create_oval(
        61,
        y - 8,
        76,
        y + 7,
        outline=icon_color,
        width=1
    )

    canvas.create_text(
        68.5,
        y - 1,
        text=symbol,
        fill=icon_color,
        font=("Arial", 9, "bold")
    )

    canvas.create_text(
        90,
        y,
        text=title,
        anchor="w",
        fill="#e6e6e6",
        font=("Arial", 10)
    )


# =========================================================
# FEATURES
# =========================================================

feature_row(
    420,
    "◷",
    "Real-time Updates",
    CYAN
)

feature_row(
    452,
    "♣",
    "Beautiful UI",
    "#a277ff"
)

feature_row(
    484,
    "ϟ",
    "Built with Python",
    "#55bfff"
)

feature_row(
    516,
    "♡",
    "Made with ♥ by SidraCodes",
    "#ff3b55"
)


# =========================================================
# BOTTOM NEON WAVE
# =========================================================

def draw_wave(base_y, amplitude, frequency, phase, color):

    points = []

    for x in range(0, WIDTH + 1, 2):

        y = (
            base_y
            + math.sin(x * frequency + phase) * amplitude
            + math.sin(x * frequency * 0.45 + phase) * amplitude * 0.4
        )

        points.append((x, y))

    # Draw connected lines
    for i in range(len(points) - 1):

        x1, y1 = points[i]
        x2, y2 = points[i + 1]

        canvas.create_line(
            x1,
            y1,
            x2,
            y2,
            fill=color,
            width=1
        )


# Multiple waves
draw_wave(
    594,
    18,
    0.035,
    0,
    "#006bff"
)

draw_wave(
    603,
    23,
    0.030,
    2,
    "#00cfff"
)

draw_wave(
    610,
    22,
    0.035,
    4,
    "#a000ff"
)

draw_wave(
    618,
    15,
    0.045,
    1,
    "#ff00e6"
)


# =========================================================
# WAVE GRID DOTS
# =========================================================

random.seed(10)

for x in range(0, WIDTH, 8):

    y = (
        605
        + math.sin(x * 0.035) * 20
    )

    canvas.create_oval(
        x,
        y,
        x + 1,
        y + 1,
        fill=CYAN,
        outline=""
    )


# =========================================================
# START CLOCK
# =========================================================

update_clock()

root.mainloop()