# -*- coding: utf-8 -*-
"""
Created on Tue Jan 20 13:05:39 2026

@author: kkeramati
"""
import pandas as pd
import math
from matplotlib import pyplot as plt
import numpy as np 
import re

def param_resolution (df,
                      time_format = None):
    time_col = "Time (s)"
    if time_format !=None:
        time_col = f"Time ({time_format})"
    # Dictionary to store the separate DataFrames
    dataframes = {}
    
    for col in df.columns:
        if col == time_col:
            continue
    
        # Select rows where this column has a value
        temp_df = df[[time_col, col]].dropna()
    
        # Only keep if there is actual data
        if not temp_df.empty:
            dataframes[col] = temp_df.reset_index(drop=True)
    return dataframes

def sampling_rate_TYTO(time_ms):
    t = np.asarray(time_ms, dtype=float)
    dt = np.diff(t)
    dt = dt[np.isfinite(dt) & (dt > 0)]          # keep valid positive steps

    # keep only the "typical" small steps (remove gaps/outliers)
    q1, q3 = np.percentile(dt, [25, 75])
    iqr = q3 - q1
    dt_f = dt[(dt >= q1 - 1.5*iqr) & (dt <= q3 + 1.5*iqr)]

    dt_ms = np.median(dt_f)                      # typical timestep in ms
    fs_hz = 1000.0 / dt_ms                       # ms -> Hz
    return fs_hz, dt_ms


def plot_fullRes(df_res, params, n_rows=1,
                 time_format = None,
                 fig_input = None,
                 ax_input = None):
    plt.rcParams["font.family"] = "DejaVu Sans"

    # --- pick keys ---
    if params is all or params == "all":
        params_TYTO = list(df_res.keys())
    else:
        params_TYTO = []
        keys = list(df_res.keys())
        for k in keys:
            for p in params:
                if p in k:
                    params_TYTO.append(k)
                    break

    if len(params_TYTO) == 0:
        raise ValueError("No matching parameters found in df_res keys.")

    # --- remove common words from labels (safe even if empty) ---
    word_sets = [set(item.split()) for item in params_TYTO]
    common_words = set.intersection(*word_sets) if word_sets else set()
    common_title = " ".join(sorted(common_words)) if common_words else ""

    params_TYTO_NEW = [
        " ".join(word for word in item.split() if word not in common_words)
        for item in params_TYTO
    ]

    n_params = len(params_TYTO_NEW)

    # --- grid shape ---
    if n_rows is None:
        n_rows = math.ceil(math.sqrt(n_params))
    n_cols = math.ceil(n_params / n_rows)

    # --- figure + better spacing ---
    fig, axes = plt.subplots(
        n_rows, n_cols,
        figsize=(5 * n_cols, 3.2 * n_rows),
        sharex=True,
        constrained_layout=False  # we'll control spacing manually
    )
    axes = axes.flatten() if n_params > 1 else [axes]

    # More breathing room (these are the "good distances")
    fig.subplots_adjust(
        left=0.08, right=0.98,
        bottom=0.08, top=0.90,   # leaves room for suptitle
        wspace=0.30, hspace=0.45 # space between subplots
    )

    colors = ['#0F3878', '#ff596c', '#525252ff', '#009494ff', '#f7941dff'] * 5

    x_col = 'Time (s)'
    if time_format !=None:
        x_col = f'Time ({time_format})'
    for i, label in enumerate(params_TYTO_NEW):
        ax = axes[i]
        ax.plot(
            df_res[params_TYTO[i]].iloc[:, 0],
            df_res[params_TYTO[i]].iloc[:, 1],
            'o-',
            lw=1, ms=1,
            color=colors[i % len(colors)]
        )

        ax.set_ylabel(label, labelpad=6)  # small padding helps readability
        ax.set_xlabel(x_col, labelpad=6)
        ax.grid(True, alpha=0.35)

        # Optional: keep labels from crowding the plot area
        ax.margins(x=0.02, y=0.08)

    # Title (don't pop twice)
    if common_title:
        fig.suptitle(common_title, y=0.98)

    # Remove extra axes
    for j in range(n_params, len(axes)):
        fig.delaxes(axes[j])
    return fig, axes[:n_params]


def find_matching_key(d, target_key):
    # exact match first
    if target_key in d:
        return target_key
    # fallback: match by cleaned text
    t = " ".join(str(target_key).split())
    for k in d.keys():
        kk = " ".join(str(k).split())
        if kk == t:
            return k
    # fallback: substring (looser)
    for k in d.keys():
        if t in str(k) or str(k) in t:
            return k
    return None

