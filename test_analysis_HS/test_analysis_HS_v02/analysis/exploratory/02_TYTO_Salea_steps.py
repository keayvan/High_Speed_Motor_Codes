# -*- coding: utf-8 -*-
"""
Created on Tue Jan 20 13:06:43 2026

@author: kkeramati
"""
from matplotlib import pyplot as plt
import pandas as pd
from pathlib import Path
import sys
# PROJECT_ROOT = Path("C:/Users/kkeramati/OneDrive - ARQUIMEA GROUP/HSM Project/High_Speed_Motor_Codes/TYTO_Analysis/phaseAnalysis")
# sys.path.insert(0, str(PROJECT_ROOT))
try:
    PROJECT_ROOT = Path(__file__).resolve().parents[2]
except NameError:
    # fallback for notebooks / interactive
    PROJECT_ROOT = Path.cwd().parent.parent

sys.path.insert(0, str(PROJECT_ROOT))
print(PROJECT_ROOT)

from analysis.features.general_functions import find_params_in_df, sync_time_Salea_with_TYTO, cut_shift_dataframe, cut_shift_dict
from analysis.features.general_functions import plot_parameters_across_dfs
from analysis.features.TYTO_general import read_result,freq_fundamental, plot_parameters_multi

from analysis.features.TYTO_full_res import plot_fullRes, param_resolution

from analysis.features.Salea_general import resolve_selected_files, plot_channels_grid, load_prepare_dataframe
from analysis.features.Salea_general import apply_scaling_per_column, apply_zoom_ms

from analysis.features.power_delta import delta_instantaneous_power
from analysis.features.power_dc import dc_power_inst_ave


           #######################################
######################## TYTO DATA #########################
           #######################################


PROCESSED_DIR_TYTO = PROJECT_ROOT / "data" / "raw" / "TYTO"
PROCESSED_DIR_Salea = PROJECT_ROOT / "data" / "processed" 
SAVING_folder = PROJECT_ROOT / "data" / "post_proccessings"
# %% Read TYTO ARC 
powertrain = "ARC_P43"
study_name = "take_off"
freq= ""
speed = "test"
resampling = "fullRes"
time_format = "ms"
    
TYTO_FILES = f"{powertrain}_{study_name}{freq}_{speed}_{resampling}"
TYTO_csv = TYTO_FILES+".csv"

df_TYTO_full_res = read_result(PROCESSED_DIR_TYTO / TYTO_csv,
                 powertrain = powertrain,
                 Time = time_format)

dic_TYTO_full_res = param_resolution(df_TYTO_full_res,
                          time_format = time_format) 

resampling = "manual"
TYTO_FILES_manual = f"{powertrain}_{study_name}{freq}_{speed}_{resampling}"
TYTO_csv = TYTO_FILES_manual+".csv"
df_TYTO_manual = read_result(PROCESSED_DIR_TYTO / TYTO_csv,
                 powertrain = powertrain,
                 Time = time_format)


params_to_cut = ["current"]
param_to_cut = find_params_in_df(df_TYTO_full_res, params_to_cut)
start_TYTO_indx, start_TYTO_ms = sync_time_Salea_with_TYTO (dic_TYTO_full_res[param_to_cut[0]], y_col = param_to_cut[0],
                                      smooth_window=31, consec=10, k=1)


params_steps = ["ESC"]
param_to_steps = find_params_in_df(df_TYTO_full_res, params_steps)
steps_TYTO_all = dic_TYTO_full_res[param_to_steps[0]]
end_TYTO_ms = steps_TYTO_all.iloc[-2,0]

df_TYTO_sync = cut_shift_dict(dic_TYTO_full_res, start_TYTO_ms,end_TYTO_ms)
steps_TYTO = df_TYTO_sync[param_to_steps[0]]

t_start_step = list(steps_TYTO.iloc[:-1,0])
t_end_step = list(steps_TYTO.iloc[1:,0])


# %% Plot the raw data
plt.rcParams["font.family"] = "Century Gothic"
fig1, axes1 = plot_fullRes(dic_TYTO_full_res,
                 params=all,
                 n_rows=4)

# %%

# %%Plot test area
plt.rcParams["font.family"] = "Century Gothic"
fig1, axes1 = plot_fullRes(df_TYTO_sync,
                 params=all,
                 n_rows=4)

# %%

# %% Plot average points
fig2, axes2 = plot_parameters_across_dfs(
        dfs=[df_TYTO_manual],
        parameters=["ESC throttle", "Fz", "Mz", "voltage", "current", "speed", "electrical", "mechanical", "ESC efficiency"] ,
        x_col="Time (ms)",              # or None to use index
        line_style = 'o-',
        df_labels=['ARC'],
        ncols=3)
