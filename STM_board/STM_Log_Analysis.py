# -*- coding: utf-8 -*-
"""
Created on Tue Dec  2 15:48:48 2025

@author: kkeramati
"""

import pandas as pd
import matplotlib.pyplot as plt
import re
import numpy as np
import mplcursors

def trim_from_ramp_start(df, col,
                         flat_samples=300,      # how many initial samples to learn "flat" behavior
                         jump_factor=5.0,       # how much bigger than flat jumps counts as "real start"
                         min_jump=1.0,          # absolute minimum jump size to consider
                         baseline_tol=0.05):    # value must rise above baseline by this amount
    """
    Find the first point where a signal transitions from "flat-ish" to "increasing",
    then return (row_position, time_value, trimmed_df).

    Assumes df.index is time.
    """
    # Fill gaps so we can detect changes even if samples alternate with NaNs
    s = df[col].ffill().bfill()
    vals = s.to_numpy()
    t = df.index.to_numpy()

    n = len(vals)
    if n < 3:
        raise ValueError("Not enough samples to detect a ramp start.")

    fs = min(flat_samples, n - 2)

    # Baseline = typical value in the initial flat region
    baseline = float(np.median(vals[:fs]))

    # Learn what "normal" step changes look like in the flat region
    flat_absdiff = np.abs(np.diff(vals[:fs]))
    noise_jump = float(np.nanpercentile(flat_absdiff, 99)) if fs > 10 else float(np.nanpercentile(np.abs(np.diff(vals)), 99))

    # Threshold for a "real" jump that indicates ramp start
    jump_thr = max(min_jump, jump_factor * noise_jump)

    d = np.diff(vals)

    ramp_pos = None
    for i in range(1, n):
        # jump bigger than threshold AND value is above baseline
        if abs(d[i - 1]) > jump_thr and vals[i] > baseline + baseline_tol:
            ramp_pos = i
            break

    if ramp_pos is None:
        # Fallback: if no big jump exists, use first sustained deviation above baseline
        run = 10
        above = vals > baseline + baseline_tol
        count = 0
        for i in range(n):
            if above[i]:
                count += 1
                if count >= run:
                    ramp_pos = i - run + 1
                    break
            else:
                count = 0

    if ramp_pos is None:
        raise ValueError(f"Ramp start not found for column '{col}'. Try adjusting thresholds.")

    ramp_time = t[ramp_pos]
    df_trim = df.loc[ramp_time:].copy()

    return ramp_pos, ramp_time, df_trim


def shift_to_zero(df, *, time_col=None, set_as_index=False, drop=False):
    """
    Shift time so it starts at zero.

    Parameters
    ----------
    df : pandas.DataFrame
        Input DataFrame
    time_col : str or None, optional
        Column name to shift. If None, shift the index.
    set_as_index : bool, default False
        If True and time_col is given, set shifted column as index.
    drop : bool, default False
        If True and time_col is given, drop the original column.

    Returns
    -------
    df_out : pandas.DataFrame
        Time-shifted DataFrame
    """
    df_out = df.copy()

    # --- Case 1: shift index ---
    if time_col is None:
        t0 = df_out.index[0]
        df_out.index = df_out.index - t0
        return df_out

    # --- Case 2: shift column ---
    if time_col not in df_out.columns:
        raise KeyError(f"Column '{time_col}' not found in DataFrame.")

    t0 = df_out[time_col].iloc[0]
    shifted = df_out[time_col] - t0

    if set_as_index:
        df_out.index = shifted
        df_out.index.name = time_col
        if drop:
            df_out = df_out.drop(columns=[time_col])
    else:
        df_out[time_col] = shifted

    return df_out


# ----------------------------------------------------
# 1) Read file and extract only numeric comma-separated rows
# ----------------------------------------------------
path = './result/flight.csv'

plt.rcParams["font.family"] = "Century Gothic"

colors = ['#ff596c','#525252ff', '#009494ff', '#0F3878',  '#f7941dff','#009494ff','#ff596c']*2

lines = []
with open(path, 'r') as f:
    lines = f.readlines()

# -------------------------------------------------------
# 1) Find the header row inside the text
# -------------------------------------------------------
header = None
header_index = None

for i, line in enumerate(lines):
    if "timestamp" in line and "," in line:
        header = [h.strip() for h in line.strip().split(',')]
        header_index = i
        break

print("Detected header:", header)

# -------------------------------------------------------
# 2) Load ONLY numeric rows after the header
# -------------------------------------------------------
numeric_rows = []
for line in lines[header_index + 1:]:
    if re.match(r'\s*\d', line) and ',' in line:
        parts = [float(x) for x in line.strip().split(',')]
        numeric_rows.append(parts)

# Create DataFrame with detected column names
df = pd.DataFrame(numeric_rows, columns=header)

print(df.head())

# -------------------------------------------------------
# 3) Plot each parameter vs timestamp
# -------------------------------------------------------
df["Time (s)"]=df["timestamp"]/1000
df["Speed (rpm)"] = df["speed"]*30/np.pi
df["Current (A)"] = df["current"]*1.63
df["Power (W)"] = df["current"]*df["voltage"]
df=df.rename(columns={"voltage":"Voltage (V)",
                      "setpoint":"Throttle (%)",
                      "temperature":"Temperature (°C)"})
time = df["Time (s)"]
cols = df.columns
fig, axes = plt.subplots(2, 3, figsize=(8, 6))
ax = list(axes.flat)

cols = ["Current (A)","Voltage (V)","Power (W)","Speed (rpm)","Throttle (%)","Temperature (°C)"]
for i,col in enumerate(cols):
    if col == "timestamp":
        continue
    # plt.figure(figsize=(10,5))
    ax[i].plot(time, df[col],'-', color = colors[i])
    ax[i].scatter(time, df[col], color = colors[i],s=2)

    ax[i].set_xlabel("Time (s)")
    ax[i].set_ylabel(col)
    ax[i].set_title(f"{col} vs Time")
    ax[i].grid(which = 'both')

artists = []
for a in ax:
    artists.extend(a.collections)  # scatter lives here

cursor = mplcursors.cursor(artists, hover=False)

@cursor.connect("add")
def on_add(sel):
    line = sel.artist
    xval, yval = sel.target

    axis_index = ax.index(line.axes)  # <-- simpler now that ax is a list

    sel.annotation.set_text(
        f"x={xval:.4f}\n"
        f"y={yval:.4f}"
    )

plt.show()

print (f'S_max: {df["Speed (rpm)"].max():.1f}rpm')

ramp_pos, ramp_time, df_trim = trim_from_ramp_start(df, 
                                     col = 'current',
                                     flat_samples=300,      
                                     jump_factor=5.0,      
                                     min_jump=1.0,          
                                     baseline_tol=0.05)
df_trim_shift = shift_to_zero(df_trim,
                              time_col = 'Time (s)')

fig, axes = plt.subplots(2, 3, figsize=(8, 6))
ax = list(axes.flat)

time1 = df_trim_shift['Time (s)']
for i,col1 in enumerate(cols):
    if col1 == "timestamp":
        continue
    # plt.figure(figsize=(10,5))
    ax[i].plot(time1, df_trim_shift[col1],'-', color = colors[i])
    ax[i].scatter(time1, df_trim_shift[col1], color = colors[i],s=2)
    ax[i].axvline(x=133, color = 'red',ls = '--',  label = 'T = 133 s')

    ax[i].set_xlabel("Time (s)")
    ax[i].set_ylabel(col1)
    ax[i].set_title(f"{col1} vs Time")
    ax[i].grid(which = 'both')