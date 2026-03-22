# -*- coding: utf-8 -*-
"""
Created on Tue Jan 27 15:54:21 2026

@author: kkeramati
"""

from pathlib import Path
import sys
try:
    PROJECT_ROOT = Path(__file__).resolve().parents[2]
except NameError:
    # fallback for notebooks / interactive
    PROJECT_ROOT = Path.cwd().parent.parent

sys.path.insert(0, str(PROJECT_ROOT))
print(PROJECT_ROOT)
from analysis.features.TYTO_general import read_result 
from analysis.features.TYTO_full_res import param_resolution 
from analysis.features.TYTO_full_res import plot_fullRes 
from matplotlib import pyplot as plt
plt.rcParams["font.family"] = "Century Gothic"

speed_points = [2000, 4000, 6000, 8000, 10000, 12000, 14000, 15000]

PROCESSED_DIR_TYTO = PROJECT_ROOT / "data" / "raw" / "TYTO"
powertrain =["ARC_f_swiching 20KHz", "ARC_f_swiching 20KHz Madrid FW","ARC_f_swiching 40KHz"]
time_format = ["ms", "ms", 'ms']
TYTO_FILES = ["ARC_SwitchingFrequency20KHz_steps_fullRes.csv",
              "ARC_SwitchingFrequency20KHz_steps_Madrid_framware_fullRes.csv",
              "ARC_SwitchingFrequency40KHz_steps_fullRes.csv"]

df_TYTOs = []
for i,v in enumerate(TYTO_FILES):
    df = read_result(PROCESSED_DIR_TYTO / v,
                     powertrain = powertrain[i],
                     Time = time_format[i])
    
    df_res = param_resolution(df,
                              time_format = time_format[i]) 
    
    df_TYTOs.append(df_res)

    plot_fullRes(df_res,
                     params=all,
                     n_rows=4)

colors = ['#0F3878', '#ff596c', '#525252ff', '#009494ff', '#f7941dff'] 

par_plot = "speed"
plt.figure()
for i,v in enumerate(df_TYTOs):
    df_p  = v
    keys = list(df_p.keys())
    for j, v in enumerate(keys):
        if par_plot in v:
            par = v
            
            
    plt.plot(df_p[par].iloc[:,0], df_p[par].iloc[:,1], label = powertrain[i], color = colors[i])
    plt.xlabel("Time (ms)")
    plt.ylabel(par_plot)
    plt.legend()
    plt.grid("both")
    