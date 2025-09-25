import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import argrelextrema
def read_csv_file(filename):
    df = pd.read_csv(filename)
    df['time'] = pd.to_numeric(df['time'])
    df['VELOCITY'] = df['VELOCITY'] * 60  # Convert velocity to RPM
    df['CURRENT'] = df['POWER'] / df['VOLTAGE']  # Compute Current
    df['Smapling_rate'] = 1/df['time'].diff()  # Calculate difference from the previous value
    return df

def annotate_max(ax, df, param, label, color, offset_index, x_param='time'):
    max_idx = df[param].idxmax()
    max_x = df[x_param][max_idx]
    max_value = df[param][max_idx]
    
    y_offset = 0.08 * (max_value if max_value != 0 else 1) * (offset_index % 2 * 2 - 1)  # Alternating offset
    ax.annotate(f"{max_value:.2f} @ {max_x:.2f}", 
                xy=(max_x, max_value), 
                xytext=(max_x, max_value + y_offset),
                textcoords="data",
                fontsize=10,
                color=color,
                bbox=dict(facecolor='white', alpha=0.6, edgecolor=color, boxstyle="round,pad=0.3"),
                arrowprops=dict(arrowstyle="->", color=color))

# List of CSV files to compare
files = ['/home/kkeramati/moteus/dataAnalysis/data/resultMoteus/KPKIV38']  # Modify as needed
csv_files = [f"{file}.csv" if not file.endswith('.csv') else file for file in files]
dfs = [read_csv_file(file) for file in csv_files]

# Parameters to plot
param1 = ["VELOCITY","POWER","CURRENT","VOLTAGE"]
param2 = ['TORQUE', 'TEMPERATURE','POSITION', 'D_CURRENT', 'Q_CURRENT','Smapling_rate']
plot_params = ['CURRENT', 'TORQUE', 'POWER']  # For Velocity-based plot
colors = {
    "gray": "#525252ff",
    "teal": "#009494ff",
    "turquoise": "#00d0b8",
    "sky_blue": "#0FAAF0",
    "red": "#f74242ff",
    "orange": "#f7941df",
    "navy_blue": "#0F3878",
    "dark_red": "#9e0012ff",
    "black": "black",
}
colors_list = list(colors.values())

fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.tight_layout(pad=4.0)
axes = axes.flatten()

# Plot first set of parameters
for ax, param in zip(axes, param1):
    for i, (df, label, color) in enumerate(zip(dfs, files, colors)):
        ax.plot(df['time'], df[param], label=f'{param} ({label})', color=color)
        annotate_max(ax, df, param, label, color, i)  # Annotate max values
    ax.set_xlabel('Time')
    ax.set_ylabel(param)
    ax.set_title(f'{param} vs Time')
    ax.legend()
    ax.grid(True)

# Second set of parameters
parm_2nd = True
if parm_2nd:
    fig2, axes2 = plt.subplots(2, 3, figsize=(14, 10))
    fig2.tight_layout(pad=6.0)
    axes2 = axes2.flatten()
    
    for ax, param in zip(axes2, param2):
        for i, (df, label, color) in enumerate(zip(dfs, files, colors)):
            ax.plot(df['time'], df[param], label=f'{param} ({label})', color=color)
            annotate_max(ax, df, param, label, color, i)
        ax.set_xlabel('Time')
        ax.set_ylabel(param)
        ax.set_title(f'{param} vs Time')
        ax.legend()
        ax.grid(True)
    
    plt.tight_layout()
    plt.show()
def fit_curve(x, y, degree=2, extrapolate_x=None):
    if len(x) > degree:
        coeffs = np.polyfit(x, y, degree)
        poly_func = np.poly1d(coeffs)
        if extrapolate_x is not None:
            return poly_func(extrapolate_x), coeffs
        return poly_func(x), coeffs
    return np.full_like(extrapolate_x if extrapolate_x is not None else x, np.mean(y))

def bound_func(sig, xAxis):
    sig = sig.dropna().to_numpy()
    xAxis = xAxis.to_numpy()
    
    local_maxima_indices = argrelextrema(sig, np.greater, order=5)[0]
    local_minima_indices = argrelextrema(sig, np.less, order=3)[0]

    if len(local_maxima_indices) > 2:
        local_maxima = sig[local_maxima_indices]
        max_time = xAxis[local_maxima_indices]
        upper_bound,_= fit_curve(max_time, local_maxima, degree=3, extrapolate_x=xAxis)
    # else:
    #     upper_bound = np.full_like(xAxis, np.max(sig))  # Fallback if not enough maxima found
    
    if len(local_minima_indices) > 2:
        local_minima = sig[local_minima_indices]
        min_time = xAxis[local_minima_indices]
        lower_bound, _ = fit_curve(min_time, local_minima, degree=3, extrapolate_x=xAxis)
    # else:
    #     lower_bound = np.full_like(xAxis, np.min(sig))  # Fallback if not enough minima found
    
    bound_range = np.max(sig) - np.min(sig)
    expansion_factor = 0.05 * bound_range  # Expand bounds slightly to visualize variation

    upper_bound_expanded = upper_bound + expansion_factor
    lower_bound_expanded = lower_bound - expansion_factor
    upper_bound_func, upper_bound_coef  = fit_curve(xAxis,upper_bound_expanded,degree= 3)
    lower_bound_func, lower_bound_coef  = fit_curve(xAxis,lower_bound_expanded, degree= 3)

    return lower_bound_expanded, upper_bound_expanded,upper_bound_coef, lower_bound_coef
