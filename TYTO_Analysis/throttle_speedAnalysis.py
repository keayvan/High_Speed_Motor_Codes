# -*- coding: utf-8 -*-
"""
Created on Fri Sep 26 11:59:37 2025

@author: kkeramati
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

palette = {
"teal_dark": "#009494ff",
"teal_light": "#00d0b8",
"lime_green": "#0AFFA0",
"navy_dark": "#0F3878",
"blue_medium": "#0f75bcff",
"sky_blue": "#0FAAF0",
"cyan_bright": "#29e2ecff",
"crimson_dark": "#9e0012ff",
"red_bright": "#f74242ff",
"coral_pink": "#ff596c",
"taupe": "#95755A",
"orange_bright": "#f7941dff",
"peach_orange": "#ffad5aff",
"gray_dark": "#525252ff",
"gray_medium": "#848484ff"
}

colors = list(palette.values())
# === Load data ===
file_path = "./Results_TYTO/withPropeller_MGM1200rpmContinious.csv"


df = pd.read_csv(file_path).iloc[:364,:]

# === Trim first 2 rows and last row ===
# df = df.iloc[2:-1].reset_index(drop=True)

# === Remove throttle = 1000 ===
df = df[df["Powertrain 1 - ESC throttle (μs)"] != 1000].reset_index(drop=True)

# Extract relevant columns
time = df["Time (s)"]
throttle = df["Powertrain 1 - ESC throttle (μs)"]
speed = df["Powertrain 1 - rotation speed (rpm)"]
torque = df["Powertrain 1 - torque MZ (torque) (N⋅m)"]
current = df['Powertrain 1 - current (A)']
# === Detect throttle steps ===
step_changes = np.where(throttle.diff() != 0)[0]
step_changes = np.append(step_changes, len(df))  # add last index to close final interval

plt.rcParams["font.family"] = "Century Gothic"

plt.figure(figsize=(10,6))
plt.plot(time, speed,'--o',ms=6, lw = 1, c= palette["teal_light"],mfc = palette["crimson_dark"] )
plt.xlabel('Time(s)')
plt.ylabel('Speed (rpm)')
plt.gca().xaxis.set_major_locator(mticker.MaxNLocator(12))
plt.grid()

plt.figure(figsize=(10,6))
plt.plot(time, torque,'--o',ms=6, lw = 1, c= palette["blue_medium"],mfc = palette["crimson_dark"] )
plt.xlabel('Time(s)')
plt.ylabel('Torque (N.m)')
plt.gca().xaxis.set_major_locator(mticker.MaxNLocator(12))

plt.grid()
# === Compute averages per step ===
avg_throttle = []
avg_speed = []
avg_torque = []
avg_current = []
mean_min = 20
mean_max = 10
for idx in step_changes:
    avg_throttle.append(throttle.iloc[idx-mean_min:idx-mean_max].mean())
    avg_speed.append(speed.iloc[idx-mean_min:idx-mean_max].mean())
    avg_torque.append(torque.iloc[idx-mean_min:idx-mean_max].mean())
    avg_current.append(current.iloc[idx-mean_min:idx-mean_max].mean())
    
    start_idx = idx

avg_throttle = np.array(avg_throttle)
avg_speed = np.array(avg_speed)
avg_torque = np.array(avg_torque)
avg_current = np.array(avg_current)
# === Remove first and last entries (unstable) ===
avg_throttle = avg_throttle[1:]
avg_speed = avg_speed[1:]
avg_torque = avg_torque[1:]
avg_current = avg_current[1:]

coeffs = np.polyfit(avg_throttle, avg_speed, 2)   # quadratic fit
poly_fit = np.poly1d(coeffs)

a, b, c = coeffs
print(poly_fit)


# Generate smooth curve for plotting
throttle_fit = np.linspace(min(avg_throttle), max(avg_throttle), 200)
speed_fit = poly_fit(throttle_fit)



# === Plot 2: Torque vs Speed ===
plt.figure(figsize=(10,6))
plt.plot(speed, torque, '.', alpha=0.3, label="Raw data")
plt.plot(avg_speed, avg_torque, 'o-',color=palette["teal_dark"],mfc='#0AFFA0',mec='#0FAAF0',lw=2,ms=6, label="Step averages")
plt.xlabel("Speed (rpm)")
plt.ylabel("Torque (N⋅m)")
for x, y in zip(avg_speed,avg_torque):
            plt.text(x, y, f"({x:.0f},{y:.2f})", fontsize=8, ha="center", va="bottom")
plt.legend()
plt.grid(True)
plt.show()
plt.gca().xaxis.set_major_locator(mticker.MaxNLocator(12))

# === Plot 1: Speed vs Throttle with quadratic fit ===



plt.figure(figsize=(10,6))
plt.plot(throttle, speed, '.', alpha=0.3, label="Raw data")
plt.plot(avg_throttle, avg_speed, 'o', color='red', label="Step averages")
plt.plot(throttle_fit, speed_fit, '-', color='#0FAAF0', linewidth=2, label="fitted curve")
plt.xlabel("Throttle (μs)")
plt.ylabel("Speed (rpm)")
plt.legend()
plt.grid(True)
plt.show()
plt.gca().xaxis.set_major_locator(mticker.MaxNLocator(12))

plt.figure(figsize=(10,6))
plt.plot(throttle, current , '.', alpha=0.3, label="Raw data")
plt.plot(avg_throttle, avg_current, 'o-',color=palette["teal_dark"],mfc='#0AFFA0',mec='#0FAAF0',lw=2,ms=6, label="Step averages")
plt.xlabel("Throttle (μs)")
plt.ylabel("Current (A)")
for x, y in zip(avg_speed,avg_torque):
            plt.text(x, y, f"({x:.0f},{y:.2f})", fontsize=8, ha="center", va="bottom")
plt.legend()
plt.grid(True)
plt.show()
plt.gca().xaxis.set_major_locator(mticker.MaxNLocator(12))


plt.figure(figsize=(10,6))
plt.plot(throttle, torque , '.', alpha=0.3, label="Raw data")
plt.plot(avg_throttle, avg_torque, 'o-',color=palette["teal_dark"],mfc='#0AFFA0',mec='#0FAAF0',lw=2,ms=6, label="Step averages")
plt.xlabel("Throttle (μs)")
plt.ylabel("Torque (N⋅m)")
for x, y in zip(avg_speed,avg_torque):
            plt.text(x, y, f"({x:.0f},{y:.2f})", fontsize=8, ha="center", va="bottom")
plt.legend()
plt.grid(True)
plt.show()
plt.gca().xaxis.set_major_locator(mticker.MaxNLocator(12))
