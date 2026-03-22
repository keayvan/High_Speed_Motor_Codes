#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 18 12:51:10 2025

@author: kkeramati
"""

import pandas as pd
import function
from matplotlib import pyplot as plt
import re
import numpy as np

def to_seconds(time_str):
    minutes = seconds = milliseconds = 0
    match = re.search(r'(\d+)m', time_str)
    if match:
        minutes = int(match.group(1))
    match = re.search(r'(\d+)s', time_str)
    if match:
        seconds = int(match.group(1))
    match = re.search(r'(\d+)ms', time_str)
    if match:
        milliseconds = int(match.group(1))
    return minutes * 60 + seconds + milliseconds / 1000.0
def readArc_csv(filename, cols=None, test = 'flight'):
    fldr_path = "./data/ARC_Defence_data/"

    df = pd.read_csv(fldr_path+filename, skiprows=9)
    if test == 'flight':
        df.columns = [
            "Unknown0","Time_sms","VOLTAGE (V)", "CURRENT (A)","SPEED (rpm)",
            "TEMPERATURE (C)", "BEC Voltage", "BEC Current",
            "BEC Temperature", "Input request (%)","POWER (W)",
            "Cruising", "Motor Temperature", "Battery Temperature", "Output power",
            "Automatic regulation", "I*T fuse", "Low voltage", "High current",
            "ESC overheated", "Motor overheated", "Battery overheated", "HW current fuse",
            "HW overvoltage/undervoltage","Pulse current"]
    elif test == 'testbench':
        df.columns = [
            "Unknown0","Time_sms","VOLTAGE (V)", "CURRENT (A)", "SPEED Wrong","SPEED (rpm)",
            "TEMPERATURE (C)", "Peak current", "Battery internal voltage",
            "Main bus voltage", "Input request","POWER (W)",
            "Unknown1", "Unknown2", "Unknown3", "Unknown4",
            "Unknown5", "Unknown6", "Unknown7", "Unknown8",
            "Unknown9", "Unknown10", "Unknown11", "Unknown12",
            "Unknown13", "Pulse current"]
        
            
    if cols is not None:
        df.columns = cols
    
    df["Time (s)"] = [x/10 for x in (range(df.shape[0]))]

    params = ["Time (s)", "VOLTAGE (V)", "CURRENT (A)", "SPEED (rpm)", "TEMPERATURE (C)", "POWER (W)"]
    df[params] = df[params].apply(pd.to_numeric, errors='coerce')
    df.loc[:, "SPEED (rpm)"] *= 100
    df_sorted = df.sort_values(by="SPEED (rpm)", ascending=True)

    return df, df_sorted

def expo_inverse(z, a, b, c):
        return (1 / b) * np.log((z - c) / a)
if __name__=="__main__":
    plt.rcParams["font.family"] = "Century Gothic"

    filename = "Telem ESC 01_2025.csv"
    # filename = "prueba 4.csv"

    df_Arc,df_Arc_sorted  = readArc_csv(filename, test = 'flight')
    # parmPlot = ["TEMPERATURE (C)", "BEC Temperature", "Motor Temperature", "Battery Temperature"]        
    # function.plotData(df= df_Arc,
    #              x_parm = 'Time (s)',
    #              y_parms= parmPlot,
    #              n_rows = 2,
    #              title = 'Raw Data',
    #              plot_type='dot')
    # parmPlot=["Input request (%)","POWER (W)", "Cruising"]
    # function.plotData(df= df_Arc,
    #              x_parm = 'Time (s)',
    #              y_parms= parmPlot,
    #              n_rows = 1,
    #              title = 'Raw Data',
    #              plot_type='dot')
    
    parmPlot = ["SPEED (rpm)", "POWER (W)", "CURRENT (A)", "VOLTAGE (V)"]        
    function.plotData(df= df_Arc,
                 x_parm = 'Time (s)',
                 y_parms= parmPlot,
                 n_rows = 2,
                 title = 'Raw Data',
                 plot_type='dot')
    
    function.plotData(df= df_Arc_sorted,
                 x_parm = 'SPEED (rpm)',
                 y_parms= parmPlot,
                 n_rows = 2,
                 title = 'Sorted Data by Speed')
    
    x_param = 'SPEED (rpm)'
    y_params = ["POWER (W)","CURRENT (A)"]
    expan_factor = 0.01
    curveTofit = "4D"
    # x_new = np.linspace(0, 18000,18001)
    x_new = None
    bound_max_all_3D, bound_min_all_3D,coef_max, coef_min,params = function.boundary_curve(df_Arc_sorted,x_param,y_params,x_new, expan_factor,curveTofit)
    
    fig2, axes2 = plt.subplots(1, 2, figsize=(20, 14))
    function.plotData(df= df_Arc_sorted,
                 x_parm = 'SPEED (rpm)',
                 y_parms= ['POWER (W)',"CURRENT (A)"],
                 upper_bound = bound_max_all_3D,
                 lower_bound = bound_min_all_3D,
                 x_new= x_new,
                 n_rows = 1,
                 title = 'Boundary Fitting',
                 plot_type='dot',
                 fig = fig2,
                 axes=axes2)

    parameter = 'POWER (W)'
    speed= 8000
    speed, p_max_mts, p_min_mts = function.valueSpeed(speed, parameter,
                                                      coef_max, coef_min,
                                                      params,
                                                      label = 'ARC Defence',
                                                      typef=curveTofit)
    axes21 = axes2.flatten()
    axes21[0].scatter([speed,speed],[p_max_mts,p_min_mts],s = 50, color= 'orange', edgecolor = "black")
    axes21[0].axvline(speed, linestyle = '--', label= f'@{speed}rpm')
    axes21[0].legend()

    
    range_min = 1000
    range_max = 2000
    scaled_param = df_Arc["SPEED (rpm)"]
    df_Arc["Powertrain 1 ESC throttle - target (μs)_scaled"] =scaled_param *(range_max-range_min)/(scaled_param.max()-scaled_param.min())+range_min
    
    df_Arc["Powertrain 1 ESC throttle - target (μs)"] = (scaled_param+scaled_param.max())/scaled_param.max()*1000
    
    scaled_param1 = df_Arc['Input request (%)']
    df_Arc["Powertrain 1 ESC throttle - target (μs)_request"] =scaled_param1 *(range_max-range_min)/(scaled_param1.max()-scaled_param1.min())+range_min

    
    parmPlot = ["Input request (%)", "Powertrain 1 ESC throttle - target (μs)","SPEED (rpm)"]  
    
    plt.figure()
    plt.plot(df_Arc['Time (s)'],df_Arc["Powertrain 1 ESC throttle - target (μs)"], 'red', label = 'ARC R&D')
    # plt.plot(df_Arc['Time (s)'],df_Arc["Powertrain 1 ESC throttle - target (μs)_scaled"], 'blue', label = 'ARC R&D scaled')
    plt.plot(df_Arc['Time (s)'],df_Arc["Powertrain 1 ESC throttle - target (μs)_request"],'gray', label= 'MGM ')
    plt.legend()
    plt.grid(True)
    plt.xlabel('Time (s)')
    plt.ylabel('ESC Throttle Input(μs)')

   
    function.plotData(df= df_Arc,
                 x_parm = 'Time (s)',
                 y_parms= parmPlot,
                 n_rows = 1,
                 title = 'Throttle (%)',
                 plot_type='line')
    
    print('***************************************')
    print(f'mean_Throttle ={df_Arc["Powertrain 1 ESC throttle - target (μs)"].mean()}')
    print('***************************************')

    df_throttle1 = df_Arc[["Time (s)" , "Powertrain 1 ESC throttle - target (μs)"]]
    df_throttle = df_throttle1.copy()

    df_throttle["Take sample"] = " "
    df_throttle = df_throttle[["Time (s)", "Take sample", "Powertrain 1 ESC throttle - target (μs)"]]

    fldr_save = './data/resultsArcDef/'
    df_throttle.to_csv(f"{fldr_save}throthle20.csv", index=False)  # index=False avoids writing row numbers

    df_time = df_throttle.copy()
    df_time.index = pd.to_timedelta(df_time["Time (s)"], unit="s")
    nearest_df = df_time.resample("0.001S").nearest()
    # nearest_df.to_csv(f"{fldr_save}throttle_nearest.csv", index=False)

    mean_df    = df_time.resample("1S").mean(numeric_only=True)  
    # mean_df.to_csv(f"{fldr_save}throttle_mean.csv", index=False)
    
    interp_df = (
        df_time.select_dtypes(include="number")
        .resample("1S")
        .interpolate(method="linear")
    )
    interp_df.to_csv(f"{fldr_save}throttle_linear.csv", index=False)

    a= 2.5064964103154286
    b= 0.0002449555769040284
    c = -3.434215630385792
   
    plt.figure()
    request = df_Arc_sorted['Input request (%)']
    speed_org = df_Arc_sorted['SPEED (rpm)']
    plt.plot(request,speed_org , '.')
    
    throttle_predicted = expo_inverse(speed_org,a,b,c)
    
    plt.figure()
    plt.plot(throttle_predicted, speed_org)
    