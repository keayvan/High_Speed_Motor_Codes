# -*- coding: utf-8 -*-
"""
Created on Tue Dec 16 16:14:20 2025

@author: kkeramati
"""
import math
import h5py
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os
from scipy.integrate import cumulative_trapezoid

def mat_v73_to_dataframe(mat_path, signals, time_key="time", value_key="value"):

    """
    Build a pandas DataFrame from a MATLAB v7.3 HDF5 .mat file.

    Parameters
    ----------
    mat_path : str
        Path to .mat file
    signals : list[str]
        Group names (e.g. ["B_volt", "B_amp", "TAS_a"])
    time_key : str
        Dataset name for time inside each group
    value_key : str
        Dataset name for value inside each group

    Returns
    -------
    df : pandas.DataFrame
        Index = time (float)
        Columns = signal names
    """

    data = {}

    with h5py.File(mat_path, "r") as f:
        time_ref = None

        for sig in signals:
            t_path = f"{sig}/{time_key}"
            v_path = f"{sig}/{value_key}"

            if t_path not in f or v_path not in f:
                raise KeyError(f"Missing '{t_path}' or '{v_path}'")

            t = np.squeeze(np.array(f[t_path])).astype(float)
            v = np.squeeze(np.array(f[v_path])).astype(float)

            if t.ndim != 1 or v.ndim != 1:
                raise ValueError(f"{sig}: time/value not 1D")

            # Remove NaNs / infs
            mask = np.isfinite(t) & np.isfinite(v)
            t = t[mask]
            v = v[mask]

            # Use first signal's time as reference index
            if time_ref is None:
                time_ref = t
                data["time"] = t

            # Align lengths (defensive)
            n = min(len(time_ref), len(v))
            data[sig] = v[:n]

    df = pd.DataFrame(data).set_index("time")
    return df

def load_many_mats_to_dfs(mat_paths, signals):
    """Return list of (label, df) for each mat file."""
    out = []
    for p in mat_paths:
        df = mat_v73_to_dataframe(p, signals=signals)
        label = os.path.splitext(os.path.basename(p))[0]
        out.append((label, df))
    return out


def plot_from_dataframe(
    df,
    subplot_params,
    overlay_params,
    xAxis = None,
    n_cols=3,
    axvline = None
):
    palette = {
        "navy_dark": "#0F3878",
        "teal_dark": "#009494ff",
        "teal_light": "#00d0b8",
        "lime_green": "#0AFFA0",
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
        "gray_medium": "#848484ff",
    }
    colors = list(palette.values())

    # ---------- Figure 1: subplots ----------
    
    
    if subplot_params !=None:
        n_plots = len(subplot_params)
        n_rows = math.ceil(n_plots / n_cols)

        fig1, axes = plt.subplots(
            n_rows,
            n_cols,
            figsize=(5 * n_cols, 3.2 * n_rows),
            sharex=True
        )
        axes = axes.flatten()
        if xAxis == None:
            xx = df.index/1e9
        else:
            xx = df[xAxis]
        for i, col in enumerate(subplot_params):
            if col not in df.columns:
                raise KeyError(f"'{col}' not in DataFrame")
    
            axes[i].plot(
                xx,
                df[col],
                color=colors[i % len(colors)],
                linewidth=1.8
            )
            if axvline:
                axes[i].axvline(x=axvline, color = 'red',ls = '--',  label = f'T = {axvline}')

            axes[i].set_title(col)
            axes[i].set_xlabel("time (s)")
            axes[i].grid(True, alpha=0.25)
    
        for j in range(i + 1, len(axes)):
            axes[j].axis("off")
    
        
        fig1.suptitle("Selected Parameters", y=0.98)
        fig1.tight_layout()
        plt.show()

    # ---------- Figure 2: overlay ----------
    if overlay_params !=None:
        n_plots = len(overlay_params)

        plt.figure(figsize=(12, 5))
    
        for i, col in enumerate(overlay_params):
            if col not in df.columns:
                raise KeyError(f"'{col}' not in DataFrame")
    
            plt.plot(
                df.index,
                df[col],
                label=col,
                color=colors[(i + n_plots) % len(colors)],
                linewidth=1.8
            )

    
        plt.xlabel("time")
        plt.ylabel("value")
        plt.title("Other Selected Parameters")
        plt.grid(True, alpha=0.25)
        plt.legend(ncol=2, frameon=False)
        plt.tight_layout()
        plt.show()

