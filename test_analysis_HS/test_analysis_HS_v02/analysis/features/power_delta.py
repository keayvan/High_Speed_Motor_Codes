# -*- coding: utf-8 -*-
"""
Created on Thu Jan 15 17:07:05 2026

@author: kkeramati


Instantaneous and average electrical power for a delta-connected three-phase system.

Assumptions:
- Phase voltages and phase currents are measured per winding
- DataFrame already contains:
    - renamed columns (semantic names)
    - numeric values
    - optional "Time [ms]" column (not required here)
"""

from __future__ import annotations
import pandas as pd
import numpy as np

def delta_instantaneous_power(
    df: pd.DataFrame,
    v_cols = ("V_ab (V)", "V_bc (V)", "V_ac (V)"),
    i_cols = ("I_a (A)", "I_b (A)", "I_c (A)"),
) -> pd.Series:
    """
    Compute instantaneous real power for a delta-connected 3-phase system
    using line-to-line voltages and corresponding currents.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing voltage and current columns
    v_cols : tuple of str
        Column names for (V_ab, V_bc, V_ca)
    i_cols : tuple of str
        Column names for (I_ab, I_bc, I_ca) or consistent line currents

    Returns
    -------
    pd.Series
        Instantaneous real power [W]
    """

    v_ab, v_bc, v_ca = v_cols
    # i_ab, i_bc, i_ca = i_cols
    i_a, i_b, i_c = i_cols


    # p_inst = (
    #     df[v_ab] * df[i_ab]
    #     + df[v_bc] * df[i_bc]
    #     + df[v_ca] * df[i_ca]
    # )
    p_inst = 1/3*(
        (df[v_ab]-df[v_ca]) * df[i_a]
        + (df[v_bc]-df[v_ab]) * df[i_b]
        + (df[v_ca]-df[v_bc]) * df[i_c]
    )
    
    p_avg = np.mean(p_inst)

    return p_inst, p_avg


# def delta_instantaneous_power(
#     df: pd.DataFrame,
#     v_cols: tuple[str, str, str],
#     i_cols: tuple[str, str, str],
# ) -> pd.Series:
#     """
#     Compute instantaneous three-phase electrical power for delta connection.

#     p(t) = v_ab * i_ab + v_bc * i_bc + v_ca * i_ca

#     Parameters
#     ----------
#     df : pd.DataFrame
#         Input data
#     v_cols : (str, str, str)
#         Phase voltage column names (e.g. ("V_a (V)", "V_b (V)", "V_c (V)"))
#     i_cols : (str, str, str)
#         Phase current column names (e.g. ("I_a (A)", "I_b (A)", "I_c (A)"))

#     Returns
#     -------
#     pd.Series
#         Instantaneous power [W]
#     """
#     for c in (*v_cols, *i_cols):
#         if c not in df.columns:
#             raise KeyError(f"Missing column: {c}")

#     p = (
#         df[v_cols[0]] * df[i_cols[0]] +
#         df[v_cols[1]] * df[i_cols[1]] +
#         df[v_cols[2]] * df[i_cols[2]]
#     )

#     return p




