import sys
import math
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
roll_buf  = deque(maxlen=WINDOW)
yaw_buf   = deque(maxlen=WINDOW)
x_idx     = deque(maxlen=WINDOW)

fig, (ax1, ax2) = plt.subplots(2,1, figsize=(10,6))

(line_pitch,) = ax1.plot([], [], label="Pitch (°)")
(line_roll,)  = ax1.plot([], [], label="Roll (°)")
(line_yaw,)   = ax1.plot([], [], label="Yaw (°)")
ax1.set_xlim(0, WINDOW)
ax1.set_ylim(-180, 180)
ax1.set_xlabel("Samples")
ax1.set_ylabel("Angle (°)")
ax1.set_title("MPU6050 Pitch, Roll, Yaw")
ax1.legend(loc="upper right")

ax2.set_xlim(-2, 2)
ax2.set_ylim(-2, 2)
ax2.set_aspect('equal')
ax2.set_title("2D Orientation")

body = np.array([[0, 0.3], [0.6, 0], [0, -0.3], [-0.6, 0]])  # X, Y points

def rotate2d(points, angle_deg):
    """Rotate 2D points by angle (degrees)."""
    theta = np.radians(angle_deg)
    R = np.array([[np.cos(theta), -np.sin(theta)],
                  [np.sin(theta),  np.cos(theta)]])
    return points @ R.T

def draw_helicopter_2d(ax, yaw):
    rotated_body = rotate2d(body, yaw)
    ax.cla()
    ax.set_xlim(-2, 2)
    ax.set_ylim(-2, 2)
    ax.set_aspect('equal')
    ax.set_title("2D Helicopter Orientation")
    ax.fill(rotated_body[:,0], rotated_body[:,1], color='blue', alpha=0.7)
    rotor_len = 0.8
    ax.plot([-rotor_len, rotor_len], [0, 0], color='red', linewidth=2)
    ax.plot([0, 0], [-rotor_len, rotor_len], color='red', linewidth=2)

def parse_line(line):
    try:
        parts = line.strip().split(',')
        if len(parts) != 3:
            return None, None, None
        pitch = float(parts[0])
        roll  = float(parts[1])
        yaw   = float(parts[2])
        return pitch, roll, yaw
    except:
        return None, None, None

def init():
    line_pitch.set_data([], [])
    line_roll.set_data([], [])
    line_yaw.set_data([], [])
    return (line_pitch, line_roll, line_yaw)

def update(frame):
    for _ in range(5):
        raw = ser.readline().decode(errors='ignore')
        if not raw:
            break
        pitch, roll, yaw = parse_line(raw)
        if pitch is None:
            continue
        pitch_buf.append(pitch)
        roll_buf.append(roll)
        yaw_buf.append(yaw)
        x_idx.append(len(x_idx)+1 if x_idx else 1)

    xs = list(range(len(x_idx)))
    line_pitch.set_data(xs, list(pitch_buf))
    line_roll.set_data(xs, list(roll_buf))
    line_yaw.set_data(xs, list(yaw_buf))
    ax1.set_xlim(max(0, len(xs)-WINDOW), max(WINDOW, len(xs)))

    if yaw_buf:
        draw_helicopter_2d(ax2, yaw_buf[-1])

    return (line_pitch, line_roll, line_yaw)

ani = animation.FuncAnimation(fig, update, init_func=init, interval=30, blit=False)
plt.tight_layout()
plt.show()
