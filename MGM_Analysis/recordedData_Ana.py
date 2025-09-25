# -*- coding: utf-8 -*-
"""
Created on Mon Jul 21 11:56:22 2025

@author: kkeramati
"""
import pandas as pd
from matplotlib import pyplot as plt
import math


date = '2025-08-01'
# hour = '12-32-20'
hour = '10-40-04'

Control = 'HBC02'
Motor = 'Motor02'

df = pd.read_csv(f'./{Motor}{Control}/MGM ProTool monitoring {date} {hour}.csv',encoding='ISO-8859-1', delimiter=';')
df['Time'] = pd.to_datetime(df['Time'], format='%H:%M:%S.%f', errors='coerce')
df = df.dropna(subset=['Time'])
start_time = df['Time'].iloc[0]
df['Time_seconds'] = (df['Time'] - start_time).dt.total_seconds()
# Get all numeric columns (skip 'Time')
data_cols = [col for col in df.columns if col not in ['Time', 'Time_seconds']]

# Convert all data columns to numeric (non-numeric will be NaN)
for col in data_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce')
colors = ['#f74242ff','#009494ff','#00d0b8','#0AFFA0','#0F3878','#0f75bcff','#0FAAF0','#29e2ecff','#9e0012ff','#ff596c','#95755A','#f7941dff','#ffad5aff','#525252ff','#848484ff']

df['rpm'] = df['Motor revolutions [x100rpm]']*100
data_cols1 = ['Input voltage [V]','Input current [A]','BEC voltage [V]', 'rpm','Incoming power [W]','Output power [%]']
# --- Plotting ---
num_plots = len(data_cols1)
cols = 2  # number of columns in subplot grid
rows = math.ceil(num_plots / cols)

fig, axes = plt.subplots(rows, cols, figsize=(10, rows * 3))
fig.suptitle(hour)
axes = axes.flatten()  # Flatten in case of single row
for i, col in enumerate(data_cols1):
    axes[i].plot(df['Time_seconds'], df[col],color = colors[i],linewidth = 2)
    axes[i].set_title(col, fontsize=10)
    axes[i].set_xlabel("Time [s]")

    axes[i].grid(True)
    # axes[i].set_xlabel([0,10])

# Hide any unused subplots
for j in range(i + 1, len(axes)):
    fig.delaxes(axes[j])

fig.tight_layout()
plt.show()