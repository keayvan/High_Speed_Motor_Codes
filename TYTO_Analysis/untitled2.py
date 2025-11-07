# -*- coding: utf-8 -*-
"""
Created on Mon Nov  3 11:44:54 2025

@author: kkeramati
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Sep  9 15:56:10 2025

@author: kkeramati
"""


import pandas as pd
import matplotlib.pyplot as plt
import os
import math
import numpy as np
from scipy.optimize import curve_fit, least_squares

def plot_parameters_multi(dfs, parameters, x='Time (s)', description="", n_rows=None):
    n_params = len(parameters)

    # Automatically determine grid shape if not specified
    if n_rows is None:
        n_rows = math.ceil(math.sqrt(n_params))
    n_cols = math.ceil(n_params / n_rows)

    fig, axes = plt.subplots(n_rows, n_cols, figsize=(5 * n_cols, 3 * n_rows), sharex=True)
    axes = axes.flatten() if n_params > 1 else [axes]

    colors = ['#525252ff', '#009494ff', '#0F3878', '#ff596c', '#f7941dff'
              ]

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
                    'o-', lw=1, ms=1.5,
                    color=colors[j % len(colors)],
                    label=f"{Powertrain}"
                )
            else:
                print(f"Warning: {param_col} not found in dataframe {Powertrain}")
        
        ax.set_ylabel(param)
        ax.legend(fontsize=8)
        ax.grid(True)

    # Hide unused subplots (if grid is larger than needed)
    for j in range(n_params, len(axes)):
        fig.delaxes(axes[j])

    axes[-1].set_xlabel(x)
    
    plt.suptitle(f"Results {description}", fontsize=14)
    plt.tight_layout(rect=[0, 0, 1, 0.97])
    plt.show()
    
def read_result(file_path, powertrain="MGM"):
    df = pd.read_csv(file_path)

    # Detect the common prefix in column names (excluding the first column)
    old_prefix = os.path.commonprefix(df.columns[1:].tolist())

    # Replace it with the desired powertrain name
    if old_prefix:
        new_columns = [
            col.replace(old_prefix, powertrain + " ") if col != df.columns[0] else col
            for col in df.columns
        ]
        df.columns = new_columns

    return df
    

def cycle_func(dfff, n_cycle = 2):
    df_list = []
    dff = dfff.copy()
    time = dff.iloc[0:int(len(dff)/n_cycle),0]

    for i in range(n_cycle):
        df11 = dff.iloc[i*int(len(dff)/n_cycle):(i+1)*int(len(dff)/n_cycle),:]
        df11.iloc[:,0] = time
        df_list.append(df11)
    
    return df_list

def steps_average(df0, par_step = 'ESC throttle (μs)'):
    cols = df0.columns[1:].tolist()
    Powertrain = os.path.commonprefix(cols)

    # === Compute averages per step ===
    avg_throttle = []
    avg_speed = []
    avg_torque = []
    avg_current = []
    avg_thrust = []
    avg_p_electrical = []
    avg_p_mechanical = []

    mean_min = 10
    mean_max =20

    throttle = df0[Powertrain + 'ESC throttle (μs)']
    speed = df0[Powertrain + 'rotation speed (rpm)']
    torque = df0[Powertrain + 'torque MZ (torque) (N⋅m)']
    current = df0[Powertrain + 'current (A)']
    thrust = df0[Powertrain + 'force Fz (thrust) (N)']
    p_electrical = df0[Powertrain + 'electrical power (W)']
    p_mechanical = df0[Powertrain + 'mechanical power (W)']
    
    step_changes = np.where(df0[Powertrain + par_step].diff() != 0)[0]
    step_changes = np.append(step_changes, len(df0))
    
        
    for idx in step_changes:
        avg_throttle.append(throttle.iloc[idx+mean_min:idx+mean_max].mean())
        avg_speed.append(speed.iloc[idx+mean_min:idx+mean_max].mean())
        avg_torque.append(torque.iloc[idx+mean_min:idx+mean_max].mean())
        avg_current.append(current.iloc[idx+mean_min:idx+mean_max].mean())
        avg_thrust.append(thrust.iloc[idx+mean_min:idx+mean_max].mean())
        avg_p_electrical.append(p_electrical.iloc[idx+mean_min:idx+mean_max].mean())
        avg_p_mechanical.append(p_mechanical.iloc[idx+mean_min:idx+mean_max].mean())
        # avg_throttle = np.array(avg_throttle)
        # avg_speed = np.array(avg_speed)
        # avg_torque = np.array(avg_torque)
        # avg_current = np.array(avg_current)
    
    avg_throttle = [x for x in avg_throttle if not (isinstance(x, float) and math.isnan(x))]
    avg_speed = [x for x in avg_speed if not (isinstance(x, float) and math.isnan(x))]
    avg_torque = [x for x in avg_torque if not (isinstance(x, float) and math.isnan(x))]
    avg_current = [x for x in avg_current if not (isinstance(x, float) and math.isnan(x))]
    avg_thrust =[x for x in avg_thrust if not (isinstance(x, float) and math.isnan(x))]
    avg_p_electrical = [x for x in avg_p_electrical if not (isinstance(x, float) and math.isnan(x))]
    avg_p_mechanical = [x for x in avg_p_mechanical if not (isinstance(x, float) and math.isnan(x))]
    

    return[avg_throttle, avg_speed, avg_torque, avg_current, avg_thrust, avg_p_electrical, avg_p_mechanical]
            




