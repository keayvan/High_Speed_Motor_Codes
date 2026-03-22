# -*- coding: utf-8 -*-
"""
Created on Tue Jan 20 13:31:27 2026

@author: kkeramati
"""
import matplotlib.pyplot as plt
import os
import math
import numpy as np
import pandas as pd

def read_result(file_path,
                powertrain=None,
                remove_ESC_min = None,
                Time = None):
    df = pd.read_csv(file_path)


    # Detect the common prefix in column names (excluding the first column)
    if powertrain !=None:
        old_prefix = os.path.commonprefix(df.columns[1:].tolist())
    
        # Replace it with the desired powertrain name
        if old_prefix:
            new_columns = [
                col.replace(old_prefix, powertrain + " ") if col != df.columns[0] else col
                for col in df.columns
            ]
            df.columns = new_columns
    if remove_ESC_min:
        df = df[df[powertrain +' ESC throttle (μs)']!=remove_ESC_min]
    if Time == 'ms':
        col_idx = 0
        df.iloc[:,col_idx] = df.iloc[:, col_idx]*1000
        df.rename(columns={df.columns[col_idx]: f"Time ({Time})"}, inplace=True)
        
    return df

def plot_parameters_multi(dfs,
                          parameters,
                          x='Time (s)',
                          description="",
                          n_rows=None,
                          markersize=1.5):
    n_params = len(parameters)

    # Automatically determine grid shape if not specified
    if n_rows is None:
        n_rows = math.ceil(math.sqrt(n_params))
    n_cols = math.ceil(n_params / n_rows)

    fig, axes = plt.subplots(n_rows, n_cols, figsize=(5 * n_cols, 3 * n_rows), sharex=True)
    axes = axes.flatten() if n_params > 1 else [axes]

    colors = [ '#0F3878', '#ff596c','#525252ff', '#009494ff', '#f7941dff','#009494ff','#ff596c']*2

    for i, param in enumerate(parameters):
        ax = axes[i]
        for j, df in enumerate(dfs):
            cols = df.columns[1:].tolist()
            Powertrain = os.path.commonprefix(cols)
            param_col = Powertrain + param
            x_col = Powertrain + x if x != 'Time (s)' else x

            if param_col in df.columns:
                ax.plot(
                    df[x_col], df[param_col],
                    'o-', lw=1, ms=markersize,
                    # color=colors[i+j % len(colors)],
                    color=colors[j % len(colors)],

                    label=f"{Powertrain}"
                )
            else:
                print(f"Warning: {param_col} not found in dataframe {Powertrain}")
        
        ax.set_ylabel(param)
        ax.set_xlabel(x)

        ax.legend(fontsize=8)
        ax.grid(True)

    # Hide unused subplots (if grid is larger than needed)
    for j in range(n_params, len(axes)):
        fig.delaxes(axes[j])

    
    plt.suptitle(f"Results {description}", fontsize=14)
    plt.tight_layout(rect=[0, 0, 1, 0.97])
    plt.show()






