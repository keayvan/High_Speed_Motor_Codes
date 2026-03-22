# -*- coding: utf-8 -*-
"""
Created on Tue Dec 16 11:35:27 2025

@author: kkeramati
"""

import pandas as pd
import matplotlib.pyplot as plt
import math
from analysisPlotting_func import plot_from_dataframe as plot
# ----------------- COLOR PALETTE -----------------
plt.rcParams["font.family"] = "Century Gothic"

# ----------------- EDIT ONLY THESE -----------------
subplot_params = [
    "Battery_Voltage",
    "Battery_Amperage",
    "Motor_RPM",
    "Temperature_Control",
    "Temperature_Motor",
    "Battery_Capacity",
]

overlay_params = [
    "TAS_a",
    "Vground",
    "Vz",
    "Roll",
    "Pitch",
]

df = pd.read_csv("./data/ARC_Defence_data/2025_11_20_12_47_11.csv")
df = df.replace(r'^\s*$', pd.NA, regex=True)

df = df.ffill()
keywords = ["Throttle"]
pattern = "|".join(keywords)   # "Throttle|Pedal"

cols = list(df.columns[df.columns.str.contains(pattern, case=False, na=False)])

plot(
    df,
    subplot_params = None,
    overlay_params = cols,
    xAxis = None,
    n_cols=3
)
# --------------------------------------------------