def steps_average1(
    df: pd.DataFrame,
    par_step: str = "ESC throttle (μs)",
    mean_min: int = 10,
    mean_max: int = 20,
    start_df = 2,
    end_df = -2
) -> pd.DataFrame:
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

    out = pd.DataFrame(rows[start_df:end_df])
    out.index = range(len(out))
    return out




def model_2d(x, a, b):
    return a*x**2+b*x

def model_3d(x, a,b,c):
    return a*x**3+b*x**2+c*x
def expo(x, a, b, c):
    return a * np.exp(b * x) + c

def robust_exponential_fit(x, y):
    # Remove NaNs / infs
    m = np.isfinite(x) & np.isfinite(y)
    x = x[m].astype(float); y = y[m].astype(float)

    # Sort by x
    order = np.argsort(x)
    x = x[order]; y = y[order]

    # Light outlier trimming on y (keeps 1..99th pct)
    # y_low, y_high = np.nanpercentile(y, [1, 99])
    # keep = (y >= y_low) & (y <= y_high)
    # x = x[keep]; y = y[keep]

    # Initial guesses via log-linearization with offset
    eps = 1e-9
    c0 = float(np.min(y)) - 0.05 * (np.ptp(y) + eps)
    yc = y - c0
    yc[yc <= eps] = np.min(yc[yc > eps]) if np.any(yc > eps) else eps
    try:
        p = np.polyfit(x, np.log(yc), 1)
        b0 = float(p[0])
        a0 = float(np.exp(p[1]))
    except Exception:
        b0 = 0.001
        a0 = max(np.ptp(y), 1.0)

    init = [a0, b0, c0]

    # Bounds
    yr = np.ptp(y) if np.ptp(y) > 0 else 1.0
    lb = [1e-12, -np.inf, np.min(y) - 5*yr - 1]
    ub = [np.inf,  np.inf, np.max(y) + 5*yr + 1]

    # Try curve_fit first
    try:
        popt, _ = curve_fit(expo, x, y, p0=init, bounds=(lb, ub), maxfev=200000)
        method = "curve_fit"
    except Exception:
        # Robust fallback
        def resid(p): return expo(x, *p) - y
        res = least_squares(resid, x0=init, bounds=(lb, ub), loss="soft_l1", f_scale=1.0, max_nfev=200000)
        if not res.success:
            raise RuntimeError("least_squares failed: " + res.message)
        popt = res.x
        method = "least_squares"
    return popt, method, x, y

