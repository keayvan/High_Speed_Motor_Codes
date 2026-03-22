# -*- coding: utf-8 -*-
"""
FFT feature extraction for time-series signals.

Assumptions:
- DataFrame contains a column "Time [ms]"
- Signals are numeric columns
- Time is monotonic
"""

import numpy as np
import pandas as pd
from scipy.signal import find_peaks, peak_prominences


def _sampling_frequency_from_time_ms(
    t_ms: pd.Series,
) -> float:
    """
    Estimate sampling frequency (Hz) from Time [ms].
    """
    dt_ms = np.diff(t_ms.to_numpy(dtype=float))
    dt_ms = dt_ms[dt_ms > 0]

    if dt_ms.size == 0:
        raise ValueError("Cannot determine sampling frequency from Time [ms].")

    dt = np.median(dt_ms) * 1e-3  # seconds
    return 1.0 / dt



def fft_single_channel(
    df: pd.DataFrame,
    signal_col: str,
    time_ms_col: str = "Time [ms]",
    window: str | None = "hann",
    detrend: bool = True,
    normalize: bool = True,   # keep name, but now means amplitude-normalized
) -> pd.DataFrame:

    x = pd.to_numeric(df[signal_col], errors="coerce").to_numpy(dtype=float)
    t_ms = df[time_ms_col]

    mask = np.isfinite(x)
    x = x[mask]
    t_ms = t_ms.iloc[mask]

    if x.size < 2:
        raise ValueError(f"Not enough samples for FFT: {signal_col}")

    fs = _sampling_frequency_from_time_ms(t_ms)

    if detrend:
        x = x - np.mean(x)

    n = x.size

    # windowing
    cg = 1.0
    if window is not None:
        if window == "hann":
            w = np.hanning(n)
        elif window == "hamming":
            w = np.hamming(n)
        else:
            raise ValueError(f"Unsupported window: {window}")
        x = x * w
        cg = w.mean()  # coherent gain for amplitude correction

    X = np.fft.rfft(x)
    freq = np.fft.rfftfreq(n, d=1.0 / fs)

    mag = np.abs(X)

    if normalize:
        # amplitude-correct scaling
        mag = mag / (n * cg)

        # one-sided correction: double everything except DC and Nyquist (if present)
        if n % 2 == 0:
            mag[1:-1] *= 2
        else:
            mag[1:] *= 2

    return pd.DataFrame({"frequency_hz": freq, "magnitude": mag})



def first_n_fft_peaks(
    spectrum: pd.DataFrame,
    n_peaks: int = 3,
    fmin: float = 0.0,
    fmax: float | None = None,
    ignore_below_hz: float = 100.0,
    smooth_bins: int = 5,
    min_prominence: float | None = None,
    min_distance_hz: float = 0.0,      # set 0 to not suppress peaks
    prominence_mad_mult: float = 2.0,  # lower than before -> more peaks
) -> pd.DataFrame:
    df = spectrum.copy().sort_values("frequency_hz").reset_index(drop=True)

    low = max(fmin, ignore_below_hz)
    mask = df["frequency_hz"] >= low
    if fmax is not None:
        mask &= df["frequency_hz"] <= fmax

    sub = df.loc[mask].reset_index(drop=True)
    if sub.empty:
        return sub

    freqs = sub["frequency_hz"].to_numpy(float)
    mag = sub["magnitude"].to_numpy(float)

    # Optional smoothing to reduce noise spikes
    if smooth_bins and smooth_bins > 1:
        mag_s = (
            pd.Series(mag)
            .rolling(smooth_bins, center=True, min_periods=1)
            .median()
            .to_numpy()
        )
    else:
        mag_s = mag

    # Distance in bins
    if min_distance_hz and len(freqs) > 2:
        dfreq = np.median(np.diff(freqs))
        distance_bins = max(1, int(np.ceil(min_distance_hz / dfreq)))
    else:
        distance_bins = 1

    # Prominence threshold
    if min_prominence is None:
        med = np.median(mag_s)
        mad = np.median(np.abs(mag_s - med)) + 1e-12
        min_prominence = prominence_mad_mult * mad  # smaller -> more peaks

    # --- Stage A: true peaks by prominence ---
    peaks, props = find_peaks(mag_s, prominence=min_prominence, distance=distance_bins)

    peak_idx = np.sort(peaks)

    # --- Stage B: fallback to local maxima if not enough ---
    if len(peak_idx) < n_peaks:
        # local maxima candidates (strict neighbors)
        candidates = np.where((mag_s[1:-1] > mag_s[:-2]) & (mag_s[1:-1] > mag_s[2:]))[0] + 1
        # remove already selected
        candidates = np.setdiff1d(candidates, peak_idx, assume_unique=False)

        # rank candidates by magnitude, take as many as needed
        need = n_peaks - len(peak_idx)
        if len(candidates) > 0:
            best = candidates[np.argsort(mag_s[candidates])[::-1]][:need]
            peak_idx = np.sort(np.concatenate([peak_idx, best]))

    # If still not enough (edge case), just take the top bins (excluding edges)
    if len(peak_idx) < n_peaks:
        valid = np.arange(1, len(mag_s) - 1) if len(mag_s) > 2 else np.arange(len(mag_s))
        best_bins = valid[np.argsort(mag_s[valid])[::-1]]
        for b in best_bins:
            if b not in peak_idx:
                peak_idx = np.sort(np.append(peak_idx, b))
            if len(peak_idx) >= n_peaks:
                break

    peak_idx = peak_idx[:n_peaks]

    out = sub.iloc[peak_idx][["frequency_hz", "magnitude"]].copy()
    out["magnitude_smoothed"] = mag_s[peak_idx]
    return out.reset_index(drop=True)
