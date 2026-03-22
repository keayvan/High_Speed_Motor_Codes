# -*- coding: utf-8 -*-
"""
Created on Sun Feb  1 18:01:40 2026

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
import matplotlib.pyplot as plt

from analysis.features.TYTO_general import read_result 
from analysis.features.TYTO_full_res import plot_fullRes, param_resolution, sampling_rate_TYTO
from analysis.features.TYTO_general import trim_after_trigger 
from analysis.features.TYTO_general import parms_to_mean 
from analysis.features.TYTO_general import freq_fundamental 
from analysis.features.Salea_general import resolve_selected_files

from analysis.features.Salea_general import load_prepare_dataframe
from analysis.features.Salea_general import plot_channels_grid
from analysis.features.Salea_general import apply_scaling_per_column
from analysis.features.Salea_general import apply_zoom_ms
from analysis.features.fft import fft_multi_channels, find_FFT_peaks, add_side_table_from_arrays, add_table_top_right




PROCESSED_DIR_TYTO = PROJECT_ROOT / "data" / "raw" / "TYTO"
PROCESSED_DIR_Salea = PROJECT_ROOT / "data" / "processed" 
SAVING_folder = PROJECT_ROOT / "data" / "post_proccessings"
speed = "14krpm"
freq= "20KHz"
resampling = "fullRes"

TYTO_FILES = f"ARC_SwitchingFrequency{freq}_{speed}_{resampling}"
TYTO_csv = TYTO_FILES+".csv"
time_format = "ms"
powertrain = "ARC_DC"
df_TYTO = read_result(PROCESSED_DIR_TYTO / TYTO_csv,
                 powertrain = powertrain,
                 Time = time_format)


# fig1,_=plot_fullRes(df_TYTO_res,
#                  params=all,
#                  n_rows=4,
#                  time_format = time_format)


zoom_TYTO = [6000, 8000]       
params_mean_TYTO, values_mean_TYTO = parms_to_mean(df_TYTO,
                               parm_for_find=['speed', "Fz", "MZ"],
                               s_win_ms = zoom_TYTO[0],
                               e_win_ms = zoom_TYTO[1])
df_TYTO_res = param_resolution(df_TYTO,
                          time_format = time_format)
speed_mean = values_mean_TYTO[0]
f_fundamental, T_fundamental_ms = freq_fundamental(speed_mean,
                                                n_magnet = 10)
print(f'Speed = {speed_mean}rpm')
print(f'f_period = {f_fundamental}KHz')
print(f't_period = {T_fundamental_ms}ms')

Salea_file = [f"ARC_SwitchingFrequency{freq}_{speed}.parquet"]
files_salea = resolve_selected_files(PROCESSED_DIR_Salea, Salea_file)

df_Salea_s = files_salea[0]

channel_name_map = {
    3: "DC Current (A)",
    4: "DC Bus (V)",
    2: "I_a (A)",
    6: "V_a (V)",
    1: "I_b (A)",
    7: "V_b (V)",
    0: "I_c (A)",
    5: "V_c (V)",
}

CHANNELS_TO_PLOT = [
    "DC Current (A)",
    "DC Bus (V)",
    "I_a (A)",
    "V_a (V)",
    "I_b (A)",
    "V_b (V)",
    "I_c (A)",
    "V_c (V)",
]


SCALE_MAP = {
    "DC Current (A)": -10,
    "I_a (A)": -10,
    "I_b (A)": -10,
    "I_c (A)": -10,
    "DC Bus (V)": 10,
    "V_a (V)": 10,
    "V_b (V)": 10,
    "V_c (V)": 10,
}

DEFAULT_SCALE = None
ZOOM_MS = None
df_Salea,fs = load_prepare_dataframe(df_Salea_s,
                                              channel_name_map)

print(f"Sampling rate = {fs:.0f} Hz")
df_scaled_Salea = apply_scaling_per_column(
    df_Salea,
    scale_map=SCALE_MAP,
)

n_periods = 3
zoom_Salea = [6000,6000+T_fundamental_ms*n_periods]
df_zoomed_Salea = apply_zoom_ms(
    df = df_scaled_Salea,
    zoom_ms= zoom_Salea,
    time_ms_col = "Time (ms)"
) 

spectra = fft_multi_channels(df_zoomed_Salea,
    signal_cols=CHANNELS_TO_PLOT,
    time_ms_col="Time (ms)",
    window="hann",
    detrend=True,
    normalize=True,
    )




    
# peaks_df, fundamentals_df = find_FFT_peaks(
#     x,
#     n_fundamentals=12,
#     harmonic_tol_hz=1.0,      # tolerant matching
#     min_freq=1.0,
#     max_freq=50000
# )
palette = {
    "red_bright": "#f74242ff",
    "teal_dark": "#009494ff",
    "navy_dark": "#0F3878",
    "lime_green": "#0AFFA0",
    "taupe": "#95755A",
    "teal_light": "#00d0b8",
    "blue_medium": "#0f75bcff",
    "sky_blue": "#0FAAF0",
    "cyan_bright": "#29e2ecff",
    "crimson_dark": "#9e0012ff",
    "coral_pink": "#ff596c",
    "orange_bright": "#f7941dff",
    "peach_orange": "#ffad5aff",
    "gray_dark": "#525252ff",
    "gray_medium": "#848484ff"
}
color_cycle = list(palette.values())
salea_whole_domain = ["DC Current (A)", "DC Bus (V)"]
axes_no_salea_whole_domain = [1, 2]


fig5, axes = plt.subplots(nrows=2, ncols=3,figsize = (20,10))
axes = axes.ravel () if hasattr(axes, 'ravel') else axes

fig5.subplots_adjust(hspace=0.6, wspace=0.3)
for i,v in enumerate(salea_whole_domain):
        x_whole_salea= df_scaled_Salea["Time (ms)"]
        y_whole_salea = df_scaled_Salea[v]
        axes[axes_no_salea_whole_domain[i]].plot(x_whole_salea, y_whole_salea, label = v, color= color_cycle[0])
        axes[axes_no_salea_whole_domain[i]].axvline(zoom_Salea[0], linestyle='--', alpha=0.7)
        axes[axes_no_salea_whole_domain[i]].axvline(zoom_Salea[1], linestyle='--', alpha=0.7)
        axes[axes_no_salea_whole_domain[i]].set_xlabel("Time (ms)")
        axes[axes_no_salea_whole_domain[i]].set_ylabel(v)
        axes[axes_no_salea_whole_domain[i]].grid(True, alpha=0.75)
        axes[axes_no_salea_whole_domain[i]].set_title(f"n_period:{n_periods}|*|t = {zoom_Salea[1]-zoom_Salea[0]:.3f}ms")

pars_TYTO_fullres_labels = ["current", "voltage"]
tiles_TYTO_plots = ["current", "voltage"]

axes_no_TYTO = [0 , 3]

for i, v in enumerate(list(df_TYTO_res.keys())):
    for j, w in enumerate(pars_TYTO_fullres_labels):
        if w in v:
            x_TYTO = df_TYTO_res[v].iloc[:,0]
            y_TYTO = df_TYTO_res[v].iloc[:,1]
            fs_hz, dt_ms = sampling_rate_TYTO(x_TYTO)
            axes[axes_no_TYTO[j]].plot(x_TYTO, y_TYTO, color = "#0F3878", lw = 1)
            axes[axes_no_TYTO[j]].axvline(zoom_TYTO[0], linestyle='--', alpha=0.7)
            axes[axes_no_TYTO[j]].axvline(zoom_TYTO[1], linestyle='--', alpha=0.7)

            axes[axes_no_TYTO[j]].set_xlabel("Time (ms)")
            axes[axes_no_TYTO[j]].set_ylabel(v)
            axes[axes_no_TYTO[j]].set_title(tiles_TYTO_plots[j] + f"|*|sampling:{fs_hz:.1f}Hz")
            axes[axes_no_TYTO[j]].grid(True, alpha=0.75, zorder = 0)
            
pars_fft_labels = ["DC Current (A)", "DC Bus (V)"]
axes_no_fft = [4, 5]

for k, w in enumerate (pars_fft_labels):
    fft_signal = spectra[w]
    mask = fft_signal[fft_signal.columns[0]] <100000
    fft_signal = fft_signal[mask]
    peaks_df, fundamentals_df = find_FFT_peaks(
        fft_signal,
        n_fundamentals=12,
        harmonic_tol_hz=1.0,      # tolerant matching
        min_freq=1.0,
        max_freq=50000
    )

    x_fft = fft_signal["frequency_hz"]
    y_fft = fft_signal["magnitude"]
    axes[axes_no_fft[k]].plot(x_fft, y_fft, color = color_cycle[0])
    axes[axes_no_fft[k]].plot(peaks_df,fundamentals_df, 'o', color = color_cycle[-2], ms = 1)

    axes[axes_no_fft[k]].set_xlabel("frequency_hz")
    axes[axes_no_fft[k]].set_ylabel("magnitude")
    axes[axes_no_fft[k]].set_title (f"FFT_{w}")
    axes[axes_no_fft[k]].grid(True, alpha=0.75, zorder = 0)

    add_table_top_right( axes[axes_no_fft[k]],
     freqs= peaks_df,
     mags= fundamentals_df,
     n=None,
     freq_fmt="{:.1f}",
     mag_fmt="{:.3g}",
     title="Points",
     fontsize=5,
     table_width=0.20,     # fraction of axes width
     table_height=0.8,    # fraction of axes height
 )