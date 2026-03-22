# -*- coding: utf-8 -*-
"""
Created on Thu Jan 15 14:49:20 2026

@author: kkeramati

Exploratory plotting for Parquet analog data (pandas)

Selection modes:
- SELECTED_FILES = ["run_001.parquet", "run_002.parquet"]
- SELECTED_FILES = "ALL"

What you asked for in this version:
- NO channel colors in the plot function (matplotlib default cycle)
- Forget "channel_layout" pairs; instead plot an ORDERED list of channels
- Scaling is done in a SEPARATE function, with DIFFERENT scale per column
- Rename channels BEFORE scaling/plotting
- Time converted to ms from start (x-axis)
"""

from pathlib import Path
import sys
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle


# ---------------------------------------------------------------------
# Plot styling (kept font only; no custom colors)
# ---------------------------------------------------------------------
plt.rcParams["font.family"] = "Century Gothic"
plt.rcParams["axes.titlesize"] = 11
plt.rcParams["axes.labelsize"] = 10
plt.rcParams["xtick.labelsize"] = 9
plt.rcParams["ytick.labelsize"] = 9
plt.rcParams["legend.fontsize"] = 9
plt.rcParams["figure.titlesize"] = 14


# ---------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))
print(PROJECT_ROOT)

from utils_io import read_parquet  # noqa
from analysis.features.power_delta import delta_instantaneous_power
from analysis.features.power_dc import add_dc_power_column, dc_power_mean
from analysis.features.fft import fft_single_channel, dominant_frequency
from analysis.features.fft import fft_multi_channels, dominant_frequencies


PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------
def resolve_selected_files(processed_dir: Path, selection):
    if selection == "ALL":
        files = sorted(processed_dir.glob("*.parquet"))
        if not files:
            raise FileNotFoundError(f"No Parquet files found in {processed_dir}")
        return files

    if isinstance(selection, list):
        paths = []
        missing = []
        for name in selection:
            p = processed_dir / name
            if p.exists():
                paths.append(p)
            else:
                missing.append(name)

        if missing:
            raise FileNotFoundError(
                "Missing parquet files:\n" + "\n".join(f"  - {m}" for m in missing)
            )
        return paths

    raise TypeError("SELECTED_FILES must be either 'ALL' or a list of parquet filenames.")


def rename_channels_by_index(df: pd.DataFrame, name_map: dict[int, str]) -> pd.DataFrame:
    """Rename signal columns by their positional index (excluding time column)."""
    time_col = df.columns[0]
    signal_cols = list(df.columns[1:])
    rename_dict = {signal_cols[i]: n for i, n in name_map.items() if i < len(signal_cols)}
    out = df.rename(columns=rename_dict)
    return out[[time_col] + [c for c in out.columns if c != time_col]]





def apply_scaling_per_column(
    df: pd.DataFrame,
    time_col: str,
    scale_map: dict[str, float],
    default_scale: float | None = None,
    time_ms_col: str = "Time [ms]",
) -> pd.DataFrame:
    out = df.copy()

    for col in out.columns:
        if col in (time_col, time_ms_col):
            continue

        # force numeric (non-numeric -> NaN)
        out[col] = pd.to_numeric(out[col], errors="coerce")

        if col in scale_map:
            out[col] = out[col] * float(scale_map[col])
        elif default_scale is not None:
            out[col] = out[col] * float(default_scale)

    return out


def ensure_channels_exist(df: pd.DataFrame, channels: list[str]):
    missing = [c for c in channels if c not in df.columns]
    if missing:
        raise ValueError(
            "Requested channels are missing:\n"
            + "\n".join(f"  - {m}" for m in missing)
        )
def apply_zoom_ms(
    df: pd.DataFrame,
    zoom_ms: tuple[float, float] | None,
    time_ms_col: str = "Time [ms]",
) -> pd.DataFrame:
    """
    Return a zoomed view of df based on a [tmin, tmax] window in milliseconds.
    If zoom_ms is None, returns df unchanged.
    """
    if zoom_ms is None:
        return df

    tmin, tmax = zoom_ms
    return df[(df[time_ms_col] >= tmin) & (df[time_ms_col] <= tmax)]