def fft_multi_channels(
    df: pd.DataFrame,
    signal_cols: list[str],
    time_ms_col: str = "Time [ms]",
    window: str | None = "hann",
    detrend: bool = True,
    normalize: bool = True,
) -> dict[str, pd.DataFrame]:
    """
    Compute FFT spectrum for each signal column.

    Returns
    -------
    dict[str, pd.DataFrame]
        {signal_name: spectrum_df} where spectrum_df has:
        - frequency_hz
        - magnitude
    """
    out: dict[str, pd.DataFrame] = {}
    for col in signal_cols:
        out[col] = fft_single_channel(
            df,
            signal_col=col,
            time_ms_col=time_ms_col,
            window=window,
            detrend=detrend,
            normalize=normalize,
        )
    return out


def detect_peaks_mag(mag, height=None, prominence=None, distance=None):
    """
    Detect peaks in magnitude array using SciPy.

    Parameters
    ----------
    mag : array-like
        Magnitude spectrum (FFT amplitude or dB).
    height : float, optional
        Minimum peak height.
    prominence : float, optional
        Minimum peak prominence.
    distance : int, optional
        Minimum distance between peaks (in samples).

    Returns
    -------
    peaks : np.ndarray
        Indices of detected peaks.
    prominences : np.ndarray
        Prominence of each detected peak.
    """
    peaks, properties = find_peaks(
        mag,
        height=height,
        prominence=prominence,
        distance=distance
    )

    prominences = peak_prominences(mag, peaks)[0]

    return peaks, prominences

def estimate_noise_floor(mag):
    """
    Simple robust noise estimate: median + scaled MAD.
    Works in linear scale; if mag is in dB, treat accordingly.
    """
    med = np.median(mag)
    mad = np.median(np.abs(mag - med))
    # convert mad -> approximate sigma: sigma ≈ 1.4826*MAD
    sigma = 1.4826 * mad
    return med, sigma

