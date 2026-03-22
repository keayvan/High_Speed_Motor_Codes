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
try:
    PROJECT_ROOT = Path(__file__).resolve().parents[2]
except NameError:
    # fallback for notebooks / interactive
    PROJECT_ROOT = Path.cwd().parent.parent

sys.path.insert(0, str(PROJECT_ROOT))
print(PROJECT_ROOT)

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

powertrains = ["MGM","ARC"]
# powertrains = ["MGM"]

study_names = ["flightTest", "flightTest"]
freqs= ["", ""]
speeds_test = ["durability","durability"]
resamplings = ["resample100ms_filter10Hz", "resample100ms_filter10Hz"]
time_formats = ["ms", "ms"]
resamplings_2nd = ["manual", "manual"]
resamplings_3rd = ["resample100ms","resample100ms"]
ks_find_start = [2.2, 2.2]
df_TYTO_resample_list = []
df_TYTO_manual_list = []
df_TYTO_sync_list = []
d_time_test_list = []

time_steps_list = []
for ii ,(powertrain, study_name, freq, speed_test, resampling, time_format, resampling_2nd,resampling_3rd) in enumerate(
        zip (powertrains, study_names, freqs, speeds_test, resamplings, time_formats, resamplings_2nd, resamplings_3rd)):
    
    TYTO_FILE = f"{powertrain}_{study_name}{freq}_{speed_test}_{resampling_3rd}"
    TYTO_csv = TYTO_FILE+".csv"
    df_TYTO_resample = read_result(PROCESSED_DIR_TYTO / TYTO_csv,
                     powertrain = powertrain,
                     Time = time_format)
    df_TYTO_resample_list.append(df_TYTO_resample)
    
    TYTO_FILES_manual = f"{powertrain}_{study_name}{freq}_{speed_test}_{resampling_2nd}"
    TYTO_csv_manual = TYTO_FILES_manual+".csv"
    
    df_TYTO_manual = read_result(PROCESSED_DIR_TYTO / TYTO_csv_manual,
                     powertrain = powertrain,
                     Time = time_format)
    df_TYTO_manual_list.append(df_TYTO_manual)
    
canon_labels, key_table = match_keys_across_dicts(
    df_TYTO_resample_list, 
    min_sim=0.5,
    require_all=False)
labels = [x+y for x,y in zip(powertrains,freqs)]   

fig1, axes1 = plot_parameters_across_dfs(
        dfs=df_TYTO_resample_list,
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
        line_style = '-',
        df_labels=labels,
        ncols=3)

fig2, axes2 = plot_parameters_across_dfs(
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