def Order3_func(x,coef):
    res = coef[0]*x*x*x+coef[1]*x*x + coef[2]*x + coef[3]
    return res
sorted_df = df.sort_values(by='time')  # Ensure order is based on time

xAxis=sorted_df['VELOCITY']
power=sorted_df['POWER']

_,_, upper_bound_coef,lower_bound_coef = bound_func(sig=power, xAxis=xAxis)

x= 8000
p_max = Order3_func(x,upper_bound_coef)
p_min = Order3_func(x,lower_bound_coef)

print(f"New_Controller@{x}rpm:p_min={np.round(p_min,1)}W, p_max = {np.round(p_max,1)}W")
# New subplots: CURRENT, TORQUE, POWER vs VELOCITY (Ordered by Time)
fig3, axes3 = plt.subplots(3, 1, figsize=(10, 15))
fig3.tight_layout(pad=8.0)

axes3 = axes3.flatten()
axes3[2].scatter([x,x],[p_min,p_max],s = 50, color = 'orange',edgecolor = 'black')

for ax, param in zip(axes3, plot_params):
    for i, (df, label,color) in enumerate(zip(dfs, files,colors)):
        ax.scatter(sorted_df['VELOCITY'], sorted_df[param], label=f'{param} ({label})', color=color, s=10)  # Small dots instead of line
        annotate_max(ax, sorted_df, param, label, color, i, x_param='VELOCITY')  # Annotate max values
        sig=sorted_df[f'{param}']
        lower_bound_expanded, upper_bound_expanded,upper_bound_coef,lower_bound_coef = bound_func(sig=sig, xAxis=sorted_df['VELOCITY'])
        ax.plot(sorted_df['VELOCITY'], upper_bound_expanded, label="Upper Bound", color='r')
        ax.plot(sorted_df['VELOCITY'], lower_bound_expanded, label="Lower Bound", color='r')
        ax.axvline(x, linestyle = '--', label= f'@{x}rpm')


    ax.set_xlabel('Velocity (RPM)')
    ax.set_ylabel(param)
    ax.set_title(f'{param} vs Velocity')
    ax.legend()
    ax.grid(True)

plt.show()


def find_extrema(signal, order_factor=0.01):
    order = max(1, int(len(signal) * order_factor))
    local_max_indices = argrelextrema(signal, np.greater, order=order)[0]
    local_min_indices = argrelextrema(signal, np.less, order=order)[0]
    return local_min_indices, local_max_indices

def fit_curve(x, y, degree=2, extrapolate_x=None):
    if len(x) > degree:
        coeffs = np.polyfit(x, y, degree)
        poly_func = np.poly1d(coeffs)
        if extrapolate_x is not None:
            return poly_func(extrapolate_x), coeffs
        return poly_func(x), coeffs
    return np.full_like(extrapolate_x if extrapolate_x is not None else x, np.mean(y))
def Order3_func(x,coef):
    res = coef[0]*x*x*x+coef[1]*x*x + coef[2]*x + coef[3]
    return res

# Load the CSV file
file_path = "/home/kkeramati/moteus/dataAnalysis/data/ARC_Defence_data/Telem ESC 01_2025.csv"
df1 = pd.read_csv(file_path, skiprows=9)

# Rename columns based on row 7 (found earlier)
df1.columns = [
    "Unknown0","Time_sms","VOLTAGE", "CURRENT", "VELOCITY",
    "TEMPERATURE", "BEC voltage", "BEC current",
    "BEC temperature", "Input request","POWER",
    "Unknown1", "Unknown2", "Unknown3", "Unknown4",
    "Unknown5", "Unknown6", "Unknown7", "Unknown8",
    "Unknown9", "Unknown10", "Unknown11", "Unknown12",
    "Unknown13", "Pulse current"
]

# Convert numeric columns to proper data types
df1 = df1.apply(pd.to_numeric, errors='coerce')