def find_FFT_peaks(
    df,
    n_fundamentals=3,
    max_harmonic=None,
    harmonic_tol_hz=None,
    min_prominence_factor=3.0,
    height_db=None,
    min_freq=None,
    max_freq=None
):
    """
    Detect switching fundamentals and harmonics from FFT DataFrame df
    (df.iloc[:,0] = frequency, df.iloc[:,1] = magnitude).
    Returns:
      peaks_df: DataFrame of detected peaks (peak_idx, freq, mag, prominence)
      fundamentals_df: DataFrame of selected fundamentals with harmonics list
    """
    freq_all = np.asarray(df.iloc[:, 0])
    mag_all  = np.asarray(df.iloc[:, 1])

    # frequency window
    if min_freq is None: min_freq = freq_all.min()
    if max_freq is None: max_freq = freq_all.max()
    mask = (freq_all >= min_freq) & (freq_all <= max_freq)
    freq = freq_all[mask]
    mag  = mag_all[mask]
    original_indices = np.nonzero(mask)[0]

    # noise / threshold defaults
    med, sigma = estimate_noise_floor(mag)
    default_prom = sigma * min_prominence_factor
    if height_db is not None:
        height = height_db
    else:
        height = med + 2.0 * sigma

    # distance in samples: ~1 Hz separation default (or at least 1)
    dfreq = np.median(np.diff(freq)) if len(freq) > 1 else 1.0
    default_distance = max(1, int(round(1.0 / dfreq)))

    # detect peaks using scipy
    peaks_idx_rel, props = find_peaks(mag, height=height, prominence=default_prom, distance=default_distance)
    prominences = peak_prominences(mag, peaks_idx_rel)[0] if len(peaks_idx_rel) > 0 else np.array([])

    # Build peaks dataframe (map relative indices back to original df indices)
    peaks = []
    for i_rel, rel_idx in enumerate(peaks_idx_rel):
        orig_idx = int(original_indices[rel_idx])
        p = {
            'peak_idx': orig_idx,
            'freq': float(freq[rel_idx]),
            'mag': float(mag[rel_idx]),
            'prominence': float(prominences[i_rel]) if i_rel < len(prominences) else float('nan')
        }
        peaks.append(p)
    peaks_df = pd.DataFrame(peaks).sort_values(by='freq').reset_index(drop=True)

    if peaks_df.empty:
        return peaks_df, pd.DataFrame([])

    # harmonic tolerance default
    if harmonic_tol_hz is None:
        harmonic_tol_hz = max(1.0, 0.005 * (freq.max()))

    # max harmonic default (bounded)
    if max_harmonic is None:
        min_candidate = peaks_df['freq'].min()
        if min_candidate <= 0:
            max_harmonic = 10
        else:
            max_harmonic = int(np.floor(max_freq / (min_candidate + 1e-12)))
            max_harmonic = max(3, min(max_harmonic, 50))

    # prepare arrays for fast matching
    peak_freqs = peaks_df['freq'].values
    peak_mags  = peaks_df['mag'].values

    return peak_freqs[:n_fundamentals], peak_mags[:n_fundamentals]

def add_side_table_from_arrays(
    ax,
    freqs: np.ndarray,
    mags: np.ndarray,
    n=None,
    freq_fmt="{:.3f}",
    mag_fmt="{:.3g}",
    title="Points"
):


    freqs = np.asarray(freqs)
    mags  = np.asarray(mags)

    if n is not None:
        freqs = freqs[:n]
        mags  = mags[:n]

    n_points = len(freqs)
    if n_points == 0:
        return None

    # Build table content
    cell_text = [
        [i + 1, freq_fmt.format(freqs[i]), mag_fmt.format(mags[i])]
        for i in range(n_points)
    ]
    col_labels = ["#", "Freq", "Mag"]

    # Resize main axes to make space
    fig = ax.figure
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.65, box.height])

    # Add table axes
    table_ax = fig.add_axes([
        box.x0 + box.width * 0.7,
        box.y0,
        box.width * 0.3,
        box.height
    ])
    table_ax.axis("off")

    table = table_ax.table(
        cellText=cell_text,
        colLabels=col_labels,
        loc="center",
        cellLoc="center"
    )

    table.auto_set_font_size(False)
    table.set_fontsize(6)
    table.scale(1, 1.2)

    table_ax.set_title(title, fontsize=10, pad=6)

    return table_ax



import numpy as np

def add_table_top_right(
    ax,
    freqs: np.ndarray,
    mags: np.ndarray,
    n=None,
    freq_fmt="{:.3f}",
    mag_fmt="{:.3g}",
    title="Points",
    fontsize=7,
    table_width=0.30,
    table_height=0.25
):
    freqs = np.asarray(freqs)
    mags  = np.asarray(mags)

    if n is not None:
        freqs = freqs[:n]
        mags  = mags[:n]

    if len(freqs) == 0:
        return None

    cell_text = [
        [i + 1, freq_fmt.format(freqs[i]), mag_fmt.format(mags[i])]
        for i in range(len(freqs))
    ]
    col_labels = ["#", "Freq", "Mag"]

    x0 = 1.0 - table_width - 0.02
    y0 = 1.0 - table_height - 0.02
    bbox = (x0, y0, table_width, table_height)

    table = ax.table(
        cellText=cell_text,
        colLabels=col_labels,
        cellLoc="center",
        bbox=bbox
    )

    table.auto_set_font_size(False)
    table.set_fontsize(fontsize)

    # ---- FORCE WHITE BACKGROUND ----
    for (row, col), cell in table.get_celld().items():
        cell.set_facecolor("white")
        cell.set_edgecolor("black")
        cell.set_linewidth(0.5)
        cell.set_zorder(10)   # << VERY IMPORTANT

    # --------------------------------

    # Title above table
    ax.text(
        x0,
        min(0.99, y0 + table_height + 0.01),
        title,
        transform=ax.transAxes,
        fontsize=fontsize + 1,
        fontweight="bold",
        va="bottom",
        ha="left",
        bbox=dict(facecolor="white", edgecolor="black", pad=1.5)
    )

    return table
