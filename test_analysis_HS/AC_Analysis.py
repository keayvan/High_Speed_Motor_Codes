import math
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

# -----------------------------
# Plot config
# -----------------------------
plt.rcParams["font.family"] = "Century Gothic"

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
colors = list(palette.values())

# -----------------------------
# Fast read using:
#  - pyarrow engine (fast, but no chunksize)
#  - chunked fallback (C engine)
#  - parse timestamp after read (ISO8601)
#  - numeric conversion after read (handles '0:' etc.)
#  - parquet caching
# -----------------------------
def read_analog_fast(csv_path: Path, chunksize: int = 250_000) -> pd.DataFrame:
    parquet_path = csv_path.with_suffix(".parquet")

    # (5) Parquet cache: fastest on repeated runs
    if parquet_path.exists():
        return pd.read_parquet(parquet_path)

    # (4) Try pyarrow (fast) WITHOUT chunksize
    try:
        df = pd.read_csv(csv_path, engine="pyarrow")
    except Exception:
        # (6) Fallback: chunked read with default C engine
        chunks = []
        for chunk in pd.read_csv(csv_path, chunksize=chunksize, low_memory=False):
            chunks.append(chunk)
        df = pd.concat(chunks, ignore_index=True)

    # (3) Parse timestamp column after read
    time_col = df.columns[0]
    try:
        df[time_col] = pd.to_datetime(df[time_col], utc=True, format="ISO8601")
    except TypeError:
        df[time_col] = pd.to_datetime(df[time_col], utc=True, errors="coerce")

    # (2) Convert all non-time columns safely to float32
    signal_cols = df.columns[1:]
    for c in signal_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce").astype("float32")

    # (5) Save parquet for next time (skip if parquet engine missing)
    try:
        df.to_parquet(parquet_path, index=False)
    except Exception:
        pass

    return df


# -----------------------------
# Main
# -----------------------------
csv_path = Path(r".\Results_3Phase\k1.csv")
df1 = read_analog_fast(csv_path, chunksize=250_000)

df = df1.copy()

time_col = df.columns[0]

# -----------------------------
# Time window definition
# -----------------------------
t_start_ms = 1000   # original cut
t_end_ms   = 1001   # desired plot end in ORIGINAL time (as in your code)
# Original relative time
time_ms = (df[time_col] - df[time_col].iloc[0]).dt.total_seconds() * 1000

if t_end_ms is None:
    mask = (time_ms >= t_start_ms)
else:
    mask = (time_ms >= t_start_ms) & (time_ms <= t_end_ms)


df = df.loc[mask].reset_index(drop=True)

# Re-zero time so t_start_ms becomes 0
time_ms = time_ms.loc[mask].reset_index(drop=True) - t_start_ms

# -----------------------------
# Channel layout plotting (2 cols x 4 rows)
# Row1: ch0 & ch6, Row2: ch1 & ch4, Row3: ch2 & ch5, Row4: ch3 & ch7
# -----------------------------
channel_name_map = {
    0: "DC Current (A)",
    6: "DC Bus (V)",
    1: "I_a (A)",
    4: "V_a (V)",
    2: "I_b (A)",
    5: "V_b (V)",
    3: "I_c (A)",
    7: "V_c (V)",
}
signal_cols = df.columns[1:]  # channels are columns after time

rename_dict = {
    signal_cols[idx]: name
    for idx, name in channel_name_map.items()
    if idx < len(signal_cols)
}

df = df.rename(columns=rename_dict)
signal_cols = df.columns[1:]  # channels are columns after time

# Optional scaling (kept from your code)
df[signal_cols] = df[signal_cols] * 10

channel_layout = [
    (0, 6),
    (1, 4),
    (2, 5),
    (3, 7),
]

# Safety: ensure channels exist
max_ch = max(max(pair) for pair in channel_layout)
if max_ch >= len(signal_cols):
    raise ValueError(
        f"Channel layout requests channel index {max_ch}, "
        f"but only {len(signal_cols)} channel columns exist."
    )

fig, axes = plt.subplots(
    nrows=4,
    ncols=2,
    figsize=(12, 12),
    sharex=False
)

for row, (ch_left, ch_right) in enumerate(channel_layout):
    # Left
    ax_l = axes[row, 0]
    col_l = signal_cols[ch_left]
    ax_l.plot(time_ms, df[col_l], color=colors[ch_left % len(colors)], linewidth=1.8)
    ax_l.set_title(col_l, fontsize=10)
    ax_l.set_xlabel("Time [ms]")
    ax_l.set_ylabel(col_l)
    ax_l.grid(True, alpha=0.3)

    # Right
    ax_r = axes[row, 1]
    col_r = signal_cols[ch_right]
    ax_r.plot(time_ms, df[col_r], color=colors[ch_right % len(colors)], linewidth=1.8)
    ax_r.set_title(col_r, fontsize=10)
    ax_r.set_xlabel("Time [ms]")
    ax_r.set_ylabel(col_r)
    ax_r.grid(True, alpha=0.3)

fig.suptitle("Selected Channels vs Time", fontsize=14)
plt.tight_layout()
plt.show()

# --- compute DC power first ---
df["DC Power"] = df["DC Current (A)"] * df["DC Bus (V)"]

# --- build time_ms from parsed timestamps (same as your pipeline) ---
# time_ms already exists in your code at this point