def plot_many_runs_from_dfs(
    dfs,               # list of (run_label, df)
    subplot_params,
    overlay_params,
    xAxis = None,
    n_cols=3
):
    palette = {
        "navy_dark": "#0F3878",
        "teal_dark": "#009494ff",
        "teal_light": "#00d0b8",
        "lime_green": "#0AFFA0",
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
        "gray_medium": "#848484ff",
    }
    run_colors = list(palette.values())
    run_linestyles = ["-", "-", ":", "-."]  # optional, cycles if many signals

    # Map each run to ONE color
    run_color_map = {
        run_label: run_colors[i % len(run_colors)]
        for i, (run_label, _) in enumerate(dfs)
    }
    if subplot_params !=None:

        # ---------- Figure 1: subplots ----------
        n_plots = len(subplot_params)
        n_rows = math.ceil(n_plots / n_cols)
    
        fig1, axes = plt.subplots(
            n_rows, n_cols,
            figsize=(5 * n_cols, 3.2 * n_rows),
            sharex=True
        )
        axes = np.array(axes).reshape(-1)
        
        for sig_i, sig in enumerate(subplot_params):
            ax = axes[sig_i]
            ax.set_title(sig)
            ax.grid(True, alpha=0.25)
    
            for run_i, (run_label, df) in enumerate(dfs):
                if xAxis == None:
                    xx = df.index
                else:
                    xx = df[xAxis]
                if sig not in df.columns:
                    continue
    
                ax.plot(
                    xx,
                    df[sig],
                    color=run_color_map[run_label],   # 🔑 color per run
                    linestyle=run_linestyles[run_i % len(run_linestyles)],
                    linewidth=1.8,
                    label=run_label if sig_i == 0 else None
                )
                ax.set_xlabel('Time (s)')
    
        # Turn off unused axes
        for j in range(sig_i + 1, len(axes)):
            axes[j].axis("off")
    
        # axes[min(n_plots - 1, len(axes) - 1)].set_xlabel("time")
    
        # fig1.suptitle("Selected Parameters (color = run)", y=0.98)
    
        # One legend for the whole figure (runs only)
        handles, labels = axes[0].get_legend_handles_labels()
        if handles:
            fig1.legend(handles, labels, loc="upper right", frameon=False)
    
        fig1.tight_layout()
        plt.show()

    # ---------- Figure 2: overlay ----------
    if overlay_params !=None:

        plt.figure(figsize=(12, 5))
    
        for run_i, (run_label, df) in enumerate(dfs):
            for sig in overlay_params:
                if sig not in df.columns:
                    continue
    
                plt.plot(
                    df.index,
                    df[sig],
                    color=run_color_map[run_label],   # 🔑 same color here
                    linestyle=run_linestyles[run_i % len(run_linestyles)],
                    linewidth=1.8,
                    label=run_label
                )
    
        plt.xlabel("time")
        plt.ylabel("value")
        plt.title("Other Selected Parameters (color = run)")
        plt.grid(True, alpha=0.25)
    
        # Deduplicate legend labels
        handles, labels = plt.gca().get_legend_handles_labels()
        uniq = dict(zip(labels, handles))
        plt.legend(uniq.values(), uniq.keys(), frameon=False)
    
        plt.tight_layout()
        plt.show()
        

def trim_from_ramp_start(df, col,
                         flat_samples=300,      # how many initial samples to learn "flat" behavior
                         jump_factor=5.0,       # how much bigger than flat jumps counts as "real start"
                         min_jump=1.0,          # absolute minimum jump size to consider
                         baseline_tol=0.05):    # value must rise above baseline by this amount
    """
    Find the first point where a signal transitions from "flat-ish" to "increasing",
    then return (row_position, time_value, trimmed_df).

    Assumes df.index is time.
    """
    # Fill gaps so we can detect changes even if samples alternate with NaNs
    s = df[col].ffill().bfill()
    vals = s.to_numpy()
    t = df.index.to_numpy()

    n = len(vals)
    if n < 3:
        raise ValueError("Not enough samples to detect a ramp start.")

    fs = min(flat_samples, n - 2)

    # Baseline = typical value in the initial flat region
    baseline = float(np.median(vals[:fs]))

    # Learn what "normal" step changes look like in the flat region
    flat_absdiff = np.abs(np.diff(vals[:fs]))
    noise_jump = float(np.nanpercentile(flat_absdiff, 99)) if fs > 10 else float(np.nanpercentile(np.abs(np.diff(vals)), 99))

    # Threshold for a "real" jump that indicates ramp start
    jump_thr = max(min_jump, jump_factor * noise_jump)

    d = np.diff(vals)

    ramp_pos = None
    for i in range(1, n):
        # jump bigger than threshold AND value is above baseline
        if abs(d[i - 1]) > jump_thr and vals[i] > baseline + baseline_tol:
            ramp_pos = i
            break

    if ramp_pos is None:
        # Fallback: if no big jump exists, use first sustained deviation above baseline
        run = 10
        above = vals > baseline + baseline_tol
        count = 0
        for i in range(n):
            if above[i]:
                count += 1
                if count >= run:
                    ramp_pos = i - run + 1
                    break
            else:
                count = 0

    if ramp_pos is None:
        raise ValueError(f"Ramp start not found for column '{col}'. Try adjusting thresholds.")

    ramp_time = t[ramp_pos]
    df_trim = df.loc[ramp_time:].copy()

    return ramp_pos, ramp_time, df_trim

def shift_to_zero(df, *, time_col=None, set_as_index=False, drop=False):
    """
    Shift time so it starts at zero.

    Parameters
    ----------
    df : pandas.DataFrame
        Input DataFrame
    time_col : str or None, optional
        Column name to shift. If None, shift the index.
    set_as_index : bool, default False
        If True and time_col is given, set shifted column as index.
    drop : bool, default False
        If True and time_col is given, drop the original column.

    Returns
    -------
    df_out : pandas.DataFrame
        Time-shifted DataFrame
    """
    df_out = df.copy()

    # --- Case 1: shift index ---
    if time_col is None:
        t0 = df_out.index[0]
        df_out.index = df_out.index - t0
        return df_out

    # --- Case 2: shift column ---
    if time_col not in df_out.columns:
        raise KeyError(f"Column '{time_col}' not found in DataFrame.")

    t0 = df_out[time_col].iloc[0]
    shifted = df_out[time_col] - t0

    if set_as_index:
        df_out.index = shifted
        df_out.index.name = time_col
        if drop:
            df_out = df_out.drop(columns=[time_col])
    else:
        df_out[time_col] = shifted

    return df_out

def integral_cul (df, par='time'):
    
    x = df[f"{par}"]
    
    df_integrated = df.copy()
    for col in df.columns:
        if col != "time":
            df_integrated[col] = cumulative_trapezoid(df[col], x, initial=0)
            return (df_integrated)
        
def integral (df, par='time'):

    x = df[f"{par}"]
    
    integrals = {
        col: np.trapz(df[col], x)
        for col in df.columns if col != "time"
    }
    
    result = pd.Series(integrals)
    return (result)
