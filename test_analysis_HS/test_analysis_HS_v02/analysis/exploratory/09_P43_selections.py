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

from analysis.features.Salea_general import  plot_channels_grid, plot_channels_grid_multi, load_prepare_dataframe
from analysis.features.Salea_general import apply_scaling_per_column

from analysis.features.power_delta import delta_instantaneous_power
from analysis.features.power_dc import dc_power_inst_ave



PROCESSED_DIR_TYTO = PROJECT_ROOT / "data" / "raw" / "TYTO"
PROCESSED_DIR_Salea = PROJECT_ROOT / "data" / "processed" 
SAVING_folder = PROJECT_ROOT / "data" / "post_proccessings"

n_repeatition = 9
# electronics = ["MGM", "ARC"]
electronics = ["ARC"]*n_repeatition

# motors=["scorpion","P43_32187"]
motors=["P43_32193"]*n_repeatition

powertrains = [x+"_"+y for x,y in zip(electronics,motors)]
# study_names = ["3phase_comparision", "3phases_P43_selections" ]
# powertrains = [powertrains [0]]
study_names = ["selection" ]*n_repeatition
freqs= [""]*n_repeatition
# speeds_test = ["steps_01"]
speeds_test =[f'steps_0{x}' for x in range(1,10)]
resamplings = ["fullRes"]*n_repeatition
time_formats = ["ms"]*n_repeatition
resamplings_2nd = ["manual"]*n_repeatition
resamplings_3rd = ["resample100ms"]*n_repeatition
df_res_list = []
df_TYTO_manual_list = []
df_TYTO_sync_list = []
d_time_test_list = []
df_resample100 = []
satrt_indx = [1]*n_repeatition

time_steps_list = []
df_mean_TYTO_list = []
dfs_TYTO_manual = {}
dfs_TYTO_resample100 = {}
dfs_TYTO_full_res = {}
dfs_TYTO_mean = {}
for ii ,(powertrain, study_name, freq, speed_test, resampling, time_format, resampling_2nd) in enumerate(
        zip (powertrains, study_names, freqs, speeds_test, resamplings, time_formats, resamplings_2nd)):
    
    TYTO_FILES_manual = f"{powertrain}_{study_name}{freq}_{speed_test}_{resampling_2nd}"
    TYTO_csv_manual = TYTO_FILES_manual+".csv"
    
    df_TYTO_manual = read_result(PROCESSED_DIR_TYTO / TYTO_csv_manual,
                     powertrain = '',
                     Time = time_format)
    df_label = powertrain+'_'+speed_test
    dfs_TYTO_manual[df_label] = df_TYTO_manual
    
    df_TYTO_manual = df_TYTO_manual.iloc[satrt_indx[ii]:,:]
    time_start = df_TYTO_manual.iloc[0,0]
    
    df_TYTO_manual_list.append(df_TYTO_manual)
    
    
    TYTO_FILES_resample100 = f"{powertrain}_{study_name}{freq}_{speed_test}_{resamplings_3rd[ii]}"
    TYTO_csv_resample100 = TYTO_FILES_resample100+".csv"
    

    df_TYTO_resample100 = read_result(PROCESSED_DIR_TYTO / TYTO_csv_resample100,
                     powertrain = '',
                     Time = time_format)
    
    dfs_TYTO_resample100[df_label] = df_TYTO_resample100

    
    mask = (df_TYTO_resample100["Time (ms)"] > time_start) 
    df_TYTO_resample100 = df_TYTO_resample100[mask]
    
    df_resample100.append(df_TYTO_resample100)
    
    TYTO_FILE = f"{powertrain}_{study_name}{freq}_{speed_test}_{resampling}"
    TYTO_csv = TYTO_FILE+".csv"
    
    df_TYTO_full_res = read_result(PROCESSED_DIR_TYTO / TYTO_csv,
                     powertrain = '',
                     Time = time_format)
    dic_TYTO_full_res = param_resolution(df_TYTO_full_res,
                              time_format = time_format)
    
    dfs_TYTO_full_res[df_label] = dic_TYTO_full_res
    
    df_res_list.append(dic_TYTO_full_res)
    
    
    params_steps = ["ESC"]
    param_to_steps = find_params_in_df(df_TYTO_full_res, params_steps)
    steps_TYTO_all = dic_TYTO_full_res[param_to_steps[0]]
    time_steps = steps_TYTO_all.iloc[:,0]
    time_steps_list.append(time_steps)

    df_mean_TYTO = mean_tyto_full_resolution(dic_TYTO_full_res, time_steps)
    param_p_mechanical = ["torque", "speed"]
    param_p_mechanical= find_params_in_df(df_TYTO_full_res, param_p_mechanical)

    param_p_electrical = ["voltage", "current"]
    param_p_electrical= find_params_in_df(df_TYTO_full_res, param_p_electrical)


    df_mean_TYTO['ESC throttle'] =steps_TYTO_all.iloc[1:,1]
    df_mean_TYTO['Time (ms)'] =steps_TYTO_all.iloc[1:,0]


    df_mean_TYTO['mechanical power (W)'] = abs(df_mean_TYTO[param_p_mechanical[0]]*df_mean_TYTO[param_p_mechanical[1]])*2*np.pi/60
    df_mean_TYTO['electrical power (W)'] = abs(df_mean_TYTO[param_p_electrical[0]]*df_mean_TYTO[param_p_electrical[1]])
    df_mean_TYTO['ESC efficiency (%)'] = df_mean_TYTO['mechanical power (W)']/df_mean_TYTO['electrical power (W)']*100

    dfs_TYTO_mean[df_label] = df_mean_TYTO

    df_mean_TYTO_list.append(df_mean_TYTO)

