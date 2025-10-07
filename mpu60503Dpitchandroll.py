import sys
import math
import serial
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque
import numpy as np
from mpl_toolkits.mplot3d import Axes3D

PORT = 'COM3'  
BAUD = 115200
WINDOW = 200

ser = serial.Serial(PORT, BAUD, timeout=1)

pitch_buf = deque(maxlen=WINDOW)
roll_buf  = deque(maxlen=WINDOW)
x_idx     = deque(maxlen=WINDOW)

fig = plt.figure(figsize=(10,6))

ax1 = fig.add_subplot(2,1,1)
(line_pitch,) = ax1.plot([], [], label="Pitch (°)", color='blue')
(line_roll,)  = ax1.plot([], [], label="Roll (°)", color='green')
ax1.set_xlim(0, WINDOW)
ax1.set_ylim(-180, 180)
ax1.set_xlabel("Samples")
ax1.set_ylabel("Angle (°)")
ax1.set_title("MPU6050 Pitch & Roll")
ax1.legend(loc="upper right")

ax2 = fig.add_subplot(2,1,2, projection='3d')
ax2.set_xlim([-2,2])
ax2.set_ylim([-2,2])
ax2.set_zlim([-2,2])
ax2.set_box_aspect([1,1,1])
ax2.set_title("3D Pitch & Roll Orientation")

theta = np.linspace(0, 2*np.pi, 30)
z = np.linspace(-1.5, 1.5, 30)   
theta, z = np.meshgrid(theta, z)
x = 0.05*np.cos(theta)
y = 0.05*np.sin(theta)
pencil_points = np.stack([x.flatten(), y.flatten(), z.flatten()], axis=1)

def rotation_matrix(pitch, roll):
    """Return rotation matrix for pitch and roll (degrees), ignoring yaw."""
    pitch = np.radians(pitch)
    roll  = np.radians(roll)

    Rx = np.array([
        [1, 0, 0],
        [0, math.cos(pitch), -math.sin(pitch)],
        [0, math.sin(pitch),  math.cos(pitch)]
    ])
    Ry = np.array([
        [ math.cos(roll), 0, math.sin(roll)],
        [0, 1, 0],
        [-math.sin(roll), 0, math.cos(roll)]
    ])
    return Ry @ Rx  

def draw_pencil(ax, pitch, roll):
    """Draw pencil with given pitch and roll."""
    R = rotation_matrix(pitch, roll)
    rotated = pencil_points @ R.T

    xp = rotated[:,0].reshape(x.shape)
    yp = rotated[:,1].reshape(y.shape)
    zp = rotated[:,2].reshape(z.shape)

    ax.cla()
    ax.set_xlim([-2,2])
    ax.set_ylim([-2,2])
    ax.set_zlim([-2,2])
    ax.set_box_aspect([1,1,1])
    ax.set_title("3D Pitch & Roll Orientation")

    ax.plot_surface(xp, yp, zp, color='orange', alpha=0.9, edgecolor='k')

    ax.quiver(0,0,0, 1,0,0, color='red')
    ax.quiver(0,0,0, 0,1,0, color='green')
    ax.quiver(0,0,0, 0,0,1, color='blue')

def parse_line(line):
    try:
        parts = line.strip().split(',')
        if len(parts) < 2:
            return None, None
        pitch = float(parts[0])
        roll  = float(parts[1])
        return pitch, roll
    except:
        return None, None

def init():
    line_pitch.set_data([], [])
    line_roll.set_data([], [])
    return (line_pitch, line_roll)

def update(frame):
    for _ in range(5):
        raw = ser.readline().decode(errors='ignore')
        if not raw:
            break
        pitch, roll = parse_line(raw)
        if pitch is None:
            continue
        pitch_buf.append(pitch)
        roll_buf.append(roll)
        x_idx.append(len(x_idx)+1 if x_idx else 1)

    xs = list(range(len(x_idx)))
    line_pitch.set_data(xs, list(pitch_buf))
    line_roll.set_data(xs, list(roll_buf))
    ax1.set_xlim(max(0, len(xs)-WINDOW), max(WINDOW, len(xs)))

    if pitch_buf and roll_buf:
        draw_pencil(ax2, pitch_buf[-1], roll_buf[-1])

    return (line_pitch, line_roll)

ani = animation.FuncAnimation(fig, update, init_func=init, interval=30, blit=False)
plt.tight_layout()
plt.show()