# Multiply "Motor revolutions" column by 100
df1.loc[:, "VELOCITY"] *= 100
df1["time (s)"] = list(range(df.shape[0]))

# Plot data
fig0= True
if fig0:
    fig0, axes0 = plt.subplots(2, 2, figsize=(14, 10))
    fig0.tight_layout(pad=4.0)
    axes0 = axes0.flatten()
    fig0.suptitle('Raw Data VS "time (s)"',fontsize = 20)
    for i,(ax0, param) in enumerate(zip(axes0, param1)):
        ax0.scatter(df1['"time (s)"'], df1[param], label=f'{param}',s =6, color=colors[i] )
        ax0.set_xlabel('"time (s)"')
        ax0.set_ylabel(param)
        ax0.set_ylim(df1[param].min()-df1[param].max()*0.3,df1[param].max()*1.3)
        ax0.set_title(f'{param} vs "time (s)"')
        ax0.legend()
        ax0.grid(True)

def bound_func(sig, xAxis):
    sig = sig.dropna().to_numpy()
    xAxis = xAxis.to_numpy()
    
    local_maxima_indices = argrelextrema(sig, np.greater, order=5)[0]
    local_minima_indices = argrelextrema(sig, np.less, order=3)[0]

    if len(local_maxima_indices) > 2:
        local_maxima = sig[local_maxima_indices]
        max_time = xAxis[local_maxima_indices]
        upper_bound,_= fit_curve(max_time, local_maxima, degree=3, extrapolate_x=xAxis)
    # else:
    #     upper_bound = np.full_like(xAxis, np.max(sig))  # Fallback if not enough maxima found
    
    if len(local_minima_indices) > 2:
        local_minima = sig[local_minima_indices]
        min_time = xAxis[local_minima_indices]
        lower_bound, _ = fit_curve(min_time, local_minima, degree=3, extrapolate_x=xAxis)
    # else:
    #     lower_bound = np.full_like(xAxis, np.min(sig))  # Fallback if not enough minima found
    
    bound_range = np.max(sig) - np.min(sig)
    expansion_factor = 0.01 * bound_range  # Expand bounds slightly to visualize variation

    upper_bound_expanded = upper_bound + expansion_factor
    lower_bound_expanded = lower_bound - expansion_factor
    upper_bound_func, upper_bound_coef  = fit_curve(xAxis,upper_bound_expanded,degree= 3)
    lower_bound_func, lower_bound_coef  = fit_curve(xAxis,lower_bound_expanded, degree= 3)

    return lower_bound_expanded, upper_bound_expanded,upper_bound_coef, lower_bound_coef



df1_sorted = df1.sort_values(by="VELOCITY", ascending=True)
fig1= False
if fig1: 
    fig1, axes1 = plt.subplots(2, 2, figsize=(14, 10))
    fig1.tight_layout(pad=4.0)
    axes1 = axes1.flatten()
    fig1.suptitle('Sorted Data VS VELOCITY',fontsize = 20)
    for i,(ax1, param) in enumerate(zip(axes1, param1)):
        ax1.scatter(df1_sorted['VELOCITY'], df1_sorted[param], label=f'{param}',s =6, color=colors[i] )
        ax1.set_xlabel('VELOCITY')
        ax1.set_ylabel(param)
        ax1.set_ylim(df1_sorted[param].min()-df1_sorted[param].max()*0.3,df1_sorted[param].max()*1.3)
        ax1.set_title(f'{param} vs VELOCITY')
        ax1.legend()
        ax1.grid(True)



xAxis=df1_sorted['VELOCITY']
power=df1_sorted['POWER']

_,_, upper_bound_coef,lower_bound_coef = bound_func(sig=power, xAxis=xAxis)

x= 8000
p_max_mts = Order3_func(x,upper_bound_coef)
p_min_mts = Order3_func(x,lower_bound_coef)

print(f"ARC_Defemce@{x}rpm:p_min={np.round(p_min_mts,1)}W, p_max = {np.round(p_max_mts,1)}W")
fig2, axes2 = plt.subplots(1, 2, figsize=(20, 10))
fig2.tight_layout(pad=4.0)
axes2 = axes2.flatten()
fig2.suptitle('Bounds',fontsize = 20)
axes2[1].scatter([x,x],[p_min_mts,p_max_mts],s = 50, color = colors['red'],edgecolor = colors["teal"])
# ax2.scatter(x,485, s=50, color = colors[-2], label = 'Moteus')
for i,(ax2, param) in enumerate(zip(axes2, ['CURRENT','POWER'])):
    sig=df1_sorted[f'{param}']
    lower_bound_expanded, upper_bound_expanded,upper_bound_coef,lower_bound_coef = bound_func(sig=sig, xAxis=xAxis)

    ax2.scatter(xAxis, sig, label=f'{param}',s =6, color=colors['turquoise'] )
    ax2.plot(xAxis, upper_bound_expanded, label="Upper Bound", color=colors['sky_blue'])
    ax2.plot(xAxis, lower_bound_expanded, label="Lower Bound", color=colors['turquoise'])

    ax2.axvline(x, linestyle = '--', label= f'@{x}rpm')
    ax2.set_xlabel('VELOCITY')
    ax2.set_ylabel(param)
    ax2.set_ylim(sig.min()-sig.max()*0.5/1.3,sig.max()*1.3)
    ax2.set_title(f'{param} vs VELOCITY')
    ax2.legend()
    ax2.grid()
    
