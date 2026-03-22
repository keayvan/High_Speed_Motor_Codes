# -*- coding: utf-8 -*-
"""
Created on Tue Jan 20 13:06:43 2026

@author: kkeramati
"""
from matplotlib import pyplot as plt
import pandas as pd
from pathlib import Path
import numpy as np

import sys
PROJECT_ROOT = Path("C:/Users/kkeramati/OneDrive - ARQUIMEA GROUP/HSM Project/High_Speed_Motor_Codes/TYTO_Analysis/phaseAnalysis")
sys.path.insert(0, str(PROJECT_ROOT))

from analysis.features.general_functions import find_params_in_df, find_params_in_dict, sync_time_Salea_with_TYTO, cut_shift_dataframe, cut_shift_dict
from analysis.features.general_functions import plot_parameters_across_dfs, apply_zoom_ms, mean_Salea_TYTO, efficiency_func
from analysis.features.TYTO_general import read_result,freq_fundamental, plot_parameters_multi

from analysis.features.TYTO_full_res import plot_fullRes, param_resolution, match_keys_across_dicts, plot_dicts

from analysis.features.Salea_general import  plot_channels_grid, plot_channels_grid_multi, load_prepare_dataframe
from analysis.features.Salea_general import apply_scaling_per_column

from analysis.features.power_delta import delta_instantaneous_power
from analysis.features.power_dc import dc_power_inst_ave



PROCESSED_DIR_TYTO = PROJECT_ROOT / "data" / "raw" / "TYTO"
PROCESSED_DIR_Salea = PROJECT_ROOT / "data" / "processed" 
SAVING_folder = PROJECT_ROOT / "data" / "post_proccessings"

# %%
# powertrains = ["ARC"]
# study_names = ["study_3phases"]
# freqs= [""]
# speeds_test = ["steps_04"]
# resamplings = ["fullRes"]
# time_formats = ["ms"]
# resamplings_2nd = ["manual"]

powertrains = ["ARC", "MGM"]
study_names = ["study_3phases", "study_3phases"]
freqs= ["", ""]
speeds_test = ["steps_05", "steps_02"]
resamplings = ["fullRes", "fullRes"]
time_formats = ["ms", "ms"]
resamplings_2nd = ["manual", "manual"]
resamplings_3rd = ["resample100ms", "resample100ms"]
ks_find_start = [2.2, 5]
df_res_list = []
df_TYTO_manual_list = []
df_TYTO_sync_list = []
d_time_test_list = []

time_steps_list = []
for ii ,(powertrain, study_name, freq, speed_test, resampling, time_format, resampling_2nd) in enumerate(
        zip (powertrains, study_names, freqs, speeds_test, resamplings, time_formats, resamplings_2nd)):
    
    TYTO_FILE = f"{powertrain}_{study_name}{freq}_{speed_test}_{resampling}"
    TYTO_csv = TYTO_FILE+".csv"
    
    df_TYTO_full_res = read_result(PROCESSED_DIR_TYTO / TYTO_csv,
                     powertrain = powertrain,
                     Time = time_format)
    dic_TYTO_full_res = param_resolution(df_TYTO_full_res,
                              time_format = time_format)
    TYTO_FILES_manual = f"{powertrain}_{study_name}{freq}_{speed_test}_{resampling_2nd}"
    TYTO_csv_manual = TYTO_FILES_manual+".csv"
    
    df_TYTO_manual = read_result(PROCESSED_DIR_TYTO / TYTO_csv_manual,
                     powertrain = powertrain,
                     Time = time_format)
    df_res_list.append(dic_TYTO_full_res)
    df_TYTO_manual_list.append(df_TYTO_manual)
    
    params_to_cut = ["current"]
    param_to_cut = find_params_in_df(df_TYTO_full_res, params_to_cut)
    start_TYTO_indx, start_TYTO_ms = sync_time_Salea_with_TYTO (dic_TYTO_full_res[param_to_cut[0]], y_col = param_to_cut[0],
                                          smooth_window=31, consec=5, k=ks_find_start[ii])


    params_steps = ["ESC"]
    param_to_steps = find_params_in_df(df_TYTO_full_res, params_steps)
    steps_TYTO_all = dic_TYTO_full_res[param_to_steps[0]]
    end_TYTO_ms = steps_TYTO_all.iloc[-2,0]

    df_TYTO_sync = cut_shift_dict(dic_TYTO_full_res, start_TYTO_ms,end_TYTO_ms)
    df_TYTO_sync_list.append(df_TYTO_sync)
    
    d_time_test = end_TYTO_ms - start_TYTO_ms
    d_time_test_list.append(d_time_test)
    
    steps_TYTO = df_TYTO_sync[param_to_steps[0]]
    time_steps = steps_TYTO.iloc[:,0]
    time_steps_list.append(time_steps)
    
