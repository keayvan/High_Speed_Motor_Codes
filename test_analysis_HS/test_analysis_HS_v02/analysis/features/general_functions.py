# -*- coding: utf-8 -*-
"""
Created on Wed Feb  4 14:27:40 2026

@author: kkeramati
"""
import pandas as pd
import numpy as np
import re
import math
import matplotlib.pyplot as plt
def find_params_in_df(df, params):
    params_TYTO = []
    keys = list(df.columns)
    for k in keys:
        for p in params:
            if p in k:
                params_TYTO.append(k)
                break
    return params_TYTO

def find_params_in_dict(df, params):
    params_TYTO = []
    keys = list(df.keys())
    for k in keys:
        for p in params:
            if p in k:
                params_TYTO.append(k)
                break
    return params_TYTO

def find_params_in_df_v1(df, params):
    col_names = []
    col_indices = []
    
    for i, col in enumerate(df.columns):
        if any(p in col for p in params):
            col_names.append(col)
            col_indices.append(i)
    
    return col_names, col_indices

def sync_time_Salea_with_TYTO (df, y_col, time_col = "Time (ms)", smooth_window=31, consec=10, k=5.0):
    """
    Returns the first index where the signal begins increasing (step onset),
    using a smoothed derivative + consecutive condition.
    
    k controls sensitivity: larger = less sensitive (fewer false triggers).
    """
    y = df[y_col].to_numpy()

    # Smooth to reduce noise (median is robust for step-like signals)
    ys = pd.Series(y).rolling(smooth_window, center=True, min_periods=1).median().to_numpy()

    dy = np.diff(ys, prepend=ys[0])

    # Robust threshold using MAD (median absolute deviation)
    med = np.median(dy)
    mad = np.median(np.abs(dy - med)) + 1e-12
    thr = med + k * 1.4826 * mad  # 1.4826*MAD ~ std for normal

    inc = dy > thr

    # Find first position with `consec` Trues in a row
    run = np.convolve(inc.astype(int), np.ones(consec, dtype=int), mode="same")
    idx = np.argmax(run >= consec)
    if run[idx] < consec:
        # fallback: if never found, return 0
        return df.index[0]
    t0 = df.loc[df.index[idx], time_col] 
    t0 = np.float64(t0)
    t0 = t0.astype(float).item()
    return df.index[idx], t0

def cut_shift_dataframe(df, t_srart, time_col = "Time (ms)"):
    mask = df[time_col] > t_srart 
    df_cut = df.loc[mask].copy()
    df_cut.loc[:, time_col] = df_cut[time_col] - df_cut[time_col].min()

    return df_cut

def cut_shift_dict(df_res, start_TYTO_ms, end_TYTO_ms=None ):
    param_dict = list(df_res.keys())
    out = {}
    for i,v  in enumerate(param_dict):
        df_dict = df_res[v]
        mask = (df_dict.iloc[:,0]>start_TYTO_ms) & (df_dict.iloc[:,0]<end_TYTO_ms)
        if 'ESC' in v:
            mask = (df_dict.iloc[:,0]>start_TYTO_ms-1000) & (df_dict.iloc[:,0]<end_TYTO_ms+150)
        df_dict =df_dict[mask]     
        df_dict.iloc[:,0] = df_dict.iloc[:,0]-df_dict.iloc[:,0].min()
        out[v] = df_dict
    return out



colors = [ '#0F3878', '#ff596c','#525252ff', '#009494ff', '#f7941dff','#009494ff','#ff596c']*2

def _norm(s: str) -> str:
    """Normalize a string for matching (casefold + collapse whitespace)."""
    return re.sub(r"\s+", " ", str(s)).strip().casefold()

def strip_prefix_from_label(s, prefixes):
    s = str(s).strip()
    for p in prefixes or []:
        p = str(p).strip()
        if not p:
            continue
        # case-insensitive "PREFIX " at the start
        if s.lower().startswith(p.lower() + " "):
            return s[len(p):].lstrip(" _-")
    return s
from collections.abc import Mapping