fig4, axes4 = plt.subplots(1, 2, figsize=(20, 10))
fig4.tight_layout(pad=4.0)
axes4 = axes4.flatten()
# axes4[1].scatter([x,x],[p_min_mts,p_max_mts],s = 50, color = colors[-1],edgecolor = colors[4])
# axes4[1].scatter([x,x],[p_min,p_max],s = 50, color = colors[-1],edgecolor = colors[1])

for i,(ax4, param) in enumerate(zip(axes4, ['CURRENT','POWER'])):
    sig1=df1_sorted[f'{param}']
    lower_bound_expanded1, upper_bound_expanded1,_,_ = bound_func(sig=sig1, xAxis=xAxis)

    sig2 = sorted_df[param]
    ax4.scatter(df1_sorted['VELOCITY'], sig1, label=f'{param}_ARC_Defence',s =6, color=colors['turquoise'] )
    ax4.scatter(sorted_df['VELOCITY'],sig2 , label=f'{param}_newController',s=10, color=colors['gray'])  # Small dots instead of line
    ax4.plot(df1_sorted['VELOCITY'], upper_bound_expanded1, label="Upper Bound_ARC_Defence", color=colors['red'])
    ax4.plot(df1_sorted['VELOCITY'], lower_bound_expanded1, label="Lower Bound_ARC_Defence", color=colors['red'])
    lower_bound_expanded, upper_bound_expanded,upper_bound_coef,lower_bound_coef = bound_func(sig=sig2, xAxis=sorted_df['VELOCITY'])
    ax4.plot(sorted_df['VELOCITY'], upper_bound_expanded, label="Upper Bound_newController", color='b')
    ax4.plot(sorted_df['VELOCITY'], lower_bound_expanded, label="Lower Bound_newController", color='b')
    ax4.axvline(x, linestyle = '--', label= f'@{x}rpm')
    ax4.set_xlabel('VELOCITY')
    ax4.set_ylabel(param)
    ax4.set_title(f'{param} vs VELOCITY')
    ax4.grid()
    ax4.legend()

    

# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# """
# Created on Wed Feb 12 17:40:57 2025

# @author: kkeramati
# """

# import pandas as pd
# import matplotlib.pyplot as plt
# import time

# # Function to read and plot the CSV data
# def plot_updating_csv(csv_file, update_interval=1):
#     plt.ion()  # Turn on interactive mode
#     fig, axs = plt.subplots(5, 2, figsize=(14, 10))
#     fig.tight_layout(pad=4.0)

#     # List of parameters to plot (excluding 'time' and 'FAULT')
#     parameters = ['POSITION', 'VELOCITY', 'TORQUE', 'Q_CURRENT', 'D_CURRENT', 'POWER', 'VOLTAGE', 'TEMPERATURE', 'Current']
#     colors = ['#009494ff', '#00d0b8', '#0FAAF0', '#f74242ff', '#525252ff', '#f7941dff', '#0F3878', '#9e0012ff', 'black', 'red']

#     while True:
#         try:
#             # Read the CSV file
#             df = pd.read_csv(csv_file)

#             # Convert the 'time' column to numeric (if it's not already)
#             df['time'] = pd.to_numeric(df['time'])
#             df['VELOCITY'] = df['VELOCITY'] * 60
#             df['Current'] = df['POWER'] / df['VOLTAGE']

#             # Clear the previous plots
#             for ax in axs.flat:
#                 ax.clear()

#             # Plot each parameter
#             for i, param in enumerate(parameters):
#                 ax = axs[i // 2, i % 2]
#                 ax.plot(df['time'], df[param], label=param, color=colors[i])
#                 ax.set_xlabel('Time')
#                 ax.set_ylabel(param)
#                 ax.set_title(f'{param} vs Time')
#                 ax.legend()
#                 ax.grid(True)

#             plt.draw()
#             plt.pause(update_interval)  # Pause to update the plot

#         except Exception as e:
#             print(f"Error: {e}")
#             break

# # Path to your CSV file
# csv_file = 'output.csv'

# # Call the function to start plotting
# plot_updating_csv(csv_file, update_interval=1)