# %%
# %%
canon_labels, key_table = match_keys_across_dicts(
    df_res_list, 
    min_sim=0.5,
    require_all=False)
labels = [x+y for x,y in zip(powertrains,freqs)]
# %%

# %%
fig0, axes0 = plot_dicts(
    df_res_list=df_res_list,
    canon_labels=canon_labels,
    key_table=key_table,
    labels=labels,
    time_format="ms",
    linestyles = ["-", "-"])
# %%

# %%
fig1, axes1 = plot_parameters_across_dfs(
        dfs=df_TYTO_manual_list,
        parameters = ['ESC throttle',
         'force Fz (thrust) (kgf)',
         'torque MZ (torque) (N⋅m)',
         'voltage (V)',
         'current (A)',
         'rotation speed (rpm)',
         'electrical power (W)',
         'mechanical power (W)',
         'ESC efficiency (%)',
         'propeller efficiency (gf/W)',
         'powertrain efficiency (gf/W)'],
        x_col="Time (ms)",              # or None to use index
        line_style = 'o-',
        df_labels=labels,
        ncols=3)
# %%

# %% Plot the sync signals
fig2, axes2 = plot_dicts(
    df_res_list=df_TYTO_sync_list,
    canon_labels=['ESC throttle',
     'force Fz (thrust) (kgf)',
     'torque MZ (torque) (N⋅m)',
     'voltage (V)',
     'current (A)',
     'rotation speed (rpm)'],
    key_table=key_table[:6],
    labels=labels,
    n_rows=2,
    time_format="ms",
    linestyles = ["-", "-"])
# %%
    
    
# %%
# %%

scale_map_ARC=  {
    "DC Current (A)": -10,
    "I_a (A)": 10,
    "I_b (A)": 10,
    "I_c (A)": 10,
    "DC Bus (V)": 10,
    "V_ab (V)": 10,
    "V_bc (V)": 10,
    "V_ac (V)": 10,
}
scale_map_MGM=  {
    "DC Current (A)": -10,
    "I_a (A)": 10,
    "I_b (A)": 10,
    "I_c (A)": 10,
    "DC Bus (V)": 10,
    "V_ab (V)": 10,
    "V_bc (V)": 10,
    "V_ac (V)": 10,
}

CHANNELS_TO_PLOT = ["DC Current (A)", "DC Bus (V)",
    "I_a (A)", "V_ab (V)",
    "I_b (A)","V_bc (V)",
    "I_c (A)", "V_ac (V)",
    "P_DC (W)","P_AC (W)"]
scale_map = [scale_map_ARC, scale_map_MGM]

df_salea_all = []
fs_all = []
for jj ,(powertrain, study_name, freq, speed_test) in enumerate(
        zip (powertrains, study_names, freqs, speeds_test)):
    Salea_file = f"{powertrain}_{study_name}{freq}_{speed_test}.parquet"
    print(f"loading: {Salea_file}")
    df_Salea, fs = load_prepare_dataframe(PROCESSED_DIR_Salea / Salea_file)
    df_scaled_Salea = apply_scaling_per_column(df_Salea, scale_map = scale_map[jj])
    df_scaled_Salea["P_AC (W)"], P_3Phase_avg= delta_instantaneous_power(
        df_scaled_Salea)

    df_scaled_Salea["P_DC (W)"],P_dc_ave = dc_power_inst_ave(df_scaled_Salea)
    df_salea_all.append(df_scaled_Salea)
    fs_all.append(fs)
    # fig3, axes3 = plot_channels_grid(
    #     df=df_scaled_Salea,
    #     channels =  CHANNELS_TO_PLOT,
    #     title = powertrain,
    #     ncols = 2,
    #     time_ms_col = "Time (ms)")
    