dfs_TYTO_manual = pd.DataFrame([dfs_TYTO_manual])
dfs_TYTO_resample100 = {}
dfs_TYTO_full_res = {}
dfs_TYTO_mean = {}


df_mean_TYTO_all  = np.stack([df.values for df in df_mean_TYTO_list], axis=0)  # shape (9, 6, 7)



canon_labels, key_table = match_keys_across_dicts(
    df_res_list,  
    min_sim=0.25,
    require_all=False)

labels = [x+"_"+y for x,y in zip(motors,speeds_test)]

fig0, axes0 = plot_parameters_across_dfs(
        dfs=df_TYTO_manual_list,
        parameters = [
         'ESC efficiency (%)'],
        x_col="speed",              # or None to use index
        line_style = 'o',
        df_labels=labels,
        ncols=3)

fig0, axes0 = plot_parameters_across_dfs(
        dfs=df_mean_TYTO_list,
        parameters = [
         'ESC efficiency (%)'],
        x_col="speed",              # or None to use index
        line_style = 'o',
        df_labels=labels,
        ncols=3)

fig01, axes01 = plot_parameters_across_dfs(
        dfs=[df_mean_TYTO_list[0],df_TYTO_manual_list[0]],
        parameters = [
         'force Fz (thrust) (kgf)',
         'torque MZ (torque) (N⋅m)',
         'voltage (V)',
         'current (A)',
         'rotation speed (rpm)',
         'electrical power (W)',
         'mechanical power (W)',
         'ESC efficiency (%)'],
        
        x_col="Time (ms)",              # or None to use index
        line_style = 'o-',
        df_labels=["mean","Manual"],
        ncols=3)


fig02, axes02 = plot_parameters_across_dfs(
        dfs=df_resample100,
        parameters = [

         'force Fz (thrust) (kgf)',
         'torque MZ (torque) (N⋅m)',
         'voltage (V)',
         'current (A)',
         'rotation speed (rpm)',
         'electrical power (W)',
         'mechanical power (W)',
         'ESC efficiency (%)'
],
        x_col="Time (ms)",              # or None to use index
        line_style = '-',
        df_labels=labels,
        ncols=3)



