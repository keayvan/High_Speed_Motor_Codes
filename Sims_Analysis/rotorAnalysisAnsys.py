# -*- coding: utf-8 -*-
"""
Created on Sun Oct 19 17:10:29 2025

@author: kkeramati
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager

# The user provided a file snippet indicating the actual header of short names (Name, P1, P2, etc.)
# is on the 7th line (index 6 in a zero-based system).
# file_path = "shaftWidthStudy1.csv"
file_path="Temperature_study_interferences.csv"

# Load the CSV file using header=6
# df = pd.read_csv(file_path, header=6).iloc[1:,:]
df = pd.read_csv(file_path, header=6)



col_map = {
    'P1': 'Shaft Contact Width [mm]',
    'P8': 'Pressure min Shaft Contact [MPa]',
    'P9': 'Pressure max Shaft Contact [MPa]',
    'P10': 'Pressure Average Shaft Contact [MPa]',

}

# col_map = {
#     'P1': 'Contact Width [mm]',
#     'P2': 'Pressure min Contact [MPa]',
#     'P3': 'Pressure max Contact [MPa]',
#     'P4': 'Pressure Average Contact [MPa]',

# }
# The short names of the columns to be used
# x_col_short = 'P1'
# y_cols_short = ['P5', 'P11']

x_col_short = 'P1'
y_cols_short = ['P8', 'P9', 'P10']

# x_col_short = 'P1'
# y_cols_short = ['P2', 'P3', 'P4']

# Convert the selected columns to numeric
df_plot = df.copy()
for col in [x_col_short] + y_cols_short:
    # Coercing errors to NaN and then dropping NaNs
    df_plot[col] = pd.to_numeric(df_plot[col], errors='coerce')

# Drop any row with NaN after conversion
df_plot = df_plot.dropna(subset=[x_col_short] + y_cols_short)

# Define the palette
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

# Parameters for plotting: (short_name, descriptive_label, color)
# plots = [
#     ('P11', col_map['P11'], palette["teal_dark"]),
#     ('P6', col_map['P6'], palette["gray_dark"])

# ]

plots = [
    ('P8', col_map['P8'], palette["cyan_bright"]),
    ('P9', col_map['P9'], palette["teal_dark"]),
    ('P10', col_map['P10'], palette["gray_dark"])

]

# plots = [
#     ('P2', col_map['P2'], palette["cyan_bright"]),
#     ('P3', col_map['P3'], palette["teal_dark"]),
#     ('P4', col_map['P4'], palette["gray_dark"])

# ]
# Set the desired font, falling back to a generic sans-serif
font_name = 'Century Gothic'
try:
    if font_name not in matplotlib.font_manager.findSystemFonts(fontext='ttf'):
        raise FileNotFoundError
    plt.rcParams['font.family'] = font_name
except:
    # Use a common, readable font if the requested one is not found
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'DejaVu Sans']

# Create a figure and a 2x2 grid of subplots
fig, axes = plt.subplots(nrows=1, ncols=3, figsize=(18, 6))
axes = axes.flatten()

x_label = col_map[x_col_short]

for i, (y_col_short, y_label, color) in enumerate(plots):
    ax = axes[i]
    ax.plot((df_plot[x_col_short]), df_plot[y_col_short], marker='o', linestyle='-', color=color, linewidth=2, markersize=8)
    # ax.set_title(f'{y_label} vs. {x_label}', fontsize=16)
    ax.set_xlabel(x_label, fontsize=14)
    ax.set_ylabel(y_label, fontsize=14)
    ax.grid(True, linestyle='--', alpha=0.6)
    # Set the font for tick labels
    ax.tick_params(axis='both', which='major', labelsize=12)
    # ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda val, _: f'{val:.1f}'))


# Adjust layout to prevent overlap and save the figure
plt.tight_layout()
plt.savefig('shaftWidthStudy_plots.png')