import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import argrelextrema

def read_csv_file(filename):
    df = pd.read_csv(filename)
    df['time'] = pd.to_numeric(df['time'])
    df['VELOCITY'] *= 60  # Convert velocity to RPM
    df['CURRENT'] = df['POWER'] / df['VOLTAGE']  # Compute Current
    df['Sampling_rate'] = df['time'].diff()  # Calculate time difference
    return df

def annotate_max(ax, df, param, label, color, offset_index, x_param='time'):
    max_idx = df[param].idxmax()
    max_x, max_value = df[x_param][max_idx], df[param][max_idx]
    y_offset = 0.08 * (max_value if max_value != 0 else 1) * (offset_index % 2 * 2 - 1)
    
    ax.annotate(f"{max_value:.2f} @ {max_x:.2f}",
                xy=(max_x, max_value),
                xytext=(max_x, max_value + y_offset),
                textcoords="data",
                fontsize=10,
                color=color,
                bbox=dict(facecolor='white', alpha=0.6, edgecolor=color, boxstyle="round,pad=0.3"),
                arrowprops=dict(arrowstyle="->", color=color))

# Load CSV Files
files = ['KPKIV38']  # Modify as needed
csv_files = [f"{file}.csv" if not file.endswith('.csv') else file for file in files]
dfs = [read_csv_file(file) for file in csv_files]

# Parameters
parameters_1 = ['VELOCITY', 'TORQUE', 'POWER', 'TEMPERATURE', 'VOLTAGE', 'CURRENT']
parameters_2 = ['POSITION', 'D_CURRENT', 'Q_CURRENT', 'Sampling_rate']
plot_params = ['CURRENT', 'TORQUE', 'POWER']
colors = ['#0F3878', '#f74242', '#00d0b8']

# Plot first set of parameters
fig, axes = plt.subplots(3, 2, figsize=(14, 10))
axes = axes.flatten()
fig.tight_layout(pad=4.0)

for ax, param in zip(axes, parameters_1):
    for i, (df, label, color) in enumerate(zip(dfs, files, colors)):
        ax.plot(df['time'], df[param], label=f'{param} ({label})', color=color)
        annotate_max(ax, df, param, label, color, i)
    ax.set_xlabel('Time')
    ax.set_ylabel(param)
    ax.set_title(f'{param} vs Time')
    ax.legend()
    ax.grid(True)

# Plot second set of parameters
fig2, axes2 = plt.subplots(2, 2, figsize=(14, 10))
axes2 = axes2.flatten()
fig2.tight_layout(pad=6.0)

for ax, param in zip(axes2, parameters_2):
    for i, (df, label, color) in enumerate(zip(dfs, files, colors)):
        ax.plot(df['time'], df[param], label=f'{param} ({label})', color=color)
        annotate_max(ax, df, param, label, color, i)
    ax.set_xlabel('Time')
    ax.set_ylabel(param)
    ax.set_title(f'{param} vs Time')
    ax.legend()
    ax.grid(True)

plt.show()

# Function to fit curve
def fit_curve(x, y, degree=2, extrapolate_x=None):
    if len(x) > degree:
        coeffs = np.polyfit(x, y, degree)
        poly_func = np.poly1d(coeffs)
        return poly_func(extrapolate_x) if extrapolate_x is not None else poly_func(x), coeffs
    return np.full_like(extrapolate_x if extrapolate_x is not None else x, np.mean(y))

# Function to compute bounds
def bound_func(sig, xAxis):
    sig, xAxis = sig.dropna().to_numpy(), xAxis.to_numpy()
    local_maxima_indices = argrelextrema(sig, np.greater, order=5)[0]
    local_minima_indices = argrelextrema(sig, np.less, order=3)[0]
    
    upper_bound = lower_bound = None
    if len(local_maxima_indices) > 2:
        upper_bound, _ = fit_curve(xAxis[local_maxima_indices], sig[local_maxima_indices], degree=3, extrapolate_x=xAxis)
    if len(local_minima_indices) > 2:
        lower_bound, _ = fit_curve(xAxis[local_minima_indices], sig[local_minima_indices], degree=3, extrapolate_x=xAxis)
    
    bound_range = np.max(sig) - np.min(sig)
    expansion_factor = 0.05 * bound_range
    return (lower_bound - expansion_factor, upper_bound + expansion_factor) if upper_bound is not None and lower_bound is not None else (None, None)

# Sorting Data
sorted_df = dfs[0].sort_values(by='time')
xAxis, power = sorted_df['VELOCITY'], sorted_df['POWER']
upper_bound_coef, lower_bound_coef = bound_func(power, xAxis)

# Evaluate bounds at specific velocity
x = 8000
p_max, p_min = np.poly1d(upper_bound_coef)(x), np.poly1d(lower_bound_coef)(x)
print(f"New_Controller@{x}rpm: p_min={np.round(p_min,1)}W, p_max={np.round(p_max,1)}W")

# Plot Current, Torque, Power vs Velocity
fig3, axes3 = plt.subplots(3, 1, figsize=(10, 15))
fig3.tight_layout(pad=8.0)
axes3 = axes3.flatten()
axes3[2].scatter([x, x], [p_min, p_max], s=50, color=colors[-1], edgecolor=colors[1])

for ax, param in zip(axes3, plot_params):
    for i, (df, label) in enumerate(zip(dfs, files)):
        ax.scatter(sorted_df['VELOCITY'], sorted_df[param], label=f'{param} ({label})', color=colors[i % len(colors)], s=10)
        annotate_max(ax, sorted_df, param, label, colors[i % len(colors)], i, x_param='VELOCITY')
        lower_bound, upper_bound = bound_func(sorted_df[param], sorted_df['VELOCITY'])
        ax.plot(sorted_df['VELOCITY'], upper_bound, label="Upper Bound", color='r')
        ax.plot(sorted_df['VELOCITY'], lower_bound, label="Lower Bound", color='r')
        ax.axvline(x, linestyle='--', label=f'@{x}rpm')
    ax.set_xlabel('Velocity (RPM)')
    ax.set_ylabel(param)
    ax.set_title(f'{param} vs Velocity')
    ax.legend()
    ax.grid(True)

plt.show()