def apply_zoom_ms(data, zoom_ms, time_ms_col: str = "Time (ms)"):
    """
    Apply a [tmin, tmax] zoom window to:
      - DataFrame
      - dict of DataFrames (each DF can have different length/time)
      - nested dicts of DataFrames

    Returns same structure as input.
    """
    if zoom_ms is None:
        return data

    tmin, tmax = zoom_ms

    def _zoom_df(df: pd.DataFrame) -> pd.DataFrame:
        if time_ms_col not in df.columns:
            raise KeyError(f"'{time_ms_col}' not found in DataFrame columns: {list(df.columns)}")
        m = (df[time_ms_col] >= tmin) & (df[time_ms_col] <= tmax)
        return df.loc[m].reset_index(drop=True)

    # DataFrame
    if isinstance(data, pd.DataFrame):
        return _zoom_df(data)

    # Dict (possibly nested)
    if isinstance(data, Mapping):
        out = {}
        for k, v in data.items():
            if isinstance(v, pd.DataFrame):
                out[k] = _zoom_df(v)
            elif isinstance(v, Mapping):
                out[k] = apply_zoom_ms(v, zoom_ms, time_ms_col=time_ms_col)  # recurse for nested dicts
            else:
                raise TypeError(f"Unsupported value type at key '{k}': {type(v)}")
        return out

    raise TypeError(f"Unsupported input type: {type(data)}")

def mean_Salea_TYTO (df_TYTO_sync,
                     df_TYTO_manual,
                     time_steps,
                     df_salea_sync):
    
    t_start_step = list(time_steps[:-1])
    t_end_step = list(time_steps[1:])
    
    mean_TYTO_steps_list = []
    mean_Salea_steps_list = []
    for n_step, start_time in enumerate(t_start_step):
        time_start_zoom = t_start_step[n_step]
        time_end_zoom = t_end_step[n_step]
        
        delta_t_zoom_ms = time_end_zoom-time_start_zoom
        time_start_zoom = time_start_zoom + delta_t_zoom_ms*0.2  
        time_end_zoom = time_end_zoom -delta_t_zoom_ms*0.2
        
        ZOOM_MS = (time_start_zoom, time_end_zoom)
        
        df_zoomed_TYTO = apply_zoom_ms(df_TYTO_sync, ZOOM_MS, time_ms_col="Time (ms)")
        mean_TYTO_steps = {}
        for key, df in df_zoomed_TYTO.items():
            # Take the second column (parameter values) and compute mean
            mean_value = df.iloc[:, 1].mean()
            mean_TYTO_steps[key] = mean_value
        mean_TYTO_steps_list.append(mean_TYTO_steps)
    
        
        df_zoomed_Salea = apply_zoom_ms(df_salea_sync, ZOOM_MS, time_ms_col="Time (ms)")
        mean_Salea_steps = df_zoomed_Salea.mean()
        mean_Salea_steps_list.append(mean_Salea_steps)
        
    params_mean = ["speed"]
    params_mean = find_params_in_dict(df_TYTO_sync, params_mean)[0]
    speeds_mean  = [s[params_mean] for s in mean_TYTO_steps_list]  
    param = "P_AC (W)"
    P_AC  = [s[param] for s in mean_Salea_steps_list]     
    param = "P_DC (W)"
    P_DC  = [s[param] for s in mean_Salea_steps_list] 
    

    df_steps_ave = pd.DataFrame.from_dict({"Speed (rpm)": speeds_mean,
                                           "t_start (ms)": t_start_step,
                                           "t_end (ms)": t_end_step,
                                         "P_DC (W)":  P_DC,
                                         "P_AC (W)":  P_AC,
                                         "P_TYTO_electrical (W)": df_TYTO_manual.iloc[1:,7],
                                         "P_mechanical (W)": df_TYTO_manual.iloc[1:,8]})
    
    return mean_TYTO_steps_list, mean_Salea_steps_list, df_steps_ave