def load_prepare_dataframe(
    parquet_path: Path,
    channel_name_map: dict[int, str],
    time_ms_col: str = "Time [ms]",
) -> tuple[pd.DataFrame, str]:
    """
    Load parquet, parse time, rename channels,
    and ADD a Time [ms] column to the DataFrame.

    Returns
    -------
    df : pd.DataFrame
        DataFrame with time column and 'Time [ms]' column
    time_col : str
        Name of the original time column
    """
    df = read_parquet(parquet_path)

    time_col = df.columns[0]
    df[time_col] = pd.to_datetime(df[time_col], utc=True, errors="coerce")
    df = df.dropna(subset=[time_col]).reset_index(drop=True)

    # Rename signal channels
    df = rename_channels_by_index(df, channel_name_map)

    # Add time in ms as a NEW column
    t0 = df[time_col].iloc[0]
    df[time_ms_col] = (df[time_col] - t0).dt.total_seconds() * 1000.0

    return df, time_col

def plot_channels_grid(
    df: pd.DataFrame,
    channels: list[str],
    title: str,
    ncols: int = 2,
    time_ms_col: str = "Time [ms]",
):
    ensure_channels_exist(df, channels)

    n = len(channels)
    nrows = (n + ncols - 1) // ncols

    fig, axes = plt.subplots(
        nrows=nrows,
        ncols=ncols,
        figsize=(12, 3.0 * nrows),
        sharex=True
    )
    axes = axes.ravel() if hasattr(axes, "ravel") else [axes]

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
    color_cycle = list(palette.values())

    for i, ch in enumerate(channels):
        ax = axes[i]
        row_idx = i // ncols
        color = color_cycle[row_idx % len(color_cycle)]

        ax.plot(df[time_ms_col], df[ch], linewidth=1.8, color=color)
        # ax.set_title(ch)
        ax.set_xlabel("Time [ms]")
        ax.set_ylabel(ch)
        ax.grid(True, alpha=0.25)

    for j in range(n, len(axes)):
        axes[j].axis("off")

    fig.suptitle(title)
    plt.tight_layout()
    plt.show()



