# -*- coding: utf-8 -*-
"""
Created on Thu Jan 15 17:26:17 2026

@author: kkeramati

DC power feature.

P_dc(t) = V_dc(t) * I_dc(t)
"""

import numpy as np
import pandas as pd


def dc_power_instantaneous(
    df: pd.DataFrame,
    vdc_col: str = "DC Bus (V)",
    idc_col: str = "DC Current (A)",
    out_col: str = "DC Power (W)",
) -> pd.Series:
    """
    Compute instantaneous DC power and return it as a Series.
    """
    if vdc_col not in df.columns:
        raise KeyError(f"Missing column: {vdc_col}")
    if idc_col not in df.columns:
        raise KeyError(f"Missing column: {idc_col}")

    vdc = pd.to_numeric(df[vdc_col], errors="coerce")
    idc = pd.to_numeric(df[idc_col], errors="coerce")
    
    return vdc * idc
def dc_power_inst_ave(
    df: pd.DataFrame,
    vdc_col: str = "DC Bus (V)",
    idc_col: str = "DC Current (A)",
    out_col: str = "DC Power (W)",
) -> pd.Series:
    """
    Compute instantaneous DC power and return it as a Series.
    """
    if vdc_col not in df.columns:
        raise KeyError(f"Missing column: {vdc_col}")
    if idc_col not in df.columns:
        raise KeyError(f"Missing column: {idc_col}")

    vdc = pd.to_numeric(df[vdc_col], errors="coerce")
    idc = pd.to_numeric(df[idc_col], errors="coerce")
    
    return vdc * idc, float(np.nanmean(vdc * idc))

def add_dc_power_column(
    df: pd.DataFrame,
    vdc_col: str = "DC Bus (V)",
    idc_col: str = "DC Current (A)",
    out_col: str = "DC Power (W)",
) -> pd.DataFrame:
    """
    Return a copy of df with an added DC Power column.
    """
    out = df.copy()
    out[out_col] = dc_power_instantaneous(out, vdc_col=vdc_col, idc_col=idc_col, out_col=out_col)
    return out


def dc_power_mean(
    df: pd.DataFrame,
    vdc_col: str = "DC Bus (V)",
    idc_col: str = "DC Current (A)",
) -> float:
    """
    Mean DC power over the dataframe (ignores NaN).
    """
    p = dc_power_instantaneous(df, vdc_col=vdc_col, idc_col=idc_col)
    return float(np.nanmean(p))
