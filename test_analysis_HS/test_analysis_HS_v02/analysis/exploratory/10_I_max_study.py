# -*- coding: utf-8 -*-
"""
Created on Mon Feb 23 09:51:16 2026

@author: kkeramati
"""

from matplotlib import pyplot as plt
import pandas as pd
from pathlib import Path
import numpy as np

import sys
try:
    PROJECT_ROOT = Path(__file__).resolve().parents[2]
except NameError:
    # fallback for notebooks / interactive
    PROJECT_ROOT = Path.cwd().parent.parent

sys.path.insert(0, str(PROJECT_ROOT))
print(PROJECT_ROOT)

from analysis.features.general_functions import find_params_in_df, find_params_in_dict, sync_time_Salea_with_TYTO, cut_shift_dataframe, cut_shift_dict
from analysis.features.general_functions import plot_parameters_across_dfs, apply_zoom_ms, mean_Salea_TYTO, efficiency_func, mean_tyto_full_resolution
from analysis.features.TYTO_general import read_result,freq_fundamental, plot_parameters_multi

from analysis.features.TYTO_full_res import plot_fullRes, param_resolution, match_keys_across_dicts, plot_dicts





PROCESSED_DIR_TYTO = PROJECT_ROOT / "data" / "raw" / "TYTO"
PROCESSED_DIR_Salea = PROJECT_ROOT / "data" / "processed" 
SAVING_folder = PROJECT_ROOT / "data" / "post_proccessings"

electronics = ["ARC"]*6
motors=["P43_10002199_32187"]*6
powertrains = [x+"_"+y for x,y in zip(electronics,motors)]
study_names = ["i115","i120","i125", "i130", "i135", "i140" ]
freqs= [""]*6
speeds_test = ["ramp"]*6
resamplings = ["fullRes"]*6
time_formats = ["ms"]*6
resamplings_2nd = ["manual"]*6
resamplings_3rd = ["resample100ms"]*6
df_res_list = []
df_TYTO_manual_list = []
df_TYTO_sync_list = []
d_time_test_list = []
df_resample100 = []
satrt_indx = [1]*6

time_steps_list = []
df_mean_TYTO_list = []
for ii ,(powertrain, study_name, freq, speed_test, resampling, time_format, resampling_2nd) in enumerate(
        zip (powertrains, study_names, freqs, speeds_test, resamplings, time_formats, resamplings_2nd)):
    
    TYTO_FILES_manual = f"{powertrain}_{study_name}{freq}_{speed_test}_{resampling_2nd}"
    TYTO_csv_manual = TYTO_FILES_manual+".csv"
    
    df_TYTO_manual = read_result(PROCESSED_DIR_TYTO / TYTO_csv_manual,
                     powertrain = powertrain,
                     Time = time_format)
    df_TYTO_manual = df_TYTO_manual.iloc[satrt_indx[ii]:,:]
    time_start = df_TYTO_manual.iloc[0,0]
    
    df_TYTO_manual_list.append(df_TYTO_manual)
    
    
    TYTO_FILES_resample100 = f"{powertrain}_{study_name}{freq}_{speed_test}_{resamplings_3rd[ii]}"
    TYTO_csv_resample100 = TYTO_FILES_resample100+".csv"
    

    df_TYTO_resample100 = read_result(PROCESSED_DIR_TYTO / TYTO_csv_resample100,
                     powertrain = powertrain,
                     Time = time_format)
    
    mask = (df_TYTO_resample100["Time (ms)"] > time_start) 
    df_TYTO_resample100 = df_TYTO_resample100[mask]
    
    df_resample100.append(df_TYTO_resample100)
    
    TYTO_FILE = f"{powertrain}_{study_name}{freq}_{speed_test}_{resampling}"
    TYTO_csv = TYTO_FILE+".csv"
    
    df_TYTO_full_res = read_result(PROCESSED_DIR_TYTO / TYTO_csv,
                     powertrain = powertrain,
                     Time = time_format)
    dic_TYTO_full_res = param_resolution(df_TYTO_full_res,
                              time_format = time_format)
    
    df_res_list.append(dic_TYTO_full_res)
    
    params_steps = ["ESC"]
    param_to_steps = find_params_in_df(df_TYTO_full_res, params_steps)
    steps_TYTO_all = dic_TYTO_full_res[param_to_steps[0]]
    time_steps = steps_TYTO_all.iloc[:,0]
    time_steps_list.append(time_steps)

    df_mean_TYTO = mean_tyto_full_resolution(dic_TYTO_full_res, time_steps)
    df_mean_TYTO_list.append(df_mean_TYTO)




canon_labels, key_table = match_keys_across_dicts(
    df_res_list,  
    min_sim=0.25,
    require_all=False)

labels = [x+y for x,y in zip(powertrains,study_names)]

fig0, axes0 = plot_parameters_across_dfs(
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
        x_col='ESC throttle',              # or None to use index
        line_style = 'o-',
        df_labels=study_names,
        ncols=3)



fig1, axes1 = plot_parameters_across_dfs(
        dfs=df_resample100,
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
        x_col='ESC throttle',              # or None to use index
        line_style = '-',
        df_labels=study_names,
        ncols=3)



fig0, axes0 = plot_parameters_across_dfs(
        dfs=df_TYTO_manual_list,
        parameters = ['voltage (V)',
         'current (A)',
         'electrical power (W)',
         'mechanical power (W)',
         'ESC efficiency (%)',
         'powertrain efficiency (gf/W)'],
        x_col="speed",              # or None to use index
        line_style = 'o-',
        df_labels=study_names,
        ncols=3)

fig0, axes0 = plot_dicts(
    df_res_list=df_res_list,
    canon_labels=canon_labels,
    key_table=key_table,
    labels=study_names,
    time_format="ms",
    linestyles = ["-"]*6)