def trim_after_trigger(
    df: pd.DataFrame,
    *,
    time_col: str = "Time (s)",
    signal_col: str = "Powertrain 1 - current (A)",
    trigger_duration_s: float = 1.0,
    baseline_window_s: float = 5.0,
    abs_threshold: float = 1.0,
    k_mad: float = 10.0,
    fill_method: str | None = "ffill",     # "ffill", "interpolate", or None
    resample_hz: float | None = None,      # e.g. 1000 for uniform 1 kHz time base
) -> tuple[pd.DataFrame, dict]:
    """
    Finds trigger from a step-like rise in `signal_col`, then returns data AFTER `trigger_duration_s`
    and shifts `time_col` to start at 0 at the trigger end.



    Returns (trimmed_df, info_dict).
    """
    if time_col not in df.columns or signal_col not in df.columns:
        raise KeyError(f"Missing required columns: {time_col!r} and/or {signal_col!r}")

    # Work on non-NaN samples only
    sig = df[[time_col, signal_col]].dropna().sort_values(time_col).reset_index(drop=True)
    t_raw = sig[time_col].to_numpy()
    x = sig[signal_col].to_numpy()

    if len(sig) < 10:
        raise ValueError("Not enough non-NaN samples in the trigger signal to detect a trigger.")

    # Convert times to seconds for internal processing if input was ms
    # if time_col == 'Time (ms)':
    #     t = t_raw.astype(float) / 1000.0
    # else:
    t = t_raw.astype(float)

    # Robust baseline over initial window (baseline_window_s is in seconds)
    t0 = float(t[0])
    baseline_mask = t <= (t0 + float(baseline_window_s))
    xb = x[baseline_mask]
    if len(xb) < 10:
        xb = x[: min(len(x), 2000)]  # fallback

    med = float(np.nanmedian(xb))
    mad = float(np.nanmedian(np.abs(xb - med)))
    robust_sigma = 1.4826 * mad if mad > 0 else float(np.nanstd(xb))

    # Threshold to detect the step
    thr = med + max(float(abs_threshold), float(k_mad) * robust_sigma)

    # Trigger start = first sample crossing threshold (operate on x and t arrays)
    if not np.any(x > thr):
        raise ValueError(
            f"No trigger found: signal never exceeds threshold={thr:.4g}. "
            f"Try lowering abs_threshold/k_mad or changing signal_col."
        )
    idx = int(np.argmax(x > thr))
    trigger_start_s = float(t[idx])                 # in seconds
    trigger_end_s = trigger_start_s + float(trigger_duration_s)

    # Trim the original full dataframe after trigger_end and shift time to 0 at trigger_end.
    # Use the original units when selecting rows: convert trigger_end back to original units
    if time_col == 'Time (ms)':
        trigger_end_raw = trigger_end_s * 1000.0
        out = df.loc[df[time_col] >= trigger_end_raw].copy()
    else:
        trigger_end_raw = trigger_end_s
        out = df.loc[df[time_col] >= trigger_end_raw].copy()

    out = out.sort_values(time_col).reset_index(drop=True)

    # Shift time so 0 aligns with trigger_end. Keep same unit as input.
    if time_col == 'Time (ms)':
        out[time_col] = out[time_col].astype(float) - trigger_end_raw   # stays in ms
    else:
        out[time_col] = out[time_col].astype(float) - trigger_end_raw   # stays in s

    # Optional filling (useful because rows are sparse)
    if fill_method == "ffill":
        cols = [c for c in out.columns if c != time_col]
        out[cols] = out[cols].ffill()
    elif fill_method == "interpolate":
        cols = [c for c in out.columns if c != time_col]
        out[cols] = out[cols].interpolate(limit_direction="both")
    elif fill_method is None:
        pass
    else:
        raise ValueError("fill_method must be one of: 'ffill', 'interpolate', or None")

    # Optional resampling to a uniform time grid (resample_hz is in Hz, i.e. per second)
    if resample_hz is not None:
        dt = 1.0 / float(resample_hz)   # seconds between samples on internal grid
        # Build grid in seconds, then map/merge back to original unit
        if time_col == 'Time (ms)':
            # create grid in seconds, convert to ms for merging with out
            tmax_s = float((out[time_col].max()) / 1000.0) if len(out) else 0.0
            grid_s = np.arange(0.0, tmax_s + dt / 2.0, dt)
            grid_raw = pd.DataFrame({time_col: grid_s * 1000.0})  # ms grid
        else:
            tmax_s = float(out[time_col].max()) if len(out) else 0.0
            grid_s = np.arange(0.0, tmax_s + dt / 2.0, dt)
            grid_raw = pd.DataFrame({time_col: grid_s})           # s grid

        merged = pd.merge_asof(grid_raw, out, on=time_col, direction="nearest")
        cols = [c for c in merged.columns if c != time_col]
        merged[cols] = merged[cols].interpolate(limit_direction="both")
        out = merged

    info = {
        "signal_col": signal_col,
        "baseline_window_s": float(baseline_window_s),
        "baseline_median": med,
        "baseline_robust_sigma": robust_sigma,
        "threshold_used": thr,
        "trigger_start_time_s": trigger_start_s,
        "trigger_end_time_s": trigger_end_s,
        # also report raw trigger times in original units for clarity
        "trigger_start_time_raw": (trigger_start_s * 1000.0) if time_col == 'Time (ms)' else trigger_start_s,
        "trigger_end_time_raw": (trigger_end_s * 1000.0) if time_col == 'Time (ms)' else trigger_end_s,
        "rows_before": int(len(df)),
        "rows_after": int(len(out)),
        "time_unit": "ms" if time_col == 'Time (ms)' else "s",
    }
    return out, info
