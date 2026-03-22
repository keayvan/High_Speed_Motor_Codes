# -*- coding: utf-8 -*-
"""
Created on Tue Dec 16 09:44:54 2025

@author: kkeramati
"""



from analysisPlotting_func import mat_v73_to_dataframe as mat
from analysisPlotting_func import load_many_mats_to_dfs as matM
from analysisPlotting_func import plot_from_dataframe as plot
from analysisPlotting_func import plot_many_runs_from_dfs as plotM
from analysisPlotting_func import trim_from_ramp_start as trim
from analysisPlotting_func import shift_to_zero as shift
from analysisPlotting_func import integral

import re
import pandas as pd
from matplotlib import pyplot as plt

if __name__ =='__main__':
    
    
    signals = ["B_volt", "B_amp", "Throttle", "TAS_a", "TAS_c"]

    subplot_params = ["B_volt", "B_amp", "Throttle", "TAS_a", "TAS_c", "power"]

    overlay_params = ["TAS_a", "TAS_c"]

    mat_path = "./data/Dec2025/flight_1-2025_12_11.mat"
    
    df = mat(
        mat_path,
        signals=list(set(signals))
    )
    
    
    df['power'] = df['B_volt']*df['B_amp']

    ramp_pos, ramp_time, df_trim = trim(df, 
                                         col = 'B_amp',
                                         flat_samples=300,      
                                         jump_factor=5.0,      
                                         min_jump=1.0,          
                                         baseline_tol=0.05)
    
    
    
    df_trim['Time (s)'] = df_trim.index/1e9
    df_trim_shift = shift(df_trim, time_col = 'Time (s)')
    df_trim_shift_133= df_trim_shift.iloc[:1330,:]
    df_trim_shift_133_sorted = df_trim_shift_133.sort_values(by="TAS_c")
    df_trim_shift_133_integral = integral (df_trim_shift_133,'Time (s)')
    
    mat_path = "./data/Dec2025/flight_2-2025_12_11.mat"
    
    df1 = mat(
        mat_path,
        signals=list(set(signals))
    )
    df1['power'] = df1['B_volt']*df1['B_amp']

    ramp_pos, ramp_time, df_trim1 = trim(df1, 
                                         col = 'B_amp',
                                         flat_samples=300,      
                                         jump_factor=5.0,      
                                         min_jump=1.0,          
                                         baseline_tol=0.05)
    df_trim1['Time (s)'] = df_trim1.index/1e9
    df_trim_shift1 = shift(df_trim1, time_col = 'Time (s)')
    df_trim_shift1_133= df_trim_shift1.iloc[:1330,:]
    df_trim_shift1_133_sorted = df_trim_shift1_133.sort_values(by="TAS_c")
    df_trim_shift1_133_integral = integral (df_trim_shift1_133,'Time (s)')


    
    plotM([('ARC R&D',df_trim_shift),('MGM',df_trim_shift1)], subplot_params, None, xAxis = 'Time (s)', n_cols=3)
    plotM([('ARC R&D',df_trim_shift_133),('MGM',df_trim_shift1_133)], subplot_params, None, xAxis = 'Time (s)', n_cols=3)
    plotM([('ARC R&D',df_trim_shift_133_sorted),('MGM',df_trim_shift1_133_sorted)], subplot_params, None, xAxis = 'TAS_c', n_cols=3)


    # Plot from DataFrame
    plot(
        df,
        subplot_params=subplot_params,
        overlay_params=None,
       
    )


    subplot_params = ["B_volt", "B_amp", "Throttle", "TAS_a", "TAS_c"]
    overlay_params = ["TAS_a", "TAS_c"]
    
    mat_paths = [
    "./data/Dec2025/flight_1-2025_12_11.mat",
    "./data/Dec2025/flight_2-2025_12_11.mat",  # add more here
    ]
    
    dfs = matM(mat_paths,signals)
    
    
    plotM(dfs, subplot_params, None, n_cols=3)
    

    plot(
        df_trim_shift,
        subplot_params=subplot_params,
        overlay_params=None,
        xAxis = 'Time (s)',
        axvline = 133
        )
    
    file_stm = 'C:/Users/kkeramati/OneDrive - ARQUIMEA GROUP/HSM Project/High_Speed_Motor_Codes/STM_board/result/flight.csv'
    
    lines = []
    with open(file_stm, 'r') as f:
        lines = f.readlines()
    
    # -------------------------------------------------------
    # 1) Find the header row inside the text
    # -------------------------------------------------------
    header = None
    header_index = None
    
    for i, line in enumerate(lines):
        if "timestamp" in line and "," in line:
            header = [h.strip() for h in line.strip().split(',')]
            header_index = i
            break
    
    print("Detected header:", header)
    
    # -------------------------------------------------------
    # 2) Load ONLY numeric rows after the header
    # -------------------------------------------------------
    numeric_rows = []
    for line in lines[header_index + 1:]:
        if re.match(r'\s*\d', line) and ',' in line:
            parts = [float(x) for x in line.strip().split(',')]
            numeric_rows.append(parts)
    
    # Create DataFrame with detected column names
    df_stm = pd.DataFrame(numeric_rows, columns=header)
    df_stm["Time (s)"]=df_stm["timestamp"]/1000

    ramp_pos_stm, ramp_time_stm, df_stm_trim = trim(df_stm, 
                                         col = 'current',
                                         flat_samples=300,      
                                         jump_factor=5.0,      
                                         min_jump=1.0,          
                                         baseline_tol=0.05)
    df_stm_trim_shift = shift(df_stm_trim, time_col = 'Time (s)')
    t_par = 'Time (s)'
    par1 = 'B_volt'
    par2 = 'voltage'
    plt.figure()
    plt.axvline(x=133, color = 'red',ls = '--',  label = 'T = 133 s')
    plt.plot(df_trim_shift[t_par], df_trim_shift[par1],'-o',color = 'blue', label = 'Telemetry', lw =1, ms =1)
    plt.plot(df_stm_trim_shift[t_par],df_stm_trim_shift[par2], '-o',color = 'gray', label = 'STM',lw = 2, ms= 1 , alpha = 0.7)
    plt.xlabel ('Time (s)')
    plt.ylabel('Voltage (V)')
    plt.grid()
    plt.legend()