# ---------------------------------------------------------------------
# __main__
# ---------------------------------------------------------------------
if __name__ == "__main__":
    # Choose files
    SELECTED_FILES = ["Pulsar_phaseStudy_10krpm_triger.parquet"]
    files = resolve_selected_files(PROCESSED_DIR, SELECTED_FILES)

    # Rename mapping (index-based after time column)
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

    # Plot order (no layout pairs; just the order you want)
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

    # Per-column scaling (different numbers for different columns)
    # Example: scale currents by 10, voltages by 1 (change as you like)
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
    DEFAULT_SCALE = None  # set to e.g. 1.0 if you want all other channels scaled too

    # Zoom window in ms (None = full)
    ZOOM_MS = (10002,10003.3)  # e.g. (0, 200)
    df_new = []
    df_P = []
    P_avg_all = []
    for i,f in enumerate(files):
        df, time_col = load_prepare_dataframe(f, channel_name_map)

        df_scaled = apply_scaling_per_column(
            df,
            time_col=time_col,
            scale_map=SCALE_MAP,
            default_scale=DEFAULT_SCALE,
        )
        
        df_zoomed = apply_zoom_ms(df_scaled, ZOOM_MS, time_ms_col="Time [ms]")
        df_new.append(df_zoomed)
    

        plot_channels_grid(
            df=df_zoomed,
            channels=CHANNELS_TO_PLOT,
            title=f.stem,
            ncols=2,
            time_ms_col="Time [ms]",
        )


        df_zoomed["P (W)"], P_avg= delta_instantaneous_power(
            df_zoomed,
            v_cols=("V_a (V)", "V_b (V)", "V_c (V)"),
            i_cols=("I_a (A)", "I_b (A)", "I_c (A)"),
        )
        df_zoomed = add_dc_power_column(df_zoomed)

        
        df_P.append(df_zoomed)
        
 
        P_avg_all.append(P_avg)
        
        print("Mean DC Power (W):", dc_power_mean(df_zoomed))
        print(f"Average electrical power: {P_avg:.2f} W")

        
        
        plot_channels_grid(
            df=df_zoomed,
            channels=["P (W)", "DC Power (W)"],
            title=f.stem,
            ncols=1,
            time_ms_col="Time [ms]",
        )
        
        phase_currents = ["I_a (A)", "I_b (A)", "I_c (A)"]
        # phase_currents = ["I_a (A)"]

        spectra = fft_multi_channels(
        df_zoomed,
        signal_cols=phase_currents,
        time_ms_col="Time [ms]",
        window="hann",
        detrend=True,
        normalize=True,
        )
        dom = dominant_frequencies(spectra, fmin=1.0, fmax=2000.0)
        print("\nDominant frequencies (Hz):")
        print(dom)

        channels = ["I_a (A)"]
        fig, axes = plt.subplots(1, 2, figsize=(10, 5))
        axes = axes.ravel()
        
        titles = [
            "FFT – Phase Currents (Full Spectrum)",
            "FFT – Phase Currents (<50 kHz)"
        ]
        masks = [
            lambda s: s,
            lambda s: s[s["frequency_hz"] < 50_000]
        ]
        markers = [None, 'o']  # different marker per subplot
        
        for i, (ax, title, mask, marker) in enumerate(zip(axes, titles, masks, markers)):
            for ch in channels:
                spec = spectra[ch]
                data = mask(spec)
        
                ax.plot(
                    data["frequency_hz"],
                    data["magnitude"],
                    linestyle='-',
                    marker=marker,
                    label=ch
                )
        
            # 🔲 Rectangle on first subplot
            if i == 0:
                ymin, ymax = ax.get_ylim()
                ax.add_patch(
                    Rectangle(
                        (0, ymin),
                        50_000,
                        ymax - ymin,
                        fill=False,
                        linestyle="--",
                        linewidth=1.5,
                        alpha=0.8
                    )
                )
        
            ax.set(xlabel="Frequency [Hz]", ylabel="Magnitude", title=title)
            ax.grid(True, alpha=0.3)
            ax.legend()

        
        phase_Vs = ["V_a (V)", "V_b (V)", "V_c (V)"]
        # phase_Vs = ["V_a (V)"]

        spectra = fft_multi_channels(
        df_zoomed,
        signal_cols=phase_Vs,
        time_ms_col="Time [ms]",
        window="hann",
        detrend=True,
        normalize=True,
        )
        dom = dominant_frequencies(spectra, fmin=1.0, fmax=2000.0)
        print("\nDominant frequencies (Hz):")
        print(dom)
        
        channels = ["V_a (V)"]
        fig, axes = plt.subplots(1, 2, figsize=(10, 5))
        axes = axes.ravel()
        
        titles = [
            "FFT – Phase Voltage (Full Spectrum)",
            "FFT – Phase Voltage (<50 kHz)"
        ]
        masks = [
            lambda s: s,
            lambda s: s[s["frequency_hz"] < 50_000]
        ]
        markers = [None, 'o']  # different marker per subplot
        
        for i, (ax, title, mask, marker) in enumerate(zip(axes, titles, masks, markers)):
            for ch in channels:
                spec = spectra[ch]
                data = mask(spec)
        
                ax.plot(
                    data["frequency_hz"],
                    data["magnitude"],
                    linestyle='-',
                    marker=marker,
                    label=ch
                )
        
            # 🔲 Rectangle on first subplot
            if i == 0:
                ymin, ymax = ax.get_ylim()
                ax.add_patch(
                    Rectangle(
                        (0, ymin),
                        50_000,
                        ymax - ymin,
                        fill=False,
                        linestyle="--",
                        linewidth=1.5,
                        alpha=0.8
                    )
                )
        
            ax.set(xlabel="Frequency [Hz]", ylabel="Magnitude", title=title)
            ax.grid(True, alpha=0.3)
            ax.legend()
        
       
        
        
        