# %%

           #######################################
######################## SALEA DATA #########################
           #######################################

# %%
Salea_file = [f"{powertrain}_{study_name}{freq}_{speed}.parquet"]
files_salea = resolve_selected_files(PROCESSED_DIR_Salea, Salea_file)
df_Salea_s = files_salea[0]

df_Salea, fs = load_prepare_dataframe(df_Salea_s)

df_scaled_Salea = apply_scaling_per_column(df_Salea)

start_Salea_indx, start_Sale_ms = sync_time_Salea_with_TYTO (df_scaled_Salea, y_col = "DC Current (A)",
                                      smooth_window=31, consec=5, k=1)

df_salea_sync = cut_shift_dataframe(df_scaled_Salea, start_Sale_ms)


df_salea_sync["P_AC (W)"], P_3Phase_avg= delta_instantaneous_power(
    df_salea_sync)

df_salea_sync["P_DC (W)"],P_dc_ave = dc_power_inst_ave(df_salea_sync)
# %%

# %%
CHANNELS_TO_PLOT = ["DC Current (A)", "DC Bus (V)",
    "I_a (A)", "V_ab (V)",
    "I_b (A)","V_bc (V)",
    "I_c (A)", "V_ac (V)"]
fig30, axes30 = plot_channels_grid(
    df=df_scaled_Salea,
    channels =  CHANNELS_TO_PLOT,
    title = powertrain,
    ncols = 2,
    time_ms_col = "Time (ms)")
# %%
CHANNELS_TO_PLOT = ["DC Current (A)", "DC Bus (V)",
    "I_a (A)", "V_ab (V)",
    "I_b (A)","V_bc (V)",
    "I_c (A)", "V_ac (V)",
    "P_DC (W)","P_AC (W)"]

fig3, axes3 = plot_channels_grid(
    df=df_salea_sync,
    channels =  CHANNELS_TO_PLOT,
    title = powertrain,
    ncols = 2,
    time_ms_col = "Time (ms)")
# %%
# %%
n_steps = t_start_step
speeds_mean=[]
power_ac_speeds = []
power_dc_speeds = []
for n_step, start_time in enumerate(n_steps):
    time_start_zoom = t_start_step[n_step]
    time_end_zoom = t_end_step[n_step]
     
    delta_t_zoom_ms = time_end_zoom-time_start_zoom
    time_start_zoom = time_start_zoom + delta_t_zoom_ms*0.2
    
    time_end_zoom = time_end_zoom -delta_t_zoom_ms*0.2
    
    ZOOM_MS = (time_start_zoom, time_end_zoom)  # e.g. (0, 200)
    # ZOOM_MS = (time_start_zoom, time_start_zoom+3)  # e.g. (0, 200)
    params_to_mean0 = ["speed"]
    params_to_mean = find_params_in_df(df_TYTO_full_res, params_to_mean0)[0]
    df_speed_TYTO = df_TYTO_sync[params_to_mean]
    

    
    mask_TYTO = (df_speed_TYTO.iloc[:,0]>time_start_zoom) & (df_speed_TYTO.iloc[:,0]<time_end_zoom)
    speed_df_for_mean = df_speed_TYTO[mask_TYTO]
    speed_mean = speed_df_for_mean.iloc[:,1].mean()
    speeds_mean.append(speed_mean)
    


    f_fundamental, T_fundamental_ms = freq_fundamental(speed=speed_mean,
                                                    n_magnet = 10)
    
    df_zoomed_Salea = apply_zoom_ms(df_salea_sync, ZOOM_MS, time_ms_col="Time (ms)")
    
    _ , power_ac_speed= delta_instantaneous_power(df_zoomed_Salea)
    _ , power_dc_speed = dc_power_inst_ave(df_zoomed_Salea)
    power_ac_speeds.append(power_ac_speed)
    power_dc_speeds.append(power_dc_speed)
    
    # fig4, axes4 = plot_channels_grid(
    #     df=df_zoomed_Salea,
    #     channels=CHANNELS_TO_PLOT,
    #     title=f"speed = {speed_mean:.2f}rpm,P_AC_ave = {power_ac_speed:.1f} W, P_DC_ave = {power_dc_speed:.1f} W",
    #     ncols=2,
    #     time_ms_col="Time (ms)")
# %%