# Example usage
if __name__ == "__main__":
    plt.rcParams["font.family"] = "Century Gothic"
    file_path = "./Results_TYTO/ARC_RD_100A_SVPWM_modify.csv"  # change path if needed
    df0 = read_result(file_path, powertrain='ARC_RD_SVPWM')
    
    file_path = "./Results_TYTO/MGM_100A_steps5s.csv"  # change path if needed
    df1 = read_result(file_path, powertrain='MGM')
    
    file_path = "./Results_TYTO/ARC_RD_100A_DPWM_min_modify.csv"  # change path if needed
    df2 = read_result(file_path, powertrain='ARC_RD_DPWM')
    
    plot_parameters_multi([df1], [
        'electrical power (W)',
        'voltage (V)',
        'current (A)',
        'ESC throttle (μs)',
        'rotation speed (rpm)',
        'force Fz (thrust) (N)',
        'torque MZ (torque) (N⋅m)',
        'powertrain efficiency (N/W)'
        ],n_rows =3,
        x='rotation speed (rpm)')
    
    plot_parameters_multi([df2], [
        'electrical power (W)',
        'voltage (V)',
        'current (A)',
        'ESC throttle (μs)',
        'rotation speed (rpm)',
        'force Fz (thrust) (N)',
        'torque MZ (torque) (N⋅m)',
        'powertrain efficiency (N/W)'
        ],n_rows =3,
        x='rotation speed (rpm)')
    
    SVPWM = steps_average(df0, par_step = 'ESC throttle (μs)')
    MGM_ave = steps_average(df1, par_step = 'ESC throttle (μs)')
    MGM_ave = [x[:-2] for x in MGM_ave]
    DPWM_ave = steps_average(df2, par_step = 'ESC throttle (μs)')
  
    
  
    MGM_ave1 = steps_average1(
        df = df1,
        par_step="ESC throttle (μs)",
        mean_min = 10,
        mean_max = 20,
        start_df = 1,
        end_df = -2
    ) 
    

    
    plt.figure()
    plt.plot(df1[ 'MGM rotation speed (rpm)'], df1['MGM current (A)'],'.', alpha = 0.3)
    plt.plot(MGM_ave1['MGM rotation speed (rpm)'], MGM_ave1['MGM current (A)'],'o',ms=5, color = 'red')
    # plt.plot(MGM_ave[1], MGM_ave[3], 'o',mfc='red', alpha = 0.6, ms=3)

    
    
    
    coeffs_DPWM = np.polyfit(DPWM_ave[1], DPWM_ave[3],  3)   # quadratic fit
    poly_fit_DPWM = np.poly1d(coeffs_DPWM)
    
    speed_fit = np.linspace(0, 15000, 200)

    params_DPWM, _ = curve_fit(model_2d,DPWM_ave[1], DPWM_ave[3], bounds=(0, np.inf))
    a, b = params_DPWM

    fit_2nd_DPWM = model_2d (speed_fit,a, b )
    
    speed_fit_DPWM = poly_fit_DPWM(speed_fit)

    x = np.array(DPWM_ave[1])
    y = np.array(DPWM_ave[3])
    (a, b, c), method, x_clean, y_clean = robust_exponential_fit(x, y)
    y_pred = expo(x_clean, a, b, c)
    ss_res = float(np.sum((y_clean - y_pred) ** 2))
    ss_tot = float(np.sum((y_clean - np.mean(y_clean)) ** 2))
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else float('nan')
    
    y_pred_DPWM = expo(speed_fit, a, b, c)
    print('***************************************')
    print(f'DPWM exponential coeficent: a = {a:.2f}, b= {b:.5f}, c={c:.4f}')
    print('***************************************')

    

    plt.figure()
    plt.plot(DPWM_ave[1], DPWM_ave[3], 'o-', label = 'experimental')
    # plt.plot(speed_fit_MGM,current_MGM_fit_3rd , 'o-', label = 'order 3')
    # plt.plot(speed_fit_MGM, current_MGM_fit_2rd, 'o-', label = 'order 2')
    # plt.plot(speed_fit, current_MGM_fit_3rd_new, label = 'order 3_v2')
    plt.plot(speed_fit, y_pred_DPWM, label = 'DPWM_fit_exppnential')


    plt.title('DPWM Electronics')
    plt.grid()
    plt.legend()
    
    

        

    coeffs_MGM = np.polyfit(MGM_ave[1], MGM_ave[3], 3)   # quadratic fit
    poly_fit_MGM = np.poly1d(coeffs_MGM)
    
    current_MGM_fit_3rd = poly_fit_MGM(speed_fit)
    
    
    params_MGM, _ = curve_fit(model_2d,MGM_ave[1], MGM_ave[3], bounds=(0, np.inf))
    a, b = params_MGM
    current_MGM_fit_2rd = model_2d (speed_fit,a, b )
    
    param_MGM_3d,_ = curve_fit(model_3d, MGM_ave[1], MGM_ave[3], bounds=(0, np.inf))
    a,b,c = param_MGM_3d
    current_MGM_fit_3rd_new = model_3d (speed_fit,a,b,c)
    
    x = np.array(MGM_ave[1])
    y = np.array(MGM_ave[3])
    (a, b, c), method, x_clean, y_clean = robust_exponential_fit(x, y)
    y_pred = expo(x_clean, a, b, c)
    ss_res = float(np.sum((y_clean - y_pred) ** 2))
    ss_tot = float(np.sum((y_clean - np.mean(y_clean)) ** 2))
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else float('nan')
    
    y_pred_MGM = expo(speed_fit, a, b, c)
    
    plt.figure()
    plt.plot(MGM_ave[0], 'o-')
    plt.figure()
    plt.plot(df1['MGM rotation speed (rpm)'],df1['MGM current (A)'], '.', alpha=0.3, label="Raw data")
    plt.plot(MGM_ave[1], MGM_ave[3], 'o',color='#00d0b8',mfc='#0AFFA0',mec='#0FAAF0',lw=2,ms=6, label="Step averages")

    print('***************************************')
    print(f'MGM exponential coeficent: a = {a:.2f}, b= {b:.5f}, c={c:.4f}')
    print('***************************************')

    plt.figure()
    plt.plot(MGM_ave[1], MGM_ave[3], 'o-', label = 'experimental')
    # plt.plot(speed_fit_MGM,current_MGM_fit_3rd , 'o-', label = 'order 3')
    # plt.plot(speed_fit_MGM, current_MGM_fit_2rd, 'o-', label = 'order 2')
    plt.plot(speed_fit, current_MGM_fit_3rd_new, label = 'order 3_v2')
    plt.plot(speed_fit, y_pred_MGM, label = 'MGM_fit_exppnential')


    plt.title('MGM Electronics')
    plt.grid()
    plt.legend()
    
    
    plt.figure()
    plt.plot(speed_fit, speed_fit_DPWM, label = 'ARC_RD_DPWM')
    plt.plot(speed_fit, current_MGM_fit_3rd, label = 'MGM')
    plt.xlabel('Rotational speed (rpm)')
    plt.ylabel('Current (A)')
    plt.legend()
    plt.grid()
    

    
    result_3d = [abs(y - x)/x*100 for x, y in zip(current_MGM_fit_3rd, speed_fit_DPWM)]
    

    plt.figure()
    # plt.plot(SVPWM[1], SVPWM[3], 'o-', label = 'ARC_RD_SVPWM')
    plt.plot(DPWM_ave[1], DPWM_ave[3], 'o',color = 'red', label = 'ARC_RD_DPWM')
    plt.plot(speed_fit, y_pred_DPWM,color = 'red', label = 'DPWM_fit_exppnential')

    plt.plot(MGM_ave[1], MGM_ave[3],'x',color = 'blue',  label = 'MGM')
    plt.plot(speed_fit, y_pred_MGM,color = 'blue', label = 'MGM_fit_exppnential')

    plt.xlabel('Rotational speed (rpm)')
    plt.ylabel('Current (A)')

    plt.legend()
    plt.grid()
    
    result_exponential = [abs(y - x)/x*100 for x, y in zip(y_pred_MGM, y_pred_DPWM)]
    
    plt.figure()
    plt.plot(speed_fit[40:],result_exponential[40:],'o-',c='red',ms=2,mfc='blue',mec='blue')
    plt.grid()
    plt.xlabel('Rotational speed (rpm)')
    plt.ylabel('Current reduction %')
