# -*- coding: utf-8 -*-
"""
Created on Mon Mar  2 13:25:14 2026

@author: kkeramati
"""
from pathlib import Path

import sys
PROJECT_ROOT = Path("C:/Users/kkeramati/OneDrive - ARQUIMEA GROUP/HSM Project/High_Speed_Motor_Codes/TYTO_Analysis/phaseAnalysis")
sys.path.insert(0, str(PROJECT_ROOT))
from analysis.features.TYTO_general import read_result
from analysis.features.TYTO_full_res import  param_resolution
from analysis.features.TYTO_full_res import plot_fullRes, param_resolution, match_keys_across_dicts, plot_dicts

from analysis.features.general_functions import find_params_in_df
from matplotlib import pyplot as plt

PROCESSED_DIR_TYTO = PROJECT_ROOT / "data" / "raw" / "TYTO"
PROCESSED_DIR_Salea = PROJECT_ROOT / "data" / "processed" 
SAVING_folder = PROJECT_ROOT / "data" / "post_proccessings"

electronics = ["ARC"]
motors=["P43_32187"]
powertrains = [x+"_"+y for x,y in zip(electronics,motors)]
study_names = "Kp_Ki"
freqs= ""
speeds_test = "steps"
resamplings = "fullRes"

TYTO_FILES = f"{powertrains[0]}_{study_names}{freqs}_{speeds_test}_{resamplings}"
TYTO_csv = TYTO_FILES+".csv"

time_format = "s"
df_TYTO_full_res = read_result(PROCESSED_DIR_TYTO / TYTO_csv,
                 powertrain = powertrains[0],
                 Time = time_format)

dic_TYTO_full_res = param_resolution(df_TYTO_full_res,
                          time_format = time_format)


canon_labels, key_table = match_keys_across_dicts(
    [dic_TYTO_full_res],  
    min_sim=0.25,
    require_all=False)

labels = [x+y for x,y in zip(powertrains,study_names)]

fig0, axes0 = plot_dicts(
    df_res_list= [dic_TYTO_full_res],
    canon_labels=canon_labels,
    key_table=key_table,
    labels=study_names,
    time_format="ms",
    linestyles = ["-"])


params = ["torque", "voltage", "current", "speed"]
params_TYTO= find_params_in_df(df_TYTO_full_res, params)

data  = [dic_TYTO_full_res[k] for k in params_TYTO]

time_all = []
y_data_all = []
for i, v in enumerate (data):
    time = v.iloc[:,0]
    y_data = v.iloc[:,1]/v.iloc[:,1].max()
    time_all.append(time)
    y_data_all.append(y_data)

palette = {
    "lime_green": "#0AFFA0",
    "red_bright": "#f74242ff",
    "orange_bright": "#f7941dff",

    "navy_dark": "#0F3878",

    "teal_dark": "#009494ff",
    "gray_medium": "#848484ff",


    "sky_blue": "#0FAAF0",
    "cyan_bright": "#29e2ecff",
    "crimson_dark": "#9e0012ff",
    "coral_pink": "#ff596c",
    "teal_light": "#00d0b8",
    "taupe": "#95755A",
    "peach_orange": "#ffad5aff",
    "gray_dark": "#525252ff",
}
colors = list(palette.values())
time_zoom = [22,22.1]
plt.figure()
for i,v in enumerate(params):
    plt.plot(time_all[i], y_data_all[i], label = params[i], color = colors[i])
    plt.axvline(x = time_zoom[0], linestyle = '--', color = "#525252ff")
    plt.axvline(x = time_zoom[1], linestyle = '--', color = "#525252ff")
    plt.xlim(5,32)

    plt.xlabel("Time(s)")
    plt.ylabel("Normalized parameter")
    plt.legend()
    plt.grid("both")
    
plt.figure()
for i,v in enumerate(params):
    plt.plot(time_all[i], y_data_all[i],"-o", color = colors[i],ms = 4, label = params[i])
    plt.xlim(time_zoom)
    plt.xlabel("Time(s)")
    plt.ylabel("Normalized parameter")
    plt.legend()
    plt.grid("both")