def _tokens(s: str) -> set[str]:
    """Normalize string -> set of tokens for fuzzy matching."""
    s = str(s).lower()
    s = re.sub(r"[^a-z0-9]+", " ", s)   # keep letters/numbers
    s = re.sub(r"\s+", " ", s).strip()
    return set(s.split())

def _jaccard(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)

def _common_label(keys: list[str]) -> str:
    """Build a label from tokens common to all matched keys."""
    token_sets = [_tokens(k) for k in keys if k is not None]
    if not token_sets:
        return ""
    common = set.intersection(*token_sets)
    # Keep a stable readable order by scanning the first key
    first = str(keys[0]).split()
    common_ordered = [w for w in first if w.lower() in common]
    return " ".join(common_ordered) if common_ordered else " / ".join(sorted(common))

def match_keys_across_dicts(dict_list, min_sim=0.45, require_all=True):
    """
    Match similar keys across multiple dicts.

    Returns:
      canon_labels: list[str]            # common label per signal group
      key_table:   list[list[str|None]]  # rows=signals, cols=dict index
    """
    if isinstance(dict_list, dict):
        dict_list = [dict_list]

    # Use dict0 as anchors (you can choose the "richest" dict instead if you want)
    anchors = list(dict_list[0].keys())
    anchor_tokens = [_tokens(k) for k in anchors]

    # Precompute tokens for other dict keys
    other_keys = [list(d.keys()) for d in dict_list]
    other_tokens = [[_tokens(k) for k in ks] for ks in other_keys]

    key_table = []
    for a_idx, a_key in enumerate(anchors):
        row = [None] * len(dict_list)
        row[0] = a_key
        a_tok = anchor_tokens[a_idx]

        # Find best match in each other dict
        for d_i in range(1, len(dict_list)):
            best_j = None
            best_score = -1.0
            for j, tok in enumerate(other_tokens[d_i]):
                score = _jaccard(a_tok, tok)
                if score > best_score:
                    best_score = score
                    best_j = j

            if best_score >= min_sim:
                row[d_i] = other_keys[d_i][best_j]

        if require_all and any(v is None for v in row):
            continue  # only keep signals present in all dicts
        key_table.append(row)

    canon_labels = [_common_label(row) for row in key_table]
    return canon_labels, key_table

def plot_dicts(df_res_list,
                        canon_labels,
                        key_table,
                        labels=None,
                        n_rows=None,
                        time_format=None,
                        linestyles = ["-", "--", ":", "-."] * 10):

    if isinstance(df_res_list, dict):
        df_res_list = [df_res_list]

    n_sets = len(df_res_list)
    n_params = len(key_table)

    if labels is None:
        labels = [f"set {i}" for i in range(n_sets)]

    # ---- grid ----
    if n_rows is None:
        n_rows = math.ceil(math.sqrt(n_params))
    n_cols = math.ceil(n_params / n_rows)

    fig, axes = plt.subplots(
        n_rows, n_cols,
        figsize=(5 * n_cols, 3.2 * n_rows),
        sharex=True,
        constrained_layout=False
    )

    axes = axes.flatten() if n_params > 1 else [axes]
    fig.subplots_adjust(left=0.08, right=0.98,
                        bottom=0.08, top=0.92,
                        wspace=0.30, hspace=0.45)

    palette = {
        "teal_dark": "#009494ff",
        "red_bright": "#f74242ff",
        "orange_bright": "#f7941dff",

        "gray_medium": "#848484ff",
        "lime_green": "#0AFFA0",
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

    x_label = 'Time (s)' if time_format is None else f'Time ({time_format})'

    # ---- plotting ----
    for i, (label, row) in enumerate(zip(canon_labels, key_table)):
        ax = axes[i]

        for d_i, key in enumerate(row):
            if key is None:
                continue

            df = df_res_list[d_i][key]
            x = df.iloc[:, 0].to_numpy()
            y = df.iloc[:, 1].to_numpy()

            ax.plot(x, y,
                    lw=1.2,
                    ls=linestyles[d_i],
                    alpha=0.9,
                    color=colors[d_i % len(colors)],
                    label=labels[d_i])

        ax.set_ylabel(label, labelpad=6)
        ax.set_xlabel(x_label, labelpad=6)
        ax.grid(True, alpha=0.35)
        ax.margins(x=0.02, y=0.08)

        if n_sets > 1:
            ax.legend(fontsize=8)

    # remove extra axes
    for j in range(n_params, len(axes)):
        fig.delaxes(axes[j])

    return fig, axes[:n_params]