def efficiency_func(df_steps_ave):
    efficiency = pd.DataFrame.from_dict({"HBC Efficiency %": df_steps_ave["P_AC (W)"]/df_steps_ave["P_DC (W)"]*100,
                                         "Motor Efficiency %": df_steps_ave["P_mechanical (W)"]/df_steps_ave["P_AC (W)"]*100,
                                         "Power train Efficiency %":df_steps_ave["P_mechanical (W)"]/df_steps_ave["P_DC (W)"]*100})
    return efficiency
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
    dfs,
    parameters,
    x_col=None,
    colors=colors,
    line_style = '-',
    ncols=2,
    figsize_per_subplot=(5, 2),
    df_labels=None,
    allow_contains=True,
):
    """
    Plot same logical parameters across multiple DataFrames, even if columns have prefixes.

    Args:
        dfs: list[pd.DataFrame]
        parameters: str or list[str] of logical parameter(s), e.g. "voltage (V)" or ["voltage (V)", "current (A)"]
        x_col: column name to use as x for all DFs; if None, uses df.index
        colors: list of hex colors
        ncols: number of subplot columns
        figsize_per_subplot: (width, height) per subplot
        df_labels: optional list[str] to label each dataframe in legend
        allow_contains: if True, match when parameter is contained in column name; else exact match after prefix stripping
    """
    # Accept single parameter string
    if isinstance(parameters, str):
        parameters = [parameters]

    if df_labels is None:
        df_labels = [f"df{i}" for i in range(len(dfs))]

    # Precompute normalized column names for each df
    df_cols_norm = []
    for df in dfs:
        cols = list(df.columns)
        df_cols_norm.append([_norm(c) for c in cols])

    n = len(parameters)
    nrows = math.ceil(n / ncols)

    fig_w = figsize_per_subplot[0] * ncols
    fig_h = figsize_per_subplot[1] * nrows
    fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(fig_w, fig_h), squeeze=False)

    for p_idx, param in enumerate(parameters):
        ax = axes[p_idx // ncols][p_idx % ncols]
        p_norm = _norm(param)

        any_plotted = False
    

        for i, df in enumerate(dfs):
            cols = list(df.columns)
            cols_norm = df_cols_norm[i]

            # Match columns: "MGM voltage (V)" matches "voltage (V)"
            matches = []
            for c, cn in zip(cols, cols_norm):
                if allow_contains:
                    if p_norm in cn:
                        matches.append(c)
                else:
                    # Try to remove a prefix token (first word) then compare
                    # e.g. "MGM voltage (V)" -> "voltage (V)"
                    tokens = cn.split(" ")
                    if len(tokens) >= 2 and _norm(" ".join(tokens[1:])) == p_norm:
                        matches.append(c)
                    elif cn == p_norm:
                        matches.append(c)
                    
            # If multiple matches inside same df, plot them all
            x_col1 = find_params_in_df(df, [x_col])[0]
            for m_idx, col in enumerate(matches):
                x = df[x_col1] 
                y = df[col]
                label = f"{df_labels[i]}"
                ax.plot(x, y, line_style, color=colors[(i + m_idx) % len(colors)],  linewidth=1.8, label=label)
                any_plotted = True

        ax.set_xlabel(x_col)        
        ax.set_ylabel(strip_prefix_from_label(param, df_labels))
        


        ax.grid(True, alpha=0.3)
        if any_plotted:
            ax.legend(fontsize=8)
        else:
            ax.text(0.5, 0.5, "No matching columns", ha="center", va="center", transform=ax.transAxes)
            ax.set_axis_off()

    # Hide unused axes
    for k in range(n, nrows * ncols):
        axes[k // ncols][k % ncols].set_axis_off()

    plt.tight_layout()
    return fig, axes

def mean_tyto_full_resolution(dic_TYTO_full_res, time_steps):
    t_start_step = list(time_steps[:-1])
    t_end_step = list(time_steps[1:])
    
    mean_TYTO_steps_list = []
    for n_step, start_time in enumerate(t_start_step):
        time_start_zoom = t_start_step[n_step]
        time_end_zoom = t_end_step[n_step]
        
        delta_t_zoom_ms = time_end_zoom-time_start_zoom
        time_start_zoom = time_start_zoom + delta_t_zoom_ms*0.2 
        time_end_zoom = time_end_zoom -delta_t_zoom_ms*0.2
        
        ZOOM_MS = (time_start_zoom, time_end_zoom)
        
        df_zoomed_TYTO = apply_zoom_ms(dic_TYTO_full_res, ZOOM_MS, time_ms_col="Time (ms)")
        mean_TYTO_steps = {}
        for key, df in df_zoomed_TYTO.items():
            # Take the second column (parameter values) and compute mean
            mean_value = df.iloc[:, 1].mean()
            mean_TYTO_steps[key] = mean_value
        mean_TYTO_steps_list.append(mean_TYTO_steps)
        
    params_mean = ["thrust", "torque", "voltage", "current", "speed"]
    params_mean = find_params_in_dict(dic_TYTO_full_res, params_mean)
    
    param_mean_all = []
    for par_indx, par in enumerate(params_mean):
        param_mean  = [float(s[par]) for s in mean_TYTO_steps_list]
        param_mean_all.append(param_mean)
        
    df = pd.DataFrame(dict(zip(params_mean,param_mean_all)))
    time_steps_df = list(time_steps) [1:]
    df["Time (ms)"] =  time_steps_df
    return df
