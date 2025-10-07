import serial
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque
import numpy as np

PORT = 'COM3'      
BAUD = 115200
WINDOW = 200      

ser = serial.Serial(PORT, BAUD, timeout=1)

pitch_buf = deque(maxlen=WINDOW)
x_idx     = deque(maxlen=WINDOW)

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10,6))

(line_pitch,) = ax1.plot([], [], label="Pitch (°)", color='blue')
ax1.set_xlim(0, WINDOW)
ax1.set_ylim(-180, 180)
ax1.set_xlabel("Samples")
ax1.set_ylabel("Pitch (°)")
ax1.set_title("MPU6050 Pitch Only")
ax1.legend(loc="upper right")

ax2.set_xlim(-1, 1)
ax2.set_ylim(-90, 90)
ax2.set_aspect('equal')
ax2.set_title("2D Pitch Visualization")

bar_width = 0.4
bar = ax2.bar([0], [0], width=bar_width, color='green')[0]

def parse_line(line):
    """Parse a serial line for pitch only."""
    try:
        parts = line.strip().split(',')
        if len(parts) < 1:
            return None
        pitch = float(parts[0])
        return pitch
    except:
        return None

def init():
    line_pitch.set_data([], [])
    bar.set_height(0)
    return (line_pitch, bar)

def update(frame):
    for _ in range(5):
        raw = ser.readline().decode(errors='ignore')
        if not raw:
            break
        pitch = parse_line(raw)
        if pitch is None:
            continue
        pitch_buf.append(pitch)
        x_idx.append(len(x_idx)+1 if x_idx else 1)

    xs = list(range(len(x_idx)))
    line_pitch.set_data(xs, list(pitch_buf))
    ax1.set_xlim(max(0, len(xs)-WINDOW), max(WINDOW, len(xs)))

    if pitch_buf:
        bar.set_height(pitch_buf[-1])
        ax2.set_ylim(-180, 180)

    return (line_pitch, bar)

ani = animation.FuncAnimation(fig, update, init_func=init, interval=30, blit=False)
plt.tight_layout()
plt.show()
