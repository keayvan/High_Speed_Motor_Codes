# -*- coding: utf-8 -*-
"""
Created on Tue Sep 23 16:23:03 2025

@author: kkeramati
"""

import pandas as pd
import matplotlib.pyplot as plt
import glob
import numpy as np
from sklearn.metrics import r2_score

proj_name = 'prpeller_char'
files = glob.glob(f"./Results_TYTO/{proj_name}/*.csv")


avg_list = []

for file in files:
    df = pd.read_csv(file)  
    
    time = df.iloc[:, 0]
    
    avg = df.iloc[:, 1:].mean()
    avg["file"] = file
    avg_list.append(avg)
    


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


avg_df = pd.DataFrame(avg_list).set_index("file")


# plt.figure()
# plt.plot (avg_df.iloc[:,0],avg_df.iloc[:,5],'-o')

plt.figure()
plt.plot (avg_df.iloc[:,5],avg_df.iloc[:,2],'-o',color=palette["teal_dark"],mfc='#0AFFA0',mec='#0FAAF0',lw=2,ms=6)
plt.xlabel(avg_df.columns[5])
plt.ylabel(avg_df.columns[2])
for x, y in zip(avg_df.iloc[:,5],avg_df.iloc[:,2]):
            plt.text(x, y, f"({x:.0f},{y:.2f})", fontsize=8, ha="center", va="bottom")




df_th_rs = avg_df[['Powertrain 1 - ESC throttle (μs)','Powertrain 1 - rotation speed (rpm)']]
deg = 2
coeffs = np.polyfit(df_th_rs["Powertrain 1 - ESC throttle (μs)"], df_th_rs["Powertrain 1 - rotation speed (rpm)"], deg)
poly = np.poly1d(coeffs)
r2_poly = r2_score(df_th_rs["Powertrain 1 - rotation speed (rpm)"], poly(df_th_rs["Powertrain 1 - ESC throttle (μs)"]))

print("Polynomial Fit (deg=2):")
print(poly)
print(f"R² = {r2_poly:.4f}")

x_fit = np.linspace(df_th_rs["Powertrain 1 - ESC throttle (μs)"].min(), df_th_rs["Powertrain 1 - ESC throttle (μs)"].max(), 300)

plt.figure()
plt.scatter(df_th_rs["Powertrain 1 - ESC throttle (μs)"], df_th_rs["Powertrain 1 - rotation speed (rpm)"], label="Data", color="black")
plt.plot(x_fit, poly(x_fit), 'r-', label=f"Poly fit (R²={r2_poly:.3f})")

plt.xlabel("Throttle (μs)")
plt.ylabel("Rotation Speed (rpm)")
plt.legend()
plt.grid(True)
plt.show()
