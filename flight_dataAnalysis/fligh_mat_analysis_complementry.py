# -*- coding: utf-8 -*-
"""
Created on Tue Dec 30 13:26:36 2025

@author: kkeramati
"""

import h5py
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import math
from analysisPlotting_func import trim_from_ramp_start as trim


def read_mat(file_path):
    signals = {}
    time = None
    
    with h5py.File(file_path, "r") as f:
        for key in f.keys():
            obj = f[key]
    
            # In your file, each top-level key is a GROUP like "Pitch"
            # and the data is in datasets like "Pitch/value" and "Pitch/time"
            if isinstance(obj, h5py.Group) and ("value" in obj) and ("time" in obj):
                values = np.array(obj["value"]).reshape(-1)  # safe for (N,) or (N,1)
                t = np.array(obj["time"]).reshape(-1)
    
                signals[key] = values
                if time is None:
                    time = t  # take the first time vector as the common one
    
    df = pd.DataFrame(signals)
    cols =  list(df.columns)
    df.insert(0, "time", time/1e9)
    return df, cols


def plot_mat(df, x_col):
    if x_col not in df.columns:
        raise ValueError(f"{x_col} not found in DataFrame")
    
    # ---- Prepare subplot grid ----
    y_cols = [c for c in df.columns if c != x_col]
    n_plots = len(y_cols)
    
    n_cols = 3  # adjust layout here
    n_rows = math.ceil(n_plots / n_cols)
    
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(5 * n_cols, 3 * n_rows))
    axes = axes.flatten()
    
    x = df[x_col]
    
    for ax, y_col in zip(axes, y_cols):
        mask = x.notna() & df[y_col].notna()
        if mask.sum() == 0:
            ax.set_title(f"{y_col} (no data)")
            ax.axis("off")
            continue
    
        ax.plot(x[mask].values, df.loc[mask, y_col].values, color = 'gray')
        ax.set_xlabel(x_col)
        ax.set_ylabel(y_col)
        ax.set_title(f"{y_col} vs {x_col}")
        ax.grid(True)
    
    # Turn off unused subplots
    for ax in axes[len(y_cols):]:
        ax.axis("off")
    
    plt.tight_layout()
    plt.show()
    return axes

if __name__ == "__main__":

    file_path = "./data/Dec2025/2025_12_11_16_29_59.txt_unified (1).mat"

    

    
    df, cols = read_mat(file_path)
    df["time"] = df["time"]-df["time"].min()
    ramp_pos, ramp_time, df_trim = trim(df, 
                                         col = 'Pitch_c',
                                         flat_samples=300,      
                                         jump_factor=5.0,      
                                         min_jump=1.0,          
                                         baseline_tol=0.05)
    
    x_col = "time"   # change to any column, e.g. "Pitch"
    axes = plot_mat(df_trim,
             x_col)
    
    for i in range(len(axes)-1):
        axes[i].axvline(133, color = 'red', ls = '--')
        

    
    # =============================
    # 1) FLIGHT MODE DEFINITIONS
    # =============================
    FLIGHT_MODE_MAP = {
        0:  "Manual",
        1:  "Takeoff 1",
        2:  "Takeoff 2",
        3:  "Flightplan",
        4:  "Landing VC",
        5:  "Landing TB",
        6:  "Landing AP",
        7:  "Landing CF",
        8:  "Landing FL",
        9:  "Landing DM",
        10: "Landing OD",
        11: "Loiter",
        12: "Preflight",
        13: "Cal Serv",
        14: "Cal Sens",
        15: "Test",
        16: "Roulette",
        17: "Semiautomatic",
        18: "FlyTo",
        19: "Home",
        20: "Degraded",
        21: "Attack",
        22: "Keep Trajectory",
        23: "Abort Attack",
        24: "Chase",
    }
    
    UNKNOWN_LABEL = "UNMAPPED"
    
    # =============================
    # 2) CLEAN + FILL FlightMode
    # =============================
    def clean_and_fill_flightmode(df: pd.DataFrame, col="FlightMode"):
        out = df.copy()
        out[col] = pd.to_numeric(out[col], errors="coerce")
        out[col] = out[col].ffill().bfill().astype(int)
        return out
    
    df_filled = clean_and_fill_flightmode(df)
    
    # Add labels
    df_filled["FlightModeLabel"] = (
        df_filled["FlightMode"]
        .map(FLIGHT_MODE_MAP)
        .fillna(UNKNOWN_LABEL)
    )
    
    # =============================
    # 3) EXTRACT SEGMENTS (TIME ORDERED)
    # =============================
    def extract_segments_time_ordered(df: pd.DataFrame, col="FlightMode", dt=None):
        s = df[col].to_numpy()
    
        # Detect changes
        change_idx = np.where(s[1:] != s[:-1])[0] + 1
    
        starts = np.r_[0, change_idx]
        ends = np.r_[change_idx - 1, len(s) - 1]
    
        seg = pd.DataFrame({
            "start_idx": starts,
            "end_idx": ends,
            "mode_code": s[starts],
            "n_samples": ends - starts + 1,
        })
    
        # Ensure TIME ORDER (this is what you asked for)
        seg = seg.sort_values("start_idx").reset_index(drop=True)
    
        if dt is not None:
            seg["duration_s"] = seg["n_samples"] * dt
            seg["start_time_s"] = seg["start_idx"] * dt
            seg["end_time_s"] = seg["end_idx"] * dt
    
        seg["mode_label"] = seg["mode_code"].map(FLIGHT_MODE_MAP).fillna(UNKNOWN_LABEL)
    
        return seg
    
    segments = extract_segments_time_ordered(df_filled, dt=None)
    
    # =============================
    # 4) RESULT: TIME SEQUENCE TABLE
    # =============================
    print("Flight modes in TIME ORDER:\n")
    print(
        segments[
            ["start_idx", "end_idx", "n_samples", "mode_code", "mode_label"]
        ]
    )
    
    # =============================
    # 5) PLOT WITH MODE NAMES
    # =============================
    plt.figure(figsize=(12, 4))
    plt.step(df_filled.index, df_filled["FlightMode"], where="post")
    plt.xlabel("Sample index")
    plt.ylabel("Flight Mode")
    
    # Annotate mode names at segment centers
    for _, row in segments.iterrows():
        x = (row["start_idx"] + row["end_idx"]) / 2
        y = row["mode_code"]
        plt.text(x, y, row["mode_label"], ha="center", va="bottom", fontsize=8)
    
    plt.grid(True)
    plt.title("Flight Mode Timeline")
    plt.tight_layout()
    plt.show()