def parms_to_mean(df,
                  parm_for_find,
                  s_win_ms = 7000,
                  e_win_ms = 9000):
    params_mean = []
    value_mean=[]
    keys = list(df.columns)
    for p in parm_for_find:
        for k in keys:
            if p in k:
                mask = (df.iloc[:,0] > s_win_ms) & (df.iloc[:,0]<e_win_ms)
                df = df[mask]
                params_mean.append(k)
                value_mean.append(round(float(df[k].mean()),2))
                break
    return params_mean, value_mean
def parms_to_find(df, parm_for_find):
    params_mean = []
    keys = list(df.columns)
    for p in parm_for_find:
        for k in keys:
            if p in k:
                params_mean.append(k)
                break
    return params_mean

def freq_fundamental (speed, n_magnet):
    f_fundamental = speed * n_magnet/2/60
    T_fundamental = 1/ f_fundamental*1000
    return f_fundamental, T_fundamental

def steps_average(
    df: pd.DataFrame,
    par_step: str = "ESC throttle (μs)",
    mean_min: int = 10,
    mean_max: int = 20,
    start_df = 2,
    end_df = None,
    win = False
):
    """
    Compute per-step averages over a fixed window after each step change.

    - Detects the step column by exact name or suffix (for prefixed columns).
    - Averages ALL numeric columns and returns a DataFrame with the same columns
      (non-numeric columns are included as NaN).
    """

    if mean_max <= mean_min:
        raise ValueError("mean_max must be greater than mean_min")

    # Find the step column (exact or suffix match)
    if par_step in df.columns:
        step_col = par_step
    else:
        matches = [c for c in df.columns if c.endswith(par_step)]
        if len(matches) == 1:
            step_col = matches[0]
        elif not matches:
            raise KeyError(f"Could not find step column '{par_step}' (no exact or suffix match).")
        else:
            raise KeyError(f"Ambiguous step column for suffix '{par_step}': {matches}")

    step_series = df[step_col]

    # Detect start of each step: row 0 OR any change vs previous row
    prev = step_series.shift()                # no fill_value -> result has NaN at row 0
    step_starts_mask = prev.isna() | step_series.ne(prev)
    step_starts = np.flatnonzero(step_starts_mask.to_numpy())

    rows = []
    for start in step_starts:
        lo = start + mean_min
        hi = min(start + mean_max, len(df))   # exclusive upper bound, clipped to end
        if lo >= hi:                          # not enough data for this window
            continue

        window = df.iloc[lo:hi]
        means = window.mean(numeric_only=True)      # average ALL numeric columns
        row = means.reindex(df.columns)             # preserve original column order/names
        rows.append(row)
    out = pd.DataFrame(rows[start_df:])

    if end_df !=None:
        out = pd.DataFrame(rows[start_df:end_df])
    out.index = range(len(out))
    if win is True:
        return out, int(step_starts[2] - step_starts[1]) 
    else:
        return out
    
