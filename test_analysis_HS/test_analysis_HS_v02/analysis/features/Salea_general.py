# -*- coding: utf-8 -*-
"""
Created on Tue Jan 20 14:02:50 2026

@author: kkeramati
"""
from pathlib import Path
import pandas as pd
from matplotlib import pyplot as plt
from utils_io import read_parquet  # noqa
import numpy as np

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

def ensure_channels_exist(df: pd.DataFrame, channels: list[str]):
    missing = [c for c in channels if c not in df.columns]
    if missing:
        raise ValueError(
            "Requested channels are missing:\n"
            + "\n".join(f"  - {m}" for m in missing)
        )
        
def load_prepare_dataframe(
    parquet_path: Path,
    channel_name_map  = {
        3: "DC Current (A)",
        4: "DC Bus (V)",
        2: "I_a (A)",
        6: "V_ab (V)",
        1: "I_b (A)",
        7: "V_bc (V)",
        0: "I_c (A)",
        5: "V_ac (V)",
    }
):
   
    df = read_parquet(parquet_path)

    # Original time column
    time_col = df.columns[0]
    df[time_col] = pd.to_datetime(df[time_col], utc=True, errors="coerce")
    df = df.dropna(subset=[time_col]).reset_index(drop=True)

    # Rename signal channels
    df = rename_channels_by_index(df, channel_name_map)

    # Convert time to milliseconds (relative)
    t0 = df[time_col].iloc[0]
    time_ms = (df[time_col] - t0).dt.total_seconds() * 1000.0
    df = df.assign(**{"Time (ms)": time_ms})
    df = df.drop(columns=[time_col])

    # ---- Sampling rate computation ----
    dt_ms = np.diff(time_ms.values) 

    # Use median for robustness against jitter
    dt_ms_med = np.median(dt_ms)

    fs = 1.0 / (dt_ms_med * 1e-3)  # Hz

    return df, fs
def apply_scaling_per_column(
    df: pd.DataFrame,
    scale_map=  {
        "DC Current (A)": -10,
        "I_a (A)": 10,
        "I_b (A)": 10,
        "I_c (A)": 10,
        "DC Bus (V)": 10,
        "V_ab (V)": 10,
        "V_bc (V)": 10,
        "V_ac (V)": 10,
    },
    default_scale: float | None = None,
) -> pd.DataFrame:
    out = df.copy()

    for col in out.columns:


        # force numeric (non-numeric -> NaN)
        out[col] = pd.to_numeric(out[col], errors="coerce")

        if col in scale_map:
            out[col] = out[col] * float(scale_map[col])
        elif default_scale is not None:
            out[col] = out[col] * float(default_scale)

    return out
def apply_zoom_ms(
    df: pd.DataFrame,
    zoom_ms: tuple[float, float] | None,
    time_ms_col: str = "Time (ms)",
) -> pd.DataFrame:
    df.copy()
    """
    Return a zoomed view of df based on a [tmin, tmax] window in milliseconds.
    If zoom_ms is None, returns df unchanged.
    """
    if zoom_ms is None:
        return df

    tmin, tmax = zoom_ms
    return df[(df[time_ms_col] >= tmin) & (df[time_ms_col] <= tmax)]

def plot_channels_grid(
    df: pd.DataFrame,
    channels: list[str],
    title: str,
    ncols: int = 2,
    time_ms_col: str = "Time [ms]",
):

    plt.rcParams["font.family"] = "DejaVu Sans"

    ensure_channels_exist(df, channels)

    n = len(channels)
    nrows = (n + ncols - 1) // ncols

    fig, axes = plt.subplots(
        nrows=nrows,
        ncols=ncols,
        figsize=(12, 2.0 * nrows),
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
    return fig, axes



def plot_channels_grid_multi(
    dfs: list[pd.DataFrame],
    channels: list[str],
    title: str,
    ncols: int = 2,
    time_ms_col: str = "Time [ms]",
    labels: list[str] | None = None,
):
    """
    Plot the same channels from multiple DataFrames on the same grid of subplots.

    Assumes all dfs contain `time_ms_col` and all `channels`.
    """

    plt.rcParams["font.family"] = "DejaVu Sans"

    if not isinstance(dfs, (list, tuple)) or len(dfs) == 0:
        raise ValueError("dfs must be a non-empty list of DataFrames.")

    # default legend labels
    if labels is None:
        labels = [f"df {i}" for i in range(len(dfs))]
    if len(labels) != len(dfs):
        raise ValueError("labels length must match dfs length.")

    # sanity checks
    for idx, df in enumerate(dfs):
        if time_ms_col not in df.columns:
            raise KeyError(f"'{time_ms_col}' not found in dfs[{idx}].columns")
        missing = [ch for ch in channels if ch not in df.columns]
        if missing:
            raise KeyError(f"Missing channels in dfs[{idx}]: {missing}")

    n = len(channels)
    nrows = (n + ncols - 1) // ncols

    fig, axes = plt.subplots(
        nrows=nrows,
        ncols=ncols,
        figsize=(12, 2.0 * nrows),
        sharex=True
    )
    axes = axes.ravel() if hasattr(axes, "ravel") else [axes]

    # your palette (reused)
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

    # Different linestyles per DataFrame (helps if curves overlap)
    linestyles = ["-", "--", ":", "-."] * 10

    for i, ch in enumerate(channels):
        ax = axes[i]
        row_idx = i // ncols
        color = color_cycle[row_idx % len(color_cycle)]

        for k, df in enumerate(dfs):
            ax.plot(
                df[time_ms_col],
                df[ch],
                linewidth=1.8,
                color=color,
                linestyle=linestyles[k],
                alpha=0.9,
                label=labels[k],
            )

        ax.set_xlabel("Time [ms]")
        ax.set_ylabel(ch)
        ax.grid(True, alpha=0.25)

        # show legend only once per axis if multiple dfs
        if len(dfs) > 1:
            ax.legend(fontsize=8)

    for j in range(n, len(axes)):
        axes[j].axis("off")

    fig.suptitle(title)
    plt.tight_layout()
    return fig, axes