df_steps_ave = pd.DataFrame.from_dict({"Speed (rpm)": speeds_mean,
                                       "t_start (ms)": t_start_step,
                                       "t_end (ms)": t_end_step,
                                     "P_DC (W)":  power_dc_speeds,
                                     "P_AC (W)":  power_ac_speeds,
                                     "P_TYTO_electrical (W)": df_TYTO_manual.iloc[1:,7],
                                     "P_mechanical (W)": df_TYTO_manual.iloc[1:,8]})




plt.figure()
for i, v in enumerate(df_steps_ave.columns[3:]):
    plt.plot(df_steps_ave["Speed (rpm)"],df_steps_ave[v], '-o', label = v)
    plt.xlabel("Speed (rpm)")
    plt.ylabel("Power (W)")
    plt.legend()
    plt.grid('both')
# %%
# %%
efficiency = pd.DataFrame.from_dict({"HBC Efficiency %": df_steps_ave["P_AC (W)"]/df_steps_ave["P_DC (W)"]*100,
                                     "Motor Efficiency %": df_steps_ave["P_mechanical (W)"]/df_steps_ave["P_AC (W)"]*100,
                                     "Power train Efficiency %":df_steps_ave["P_mechanical (W)"]/df_steps_ave["P_DC (W)"]*100})

palette = {
    "sky_blue": "#0FAAF0",
    "gray_dark": "#525252ff",
    "teal_dark": "#009494ff",
    "red_bright": "#f74242ff",
    "teal_light": "#00d0b8",
    "lime_green": "#0AFFA0",
    "navy_dark": "#0F3878",
    "blue_medium": "#0f75bcff",
    "cyan_bright": "#29e2ecff",
    "crimson_dark": "#9e0012ff",
    "coral_pink": "#ff596c",
    "taupe": "#95755A",
    "orange_bright": "#f7941dff",
    "peach_orange": "#ffad5aff",
    "gray_medium": "#848484ff"
}
color_cycle = list(palette.values())
plt.figure()
for i, v in enumerate(efficiency.columns):
    plt.plot(df_steps_ave["Speed (rpm)"],efficiency[v], '-o', color = color_cycle[i], label = v)
    plt.xlabel("Speed (rpm)")
    plt.ylabel("Efficiency %")
    plt.legend()
    plt.grid('both')
# %%
    
# %%
n_step =4
time_start_zoom = t_start_step[n_step]
n_periods = 3
t_strat_period = time_start_zoom
t_end_period = time_start_zoom+n_periods*T_fundamental_ms
zoom_perid = [t_strat_period,t_end_period]
df_zoomed_salea_periods = apply_zoom_ms(df_scaled_Salea, zoom_perid, time_ms_col="Time (ms)")

fig6, axes6 = plot_channels_grid(
        df=df_zoomed_salea_periods,
        channels=CHANNELS_TO_PLOT,
        title=f"speed={speeds_mean[n_step]:.0f}rpm,t_fundamental={T_fundamental_ms:.2f}ms,n_period={n_periods}",
        ncols=2,
        time_ms_col="Time (ms)")
# %%

AC_power = df_zoomed_Salea["P_AC (W)"]
DC_power = df_zoomed_Salea["P_DC (W)"]

from scipy.signal import savgol_filter

# choose window ≈ several PWM periods or electrical cycles
window = 1000    # MUST be odd – tune this
poly = 3

AC_power_s = savgol_filter(AC_power, window, poly)
DC_power_s = savgol_filter(DC_power, window, poly)


fig7, axes = plt.subplots(nrows=2,ncols= 2)
axes = axes.ravel()
ax= 0
axes[ax].plot(df_zoomed_Salea["Time (ms)"],AC_power, label = "Power_AC", color = '#ff596c')
axes[ax].plot(df_zoomed_Salea["Time (ms)"],DC_power, label = "Power_DC", color = '#0F3878')
axes[ax].set_xlabel("Time (ms)")
axes[ax].set_ylabel("Power (W)")
axes[ax].grid("True")
axes[ax].legend()

ax= 1
axes[ax].plot(df_zoomed_Salea["Time (ms)"],AC_power_s, label = "Power_AC", color = '#ff596c')
axes[ax].plot(df_zoomed_Salea["Time (ms)"],DC_power_s, label = "Power_DC", color = '#0F3878')
axes[ax].set_xlabel("Time (ms)")
axes[ax].set_ylabel("Power (W)")
axes[ax].grid("True")
axes[ax].legend()

print(f"Mean DC Power (W):{P_dc_ave:.2f}")
print(f"Average AC Power (W): {P_3Phase_avg:.2f}")
print(f"Efficiency{P_3Phase_avg/P_dc_ave:.2f}%")