# %%
ks_find_start = [5, 5]
df_salea_sync_list = []
for ii , df_salea in enumerate(df_salea_all):
    start_Salea_indx, start_Sale_ms = sync_time_Salea_with_TYTO (df_salea, y_col = "I_a (A)",
                                          smooth_window=31, consec=10, k=ks_find_start[ii])
    
    df_salea_sync = cut_shift_dataframe(df_salea, start_Sale_ms)
    df_salea_sync_list.append(df_salea_sync)
    
    
    fig3, axes3 = plot_channels_grid(
        df=df_salea_sync,
        channels =  CHANNELS_TO_PLOT,
        title = powertrains[ii],
        ncols = 2,
        time_ms_col = "Time (ms)")

# %%

# %%
df_steps_ave_list=[]
efficiency_all = []

for i in range(len(df_salea_sync_list)):
    df_salea_sync = df_salea_sync_list[i]
    time_steps = time_steps_list[i]
    
    df_TYTO_sync = df_TYTO_sync_list[i]
    df_TYTO_manual = df_TYTO_manual_list[i]
    
    
    _,_,df_steps_ave=mean_Salea_TYTO (df_TYTO_sync,
                         df_TYTO_manual,
                         time_steps,
                         df_salea_sync)
    df_steps_ave_list.append(df_steps_ave)
    eff = efficiency_func(df_steps_ave)
    efficiency_all.append(eff)
    
palette = {
    "navy_dark": "#0F3878",
    "red_bright": "#f74242ff",
    "gray_dark": "#525252ff",
    "sky_blue": "#0FAAF0",
    "teal_dark": "#009494ff",
    "teal_light": "#00d0b8",
    "lime_green": "#0AFFA0",
    "blue_medium": "#0f75bcff",
    "cyan_bright": "#29e2ecff",
    "crimson_dark": "#9e0012ff",
    "coral_pink": "#ff596c",
    "taupe": "#95755A",
    "orange_bright": "#f7941dff",
    "peach_orange": "#ffad5aff",
    "gray_medium": "#848484ff"
}
color = list(palette.values())
fig3, axes3 = plt.subplots(1,2, figsize = (10,5))
axes3= axes3.ravel()
for j, u in enumerate(df_steps_ave_list):
    for i, v in enumerate(u.columns[3:]):
        axes3[j].plot(u["Speed (rpm)"],u[v], '-o', label = v)
        axes3[j].set_xlabel("Speed (rpm)")
        axes3[j].set_ylabel("Power (W)")
        axes3[j].set_title(powertrains[j])
        axes3[j].legend()
        axes3[j].grid('both')

style = ['-o','--*']
plt.figure()
for j, u in enumerate(df_steps_ave_list):
    for i, v in enumerate(u.columns[[3,4,6]]):
        plt.plot(u["Speed (rpm)"],u[v], style[j], label = v + "_"+powertrains[j], color = color[i])
        plt.xlabel("Speed (rpm)")
        plt.ylabel("Power (W)")
        plt.title("Pulsar vs MGM Powers")
        plt.legend()
        plt.grid('both')

# %%


# %%



fig5, axes5 = plt. subplots(1,2, figsize=(10,5))
axes5 =axes5. ravel()
for i,v in enumerate(df_steps_ave_list):
    eff = efficiency_all[i]
    
    for k, w in enumerate(eff.columns):
        axes5[i].plot(df_steps_ave["Speed (rpm)"],eff[w], '-o', color = color[k], label = w)
        axes5[i].set_xlabel("Speed (rpm)")
        axes5[i].set_ylabel("Efficiency %")
        axes5[i].set_ylim(20,100)
        axes5[i].set_title(powertrains[i])
        axes5[i].legend()
        axes5[i].grid('both')
plt.figure()        
for i,v in enumerate(df_steps_ave_list):
    eff = efficiency_all[i]
    
    for k, w in enumerate(eff.columns):
        plt.plot(df_steps_ave["Speed (rpm)"],eff[w], style[i], color = color[k], label = w+"_"+powertrains[i])
        plt.xlabel("Speed (rpm)")
        plt.ylabel("Efficiency %")
        plt.title("Pulsar vs MGM Efficiencies")
        plt.legend()
        plt.grid('both')
   
    # for j,u in enumerate(cols):
    #     axes[j].plot(df_steps_ave_list[i]["Speed (rpm)"],efficiency_all[i][u], '-o', color= color_cycle[i], label = powertrains[i])
    #     axes[j].set_xlabel("Speed (rpm)")
    #     axes[j].set_ylabel(u)

    #     axes[j].legend()
    #     axes[j].grid('both')




