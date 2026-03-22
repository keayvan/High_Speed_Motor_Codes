# -*- coding: utf-8 -*-
"""
Created on Wed Jan 28 10:55:04 2026

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
powertrain = "ARC"
study_name = "study_frequency"
freq= "20kHz"
speed = "steps_01"
resampling = "fullRes"
# resampling = "resample100ms"

TYTO_FILES = f"{powertrain}_{study_name}{freq}_{speed}_{resampling}"
TYTO_csv = TYTO_FILES+".csv"
time_format = "ms"
df_TYTO = read_result(PROCESSED_DIR_TYTO / TYTO_csv,
                 powertrain = powertrain,
                 Time = time_format)
 
# df_TYTO_trim, info = trim_after_trigger(
#     df_TYTO,
#     time_col = f'Time ({time_format})',
#     signal_col=f"{powertrain} current (A)",
#     trigger_duration_s=10,
#     fill_method="ffill",     # try "interpolate" if you prefer smoother values
#     # resample_hz=1000,       # optional: get a uniform time base
# )

df_TYTO_res = param_resolution(df_TYTO,
                          time_format = time_format)
# fig1,_=plot_fullRes(df_TYTO_res,
#                  params=all,
#                  n_rows=4,
#                  time_format = time_format)


zoom_TYTO = [13000, 14000]       
params_mean_TYTO, values_mean_TYTO = parms_to_mean(df_TYTO,
                               parm_for_find=['speed', "Fz", "MZ"],
                               s_win_ms = zoom_TYTO[0],
                               e_win_ms = zoom_TYTO[1])
speed_mean = values_mean_TYTO[0]
f_fundamental, T_fundamental_ms = freq_fundamental(speed_mean,
                                                n_magnet = 10)
print(f'Speed = {speed_mean}rpm')
print(f'f_period = {f_fundamental}KHz')
print(f't_period = {T_fundamental_ms}ms')


Salea_file = [f"{powertrain}_{study_name}{freq}_{speed}.parquet"]
files_salea = resolve_selected_files(PROCESSED_DIR_Salea, Salea_file)

df_Salea_s = files_salea[0]

channel_name_map = {
    3: "DC Current (A)",
    4: "DC Bus (V)",
    2: "I_a (A)",
    6: "V_ab (V)",
    1: "I_b (A)",
    7: "V_bc (V)",
    0: "I_c (A)",
    5: "V_ac (V)",
}

CHANNELS_TO_PLOT = [
    "DC Current (A)",
    "DC Bus (V)",
    "I_a (A)",
    "V_ab (V)",
    "I_b (A)",
    "V_bc (V)",
    "I_c (A)",
    "V_ac (V)",
]


SCALE_MAP = {
    "DC Current (A)": -10,
    "I_a (A)": -10,
    "I_b (A)": -10,
    "I_c (A)": -10,
    "DC Bus (V)": 10,
    "V_ab (V)": 10,
    "V_bc (V)": 10,
    "V_ac (V)": 10,
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

# fig2 = plot_channels_grid(
#     df=df_scaled_Salea,
#     channels=CHANNELS_TO_PLOT,
#     title=df_Salea_s.stem,
#     ncols=2,
#     time_ms_col="Time (ms)",
# )

n_periods = 2
zoom_Salea = [13000,13000+T_fundamental_ms*n_periods]
df_zoomed_Salea = apply_zoom_ms(
    df = df_scaled_Salea,
    zoom_ms= zoom_Salea,
    time_ms_col = "Time (ms)"
) 



# fig3 = plot_channels_grid(
#     df=df_zoomed_Salea,
#     channels=CHANNELS_TO_PLOT,
#     title=df_Salea_s.stem,
#     ncols=2,
#     time_ms_col="Time (ms)",
# )

spectra = fft_multi_channels(df_zoomed_Salea,
    signal_cols=CHANNELS_TO_PLOT,
    time_ms_col="Time (ms)",
    window="hann",
    detrend=True,
    normalize=True,
    )

x = spectra[CHANNELS_TO_PLOT[2]]
mask = x[x.columns[0]] <50000
x = x[mask]


    
peaks_df, fundamentals_df = find_FFT_peaks(
    x,
    n_fundamentals=12,
    harmonic_tol_hz=1.0,      # tolerant matching
    min_freq=1.0,
    max_freq=50000
)

# fig4,ax = plt.subplots()

# ax.plot(x.iloc[:,0],x.iloc[:,1])
# ax.plot(peaks_df,fundamentals_df, 'o', color = 'red')
# ax.grid('both')
# ax.set_xlabel ("Frequency_hz")
# ax.set_ylabel ("Magnetude")

# add_side_table_from_arrays(ax, peaks_df, fundamentals_df,title = f'@Speed = {speed_mean:.2f} rpm & Fundamental_TYTO = {f_fundamental:.2f}')
# plt.show()

salea_whole_domain = ["I_a (A)", "V_ab (V)"]
axes_no_salea_whole_domain = [1, 2]

I_to_plot = ["I_a (A)", "I_b (A)", "I_c (A)"]

V_to_plot  = [ "V_ab (V)", "V_bc (V)", "V_ac (V)"]


pars_signal_plots = [I_to_plot, V_to_plot]
pars_salea_labels = ["3 Phase Curernt", "3 Phase Voltage"]
axes_no_sela = [4, 5]

pars_fft_labels = ["I_a (A)","V_ab (V)" ]
axes_no_fft = [7, 8]
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
plt.rcParams["font.family"] = "DejaVu Sans"

fig5, axes = plt.subplots(nrows=3, ncols=3,figsize = (20,10))
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

    


for i, u in enumerate (pars_salea_labels):
    for j, v in enumerate(pars_signal_plots[i]):
        x_salea = df_zoomed_Salea["Time (ms)"]
        y_salea= df_zoomed_Salea[v]
        axes[axes_no_sela[i]].plot(x_salea, y_salea, label = v, color= color_cycle[j])
        axes[axes_no_sela[i]].set_xlabel("Time (ms)")
        # axes[axes_no_sela[i]].set_ylabel(v)

        axes[axes_no_sela[i]].legend()
    axes[axes_no_sela[i]].set_title(u+f'|*| sampling: {fs:.0f} Hz')
    axes[axes_no_sela[i]].grid(True, alpha=0.75)


    
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
axes_no_TYTO = [0 , 3, 6]
pars_TYTO_fullres_labels = ["speed", "Fz", "MZ"]
tiles_TYTO_plots= [f"s: {values_mean_TYTO[0]:.1f}rpm|*|f_fund:{f_fundamental:.1f}Hz|*|T_fund:{T_fundamental_ms:.1f}ms",
                   f"Thrust_mean = {values_mean_TYTO[1]}kgf",
                   f"Torque = {values_mean_TYTO[2]}N.m"]
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

list_all_plot = axes_no_TYTO + axes_no_sela + axes_no_fft + axes_no_salea_whole_domain
empty_ax = [x for x in  list(range(len(axes))) if x not in list_all_plot]

for i, v in enumerate(empty_ax):
    fig5.delaxes(axes[v])

fig_file = TYTO_FILES+'.png'
fig5.savefig(SAVING_folder / fig_file , dpi=600) 