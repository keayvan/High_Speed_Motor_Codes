#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 18 12:51:10 2025

@author: kkeramati
"""

import pandas as pd
import function
from matplotlib import pyplot as plt
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
    
    df["time (s)"] = list(range(df.shape[0]))
    params = ["time (s)", "VOLTAGE (V)", "CURRENT (A)", "SPEED (rpm)", "TEMPERATURE (C)", "POWER (W)"]
    df[params] = df[params].apply(pd.to_numeric, errors='coerce')
    df.loc[:, "SPEED (rpm)"] *= 100
    df_sorted = df.sort_values(by="SPEED (rpm)", ascending=True)

    return df, df_sorted

if __name__=="__main__":
    # filename = "Telem ESC 01_2025.csv"
    filename = "prueba 4.csv"

    df_Arc,df_Arc_sorted  = readArc_csv(filename, test = 'testbench')
    # parmPlot = ["TEMPERATURE (C)", "BEC Temperature", "Motor Temperature", "Battery Temperature"]        
    # function.plotData(df= df_Arc,
    #              x_parm = 'time (s)',
    #              y_parms= parmPlot,
    #              n_rows = 2,
    #              title = 'Raw Data',
    #              plot_type='dot')
    # parmPlot=["Input request (%)","POWER (W)", "Cruising"]
    # function.plotData(df= df_Arc,
    #              x_parm = 'time (s)',
    #              y_parms= parmPlot,
    #              n_rows = 1,
    #              title = 'Raw Data',
    #              plot_type='dot')
    
    parmPlot = ["SPEED (rpm)", "POWER (W)", "CURRENT (A)", "VOLTAGE (V)"]        
    function.plotData(df= df_Arc,
                 x_parm = 'time (s)',
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