# --- create timedelata index for rolling RMS ---
df["_time_td"] = pd.to_timedelta(time_ms, unit="ms")

# Drop rows with invalid time (NaT) before rolling
valid_time = df["_time_td"].notna()
df = df.loc[valid_time].reset_index(drop=True)
time_ms = time_ms.loc[valid_time].reset_index(drop=True)

# Now set index and compute time-based rolling RMS
df = df.set_index("_time_td")

window_ms = 2  # for 20 kHz PWM, 2 ms ~ 40 cycles
df["DC Power RMS"] = (
    df["DC Power"]
    .pow(2)
    .rolling(f"{window_ms}ms", center=True, min_periods=1)
    .mean()
    .pow(0.5)
)

# Restore index for plotting
df = df.reset_index(drop=True)

# Plot
plt.figure(figsize=(8, 3))
plt.plot(time_ms, df["DC Power"], color=palette["blue_medium"], linewidth=2)
plt.plot(time_ms, df["DC Power RMS"], color=palette["red_bright"], linewidth=2)

plt.xlabel("Time [ms]")
plt.ylabel("RMS DC Power [W]")
plt.title(f"Local RMS DC Power ({window_ms} ms window)")
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()

# ============================================================
# 3-Phase power (instantaneous) + local RMS vs time_ms
# Uses your renamed channels: I_a, V_a, I_b, V_b, I_c, V_c
# ============================================================

# --- 1) Instantaneous per-phase powers ---
df["P_a"] = df["I_a (A)"] * df["V_a (V)"]
df["P_b"] = df["I_b (A)"] * df["V_b (V)"]
df["P_c"] = df["I_c (A)"] * df["V_c (V)"]

# --- 2) Total 3-phase instantaneous power (assuming Va,Vb,Vc are phase-to-neutral) ---
df["P_3ph"] = df["P_a"] + df["P_b"] + df["P_c"]

# --- 3) Time-based local RMS of 3-phase power ---
# IMPORTANT: time-based rolling requires a time-like index (TimedeltaIndex) with no NaT
df["_time_td"] = pd.to_timedelta(time_ms, unit="ms")
valid_time = df["_time_td"].notna()
df = df.loc[valid_time].reset_index(drop=True)
time_ms = time_ms.loc[valid_time].reset_index(drop=True)

df = df.set_index("_time_td")

window_ms = 10  # choose (e.g. 2.0 ms for PWM smoothing at 20 kHz, or 10 ms for electrical average)

df["P_3ph_RMS"] = (
    df["P_3ph"]
    .pow(2)
    .rolling(f"{window_ms}ms", center=True, min_periods=1)
    .mean()
    .pow(0.5)
)

# Restore index for plotting
df = df.reset_index(drop=True)

# --- 4) Plot instantaneous 3-phase power + RMS ---
plt.figure(figsize=(10, 3))
plt.plot(time_ms, df["P_3ph"], color=palette["blue_medium"], linewidth=1.5, label="3φ Power (inst.)")
plt.plot(time_ms, df["P_3ph_RMS"], color=palette["red_bright"], linewidth=2.0, label=f"3φ Power RMS ({window_ms} ms)")
plt.xlabel("Time [ms]")
plt.ylabel("Power [W]")
plt.title("3-Phase Power vs Time")
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()
plt.show()

# ============================================================
# Efficiency = P_3ph / P_dc  (instantaneous + local RMS)
# Uses your existing columns:
#   DC Power, DC Power RMS, P_3ph, P_3ph_RMS
# ============================================================

import numpy as np

# --- 1) Instantaneous efficiency ---
# Avoid divide-by-zero and nonsense when DC power is ~0 or negative
pdc = df["DC Power"].astype(float)
pac = df["P_3ph"].astype(float)

eps = 1e-9
df["Efficiency_inst"] = np.where(np.abs(pdc) > eps, pac / pdc, np.nan)

# Optional: limit to [0, 1.5] just for nicer plots (comment out if not wanted)
df["Efficiency_inst_clip"] = df["Efficiency_inst"].clip(lower=0, upper=1.5)

# --- 2) RMS-based efficiency (recommended for a smooth metric) ---
pdc_rms = df["DC Power RMS"].astype(float)
pac_rms = df["P_3ph_RMS"].astype(float)

df["Efficiency_RMS"] = np.where(np.abs(pdc_rms) > eps, pac_rms / pdc_rms, np.nan)
df["Efficiency_RMS_clip"] = df["Efficiency_RMS"].clip(lower=0, upper=1.5)

# --- 3) Plot efficiency vs time_ms ---
plt.figure(figsize=(10, 3))
plt.plot(time_ms, df["Efficiency_inst_clip"], color=palette["gray_medium"], linewidth=1.2, label="η inst (clipped)")
plt.plot(time_ms, df["Efficiency_RMS_clip"], color=palette["lime_green"], linewidth=2.0, label="η RMS (clipped)")
plt.xlabel("Time [ms]")
plt.ylabel("Efficiency (P_3ph / P_dc)")
plt.title("Efficiency vs Time")
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()
plt.show()

# --- 4) If you want efficiency in percent ---
df["Efficiency_RMS_pct"] = 100.0 * df["Efficiency_RMS"]
print("Mean RMS efficiency (%):", np.nanmean(df["Efficiency_RMS_pct"]))