fig03, axes03 = plot_parameters_across_dfs(
        dfs=df_mean_TYTO_list,
        parameters = ['voltage (V)',
         'current (A)',
         'electrical power (W)',
         'mechanical power (W)',
         'ESC efficiency (%)',
         'powertrain efficiency (gf/W)'],
        x_col="speed",              # or None to use index
        line_style = 'o-',
        df_labels=labels,
        ncols=3)

# fig0, axes0 = plot_dicts(
#     df_res_list=dfs_TYTO_mean,
#     canon_labels=canon_labels,
#     key_table=key_table,
#     labels=labels,
#     time_format="ms",
#     linestyles = ["-"]*9)

key = list(dfs_TYTO_mean.keys())[0]
df = dfs_TYTO_mean[key]

fig, ax = plt.subplots(3,4)
ax = ax.ravel()
for i in range(df.shape[1]):
    ax[i].plot(df["Time (ms)"],df.iloc[:,i])
    

params = [" current (A)", " voltage (V)"]  # parameters to plot

n_params = len(params)

fig, axes = plt.subplots(n_params, 1, figsize=(8, 4*n_params), sharex=True)

# If only one parameter, axes is not a list → fix that
if n_params == 1:
    axes = [axes]

for ax, param in zip(axes, params):
    for name, df in dfs_TYTO_mean.items():
        ax.plot(df["Time (ms)"], df[param], label=name)

    ax.set_title(param)
    ax.set_ylabel(param)
    ax.legend()

axes[-1].set_xlabel("Time (ms)")

plt.tight_layout()
plt.show()

import math
import matplotlib.pyplot as plt

palette = {
    "teal_dark": "#009494ff",
    "red_bright": "#f74242ff",
    "gray_medium": "#848484ff",
    "lime_green": "#0AFFA0",
    "orange_bright": "#f7941dff",
    "navy_dark": "#0F3878",
    "blue_medium": "#0f75bcff",
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


def plot_parameters_across_dfs(
    dfs_dict,                 # dict: {name: df}
    parameters,               # str or list[str]
    x_col=None,               # column for x-axis (None → use index)
    colors=colors,
    line_style='-',
    ncols=2,
    figsize_per_subplot=(5, 2),
):

    if isinstance(parameters, str):
        parameters = [parameters]

    df_names = list(dfs_dict.keys())
    dfs = list(dfs_dict.values())

    n = len(parameters)
    nrows = math.ceil(n / ncols)

    fig_w = figsize_per_subplot[0] * ncols
    fig_h = figsize_per_subplot[1] * nrows
    fig, axes = plt.subplots(nrows=nrows, ncols=ncols,
                             figsize=(fig_w, fig_h),
                             squeeze=False)

    for p_idx, param in enumerate(parameters):
        ax = axes[p_idx // ncols][p_idx % ncols]

        for i, (name, df) in enumerate(zip(df_names, dfs)):

            x = df[x_col] if x_col is not None else df.index
            y = df[param]

            ax.plot(
                x,
                y,
                line_style,
                color=colors[i % len(colors)],
                linewidth=1.8,
                label=name
            )

        ax.set_xlabel(x_col if x_col else "Index")
        ax.set_ylabel(param)
        ax.set_title(param)
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=8)

    # Hide unused subplots
    for k in range(n, nrows * ncols):
        axes[k // ncols][k % ncols].set_axis_off()

    plt.tight_layout()
    plt.show()
    return fig, axes

# plot_parameters_across_dfs(
#     dfs_dict = dfs_TYTO_mean,                 # dict: {name: df}
#     parameters = params,               # str or list[str]
#     x_col="Time (ms)",               # column for x-axis (None → use index)
#     colors=colors,
#     line_style='-',
#     ncols=2,
#     figsize_per_subplot=(5, 2),
# )