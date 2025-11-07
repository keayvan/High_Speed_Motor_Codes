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

def plot_parameters_multi(dfs, parameters, x='Time (s)', description="", n_rows=None,ms=1.5):
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
                    'o-', lw=1, ms=ms,
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

def steps_average(
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
    out = pd.DataFrame(rows[start_df:])

    if end_df !=None:
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

def fitting_expo (df, x_param, y_param, v_output = (0,15000)):

    speed_fit = np.linspace(v_output[0], v_output[1], 200)
    cols = df.columns[1:].tolist()
    powertrain = os.path.commonprefix(cols)
    x = np.array(df[powertrain+x_param])
    y = np.array(df[powertrain+y_param])
    (a, b, c), method, x_clean, y_clean = robust_exponential_fit(x, y)
    y_pred = expo(x_clean, a, b, c)
    ss_res = float(np.sum((y_clean - y_pred) ** 2))
    ss_tot = float(np.sum((y_clean - np.mean(y_clean)) ** 2))
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else float('nan')
    
    y_pred_MGM = expo(speed_fit, a, b, c)
    print('***************************************')
    print(f'{powertrain} exponential coeficent: a = {a:.2f}, b= {b:.5f}, c={c:.4f}')
    print (f'r2={r2}')
    print('***************************************')
    return speed_fit, y_pred_MGM

def analysis_fit_compare(file_name, powertrain, x_par, y_par):
    file_path = f"./Results_TYTO/{file_name}.csv"  # change path if needed
    df4 = read_result(file_path, powertrain)
    ave =steps_average(df = df4,
            par_step="ESC throttle (μs)",
            mean_min = 10,
            mean_max = 20,
            start_df = 0,
            end_df = None)
    speed_fit, y_pred = fitting_expo (df =ave,
                                          x_param = x_par,
                                          y_param = y_par,
                                          v_output = (0,15000))
    x1_plot = speed_fit
    y1_plot = y_pred
    x2_plot = ave[powertrain+' '+x_par]
    y2_plot = ave[powertrain+' '+y_par]
    
    return df4, ave, [x1_plot,y1_plot], [x2_plot,y2_plot]

# Example usage
if __name__ == "__main__":
    plt.rcParams["font.family"] = "Century Gothic"
    
    
    file_path = "./Results_TYTO/MGM_100A_steps5s.csv"  # change path if needed
    df0 = read_result(file_path, powertrain='MGM')
    
    file_path = "./Results_TYTO/ARC_RD_100A_DPWM_min_modify.csv"  # change path if needed
    df1 = read_result(file_path, powertrain='ARC_RD_DPWM')
    
    file_path = "./Results_TYTO/ARC_RD_100A_SVPWM_modify.csv"  # change path if needed
    df2 = read_result(file_path, powertrain='ARC_RD_SVPWM')
    
    file_path = "./Results_TYTO/ARC_RD_20kHz_withCalibration_steps.csv"  # change path if needed
    df3 = read_result(file_path, powertrain='ARC_20kHz')
    
    file_path = "./Results_TYTO/ARC_STM20kHz_SCP04_Magnet4_DPWM_MIN_flightScenario_2sStepsv.csv"  # change path if needed
    df4 = read_result(file_path, powertrain='flightTest')
    
    
    plot_parameters_multi([df0], [
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
    
    plot_parameters_multi([df3], [
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
    
    plot_parameters_multi([df4.iloc[:4000,:]], [
        'electrical power (W)',
        'voltage (V)',
        'current (A)',
        'ESC throttle (μs)',
        'rotation speed (rpm)',
        'force Fz (thrust) (N)',
        'torque MZ (torque) (N⋅m)',
        'powertrain efficiency (N/W)'
        ],n_rows =3,
        x='Time (s)')
    
    plot_parameters_multi([df4], [
        'electrical power (W)',
        'voltage (V)',
        'current (A)',
        'ESC throttle (μs)',
        'rotation speed (rpm)',
        'force Fz (thrust) (N)',
        'torque MZ (torque) (N⋅m)',
        'powertrain efficiency (N/W)'
        ],n_rows =3,
        x='ESC throttle (μs)')
    
    MGM_ave = steps_average(df = df0,
        par_step="ESC throttle (μs)",
        mean_min = 5,
        mean_max = 45,
        start_df = 1,
        end_df = -2)
    
    DPWM_ave = steps_average(df = df1,
        par_step="ESC throttle (μs)",
        mean_min = 10,
        mean_max = 20,
        start_df = 1,
        end_df = -1)
    
    SVPWM_ave = steps_average(df = df2,
        par_step="ESC throttle (μs)",
        mean_min = 10,
        mean_max = 20,
        start_df = 1,
        end_df = -2)
    
    ARC_20kHz_ave =steps_average(df = df3,
            par_step="ESC throttle (μs)",
            mean_min = 10,
            mean_max = 20,
            start_df = 0,
            end_df = None)
    
    speed_fit_MGM, y_pred_MGM = fitting_expo (df =MGM_ave,
                                          x_param = 'rotation speed (rpm)',
                                          y_param = 'current (A)',
                                          v_output = (0,15000))
    
    speed_fit_DPWM, y_pred_DPWM = fitting_expo (df =DPWM_ave,
                                          x_param = 'rotation speed (rpm)',
                                          y_param = 'current (A)',
                                          v_output = (0,15000))
    
    speed_fit_20kHz, y_pred_20kHz = fitting_expo (df =ARC_20kHz_ave,
                                          x_param = 'rotation speed (rpm)',
                                          y_param = 'current (A)',
                                          v_output = (0,15000))
    
    
    plt.figure()
    plt.plot(df0['MGM rotation speed (rpm)'], df0['MGM current (A)'],'.', alpha = 0.3,label = 'experimental')
    plt.plot(MGM_ave['MGM rotation speed (rpm)'], MGM_ave['MGM current (A)'],'o',ms=5, color = 'red',label = 'steps_average')
    plt.plot(speed_fit_MGM, y_pred_MGM, color = '#00d0b8', label = 'Exponential fitting')
    plt.title('MGM results')
    plt.legend()
    plt.grid(True)  
    
    plt.figure()
    plt.plot(df1['ARC_RD_DPWM rotation speed (rpm)'], df1['ARC_RD_DPWM current (A)'],'.', alpha = 0.3,label = 'experimental')
    plt.plot(DPWM_ave['ARC_RD_DPWM rotation speed (rpm)'], DPWM_ave['ARC_RD_DPWM current (A)'],'o',ms=5, color = 'red',label = 'steps_average')
    plt.plot(speed_fit_DPWM, y_pred_DPWM, color = '#00d0b8', label = 'Exponential fitting')
    plt.title('ARC_RD_DPWM results')
    plt.legend()
    plt.grid(True)  
    
    plt.figure()
    plt.plot(speed_fit_MGM, y_pred_MGM, color = '#0F3878', label = 'MGM Exponential fitting')
    plt.plot(MGM_ave['MGM rotation speed (rpm)'], MGM_ave['MGM current (A)'],'o',ms=5, color = '#0f75bcff',label = 'MGM steps_average')
    plt.plot(speed_fit_DPWM, y_pred_DPWM, color = '#00d0b8', label = 'SG Exponential fitting')
    plt.plot(DPWM_ave['ARC_RD_DPWM rotation speed (rpm)'], DPWM_ave['SG current (A)'],'o',ms=5, color = '#f74242ff',label = 'ARC_RD_DPWM steps_average')
    plt.title('Results comparision')
    plt.legend()
    plt.grid(True)  
    
    plt.figure()
    plt.plot(speed_fit_MGM, y_pred_MGM, color = '#0F3878', label = 'MGM Exponential fitting')
    plt.plot(MGM_ave['MGM rotation speed (rpm)'], MGM_ave['MGM current (A)'],'o',ms=5, color = '#0f75bcff',label = 'MGM steps_average')
    plt.plot(speed_fit_20kHz, y_pred_20kHz, color = '#00d0b8', label = 'STM_20kHz Exponential fitting')
    plt.plot(ARC_20kHz_ave['ARC_20kHz rotation speed (rpm)'], ARC_20kHz_ave['ARC_20kHz current (A)'],'o',ms=5, color = '#f74242ff',label = 'STM_20kHz steps_average')
    plt.title('Results comparision')
    plt.legend()
    plt.grid(True) 




    
    result_expo = [abs(y - x)/x*100 for x, y in zip(y_pred_MGM, y_pred_DPWM)]
    
    result_expo1 = [abs(y - x)/x*100 for x, y in zip(y_pred_MGM, y_pred_20kHz)]

   
    plt.figure()
    plt.plot(speed_fit_DPWM[40:],result_expo[40:],'o-',c='orange',ms=2,mfc='gray',mec='gray', label = 'SG_MGM')
    plt.plot(speed_fit_20kHz[40:],result_expo1[40:],'o-',c='red',ms=2,mfc='blue',mec='blue', label = 'STM_20kHz_MGM')

    plt.grid()
    plt.xlabel('Rotational speed (rpm)')
    plt.ylabel('Current reduction %')
    plt.title('abs(I_DPWM-I_MGM)/I_MGM*100')
    plt.legend()
    
    plot_parameters_multi([MGM_ave,DPWM_ave], [
        'electrical power (W)',
        'voltage (V)',
        'current (A)',
        'ESC throttle (μs)',
        'rotation speed (rpm)',
        'force Fz (thrust) (N)',
        'torque MZ (torque) (N⋅m)',
        'electrical power (W)',
        'mechanical power (W)',
        'propeller efficiency (N/W)',
        'motor & ESC efficiency (%)',
        'powertrain efficiency (N/W)'
        ],n_rows =3,
        x='rotation speed (rpm)',
        ms=4)
    
    plot_parameters_multi([MGM_ave,DPWM_ave], [
        'electrical power (W)',
        'mechanical power (W)',
        'propeller efficiency (N/W)',
        'motor & ESC efficiency (%)',
        'powertrain efficiency (N/W)'
        ],n_rows =3,
        x='Time (s)',
        ms = 4)
    
    # MGM_ave.to_csv('./Results_TYTO/Post/MGM_ave.csv')
    
    powertrain1 = 'ARC_20kHz_encoder'
    file_path = "./Results_TYTO/ARC_STM_20kHz_encoderMechanical_SCP04_Magnet4mm.csv"  # change path if needed
    df4 = read_result(file_path, powertrain=powertrain1)
    
    plot_parameters_multi([df4], [
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
    
    ARC_20kHz_encoder_ave =steps_average(df = df4,
            par_step="ESC throttle (μs)",
            mean_min = 10,
            mean_max = 20,
            start_df = 0,
            end_df = None)
    
    speed_fit_20kHz_encoder, y_pred_20kHz_encoder = fitting_expo (df =ARC_20kHz_encoder_ave,
                                          x_param = 'rotation speed (rpm)',
                                          y_param = 'current (A)',
                                          v_output = (0,15000))
    plt.figure()
    plt.plot(speed_fit_MGM, y_pred_MGM, color = '#0F3878', label = 'MGM Exponential fitting')
    plt.plot(MGM_ave['MGM rotation speed (rpm)'], MGM_ave['MGM current (A)'],'o',ms=5, color = '#0f75bcff',label = 'MGM steps_average')
    plt.plot(speed_fit_20kHz_encoder, y_pred_20kHz_encoder, color = '#00d0b8', label = 'STM_20kHz_encoder Exponential fitting')
    plt.plot(ARC_20kHz_encoder_ave['ARC_20kHz_encoder rotation speed (rpm)'], ARC_20kHz_encoder_ave['ARC_20kHz_encoder current (A)'],'o',ms=5, color = '#f74242ff',label = 'STM_20kHz_encoder steps_average')
    
    
    plt.title('Results comparision')
    plt.legend()
    plt.grid(True) 


    
    
   
 
    file_names = ['ARC_STM_20kHz_encoderMechanical_SCP04_Magnet4mm','MGM_100A_steps5s','ARC_STM20kHz_SCP04_Magnet4_DPWM_MIN_test2']
    powetrains = ['ARC_20kHz_encoder','MGM','DPWM_MIN']
    plt.figure()
    plt.legend()
    plt.grid(True)
    fitting_all = []
    for i, v in enumerate(file_names):
        df, ave, fitting, ave_expr = analysis_fit_compare(file_name=file_names[i],
                                      powertrain=powetrains[i],
                                      x_par = 'rotation speed (rpm)',
                                      y_par = 'current (A)')
        fitting_all.append(fitting)
        plt.plot(fitting[0],fitting[1], label = powetrains[i]+'_exponential fitting')
        plt.plot(ave_expr[0],ave_expr[1],'o', label = powetrains[i]+'_experimental')
        plt.legend()
    
   
    
    skip = 40
    ref_I = ['MGM','MGM']
    curve_I = ['ARC_20kHz_encoder', 'SVPWM']
    plt.figure()

    for i in range(len(curve_I)):
        f1 = powetrains.index(ref_I[i])
        f2 = powetrains.index(curve_I[i])
        result_exponential = [abs(((x) - (y))/(x))*100 for x, y in zip(fitting_all[f1][1], fitting_all[f2][1])][skip:]
        xx = fitting_all[0][0][skip:]
        
        plt.plot(xx,result_exponential,'o-',ms =2, label = curve_I[i]+'_'+ref_I[i])
        plt.grid(True)
        plt.xlabel('Rotational speed (rpm)')
        plt.ylabel('Current reduction %')
        plt.title('abs(I_DPWM-I_MGM)/I_MGM*100')
        plt.legend()

