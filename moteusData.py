#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 18 17:31:41 2025

@author: kkeramati
"""
import pandas as pd
import function
from matplotlib import pyplot as plt
def process_csv_files(files):

    def read_and_process(filename):
        fldr_path = './data/resultMoteus/'
        df = pd.read_csv(fldr_path+filename)
        df['time'] = pd.to_numeric(df['time'])
        df['VELOCITY'] = df['VELOCITY'] * 60  # Convert velocity to RPM
        df['CURRENT'] = df['POWER'] / df['VOLTAGE']  # Compute Current
        df['Sampling_rate'] = df['time'].diff()  # Compute Sampling Rate
        df.rename(columns={'time': 'time (s)',
                           'VELOCITY': 'SPEED (rpm)',
                           'CURRENT': 'CURRENT (A)',
                           'VOLTAGE': 'VOLTAGE (V)',
                           'POWER': 'POWER (W)'},
                            inplace=True)


        return df
    csv_files = [f"{file}.csv" if not file.endswith('.csv') else file for file in files]

    dataframes = [read_and_process(file) for file in csv_files]
    dataframes_sorted = [df.sort_values(by="SPEED (rpm)", ascending=True) for df in dataframes]

    return dataframes, dataframes_sorted
if __name__=="__main__":

    filenames = ['KPKIV38', 'KPKIV34']  # List of CSV files (without .csv extension)
    df,df_sorted = process_csv_files(filenames)
    
    fig, axes = plt.subplots(2, 2, figsize=(20, 14))
    for i, u in enumerate(filenames):
        function.plotData(df[i],
                     x_parm= 'time (s)',
                     y_parms= ['SPEED (rpm)','POWER (W)', 'CURRENT (A)', 'VOLTAGE (V)'],
                     upper_bound=None,
                     lower_bound=None,
                     x_new = None,
                     n_rows = 2,
                     title = 'Data',
                     plot_type = 'line',
                     fig= fig,
                     axes = axes,
                     label = u,
                     colorCode = i,
                     annotation_max=True)
        
    fig, axes = plt.subplots(2, 2, figsize=(20, 14))
    fig1, axes1 = plt.subplots(1, 2, figsize=(20, 14))
    
    for i, u in enumerate(filenames):
        function.plotData(df[i],
                     x_parm= 'time (s)',
                     y_parms= ['TORQUE', 'TEMPERATURE', 'POSITION', 'Sampling_rate'],
                     upper_bound=None,
                     lower_bound=None,
                     x_new = None,
                     n_rows = 2,
                     title = 'Data',
                     plot_type = 'line',
                     fig= fig,
                     axes = axes,
                     label = u,
                     colorCode = i,
                     annotation_max=True)
       
        function.plotData(df[i],
                     x_parm= 'time (s)',
                     y_parms= ['Q_CURRENT', 'D_CURRENT'],
                     upper_bound=None,
                     lower_bound=None,
                     x_new = None,
                     n_rows = 2,
                     title = 'Data',
                     plot_type = 'line',
                     fig= fig1,
                     axes = axes1,
                     label = u,
                     colorCode = i,
                     annotation_max=True)
    
    x_param = 'SPEED (rpm)'
    y_params = ['TORQUE',"POWER (W)","CURRENT (A)"]
    expan_factor = 0.1
    curveTofit = "3D"
    import numpy as np
    x_new = np.linspace(0, 16000,16001)
    x_new = None
    bound_max_all_3D, bound_min_all_3D,coef_max, coef_min,params = function.boundary_curve(df_sorted[0],x_param,y_params,x_new, expan_factor,curveTofit)
    
    
    
    
    
        
    parameter = 'POWER (W)'
    speed= 8000
    speed, p_max_mts, p_min_mts = function.valueSpeed(speed, parameter,
                                                      coef_max, coef_min,
                                                      params,
                                                      label = 'New Controller',
                                                      typef='3D')
    
    fig2, axes2 = plt.subplots(3, 1, figsize=(10, 8))
    
    function.plotData(df= df_sorted[0],
                 x_parm = 'SPEED (rpm)',
                 y_parms= ['TORQUE','POWER (W)',"CURRENT (A)"],
                 upper_bound = bound_max_all_3D,
                 lower_bound = bound_min_all_3D,
                 x_new= x_new,
                 n_rows = 3,
                 title = 'Sorted Data by Speed',
                 plot_type='dot',
                 colorCode=0,
                 fig=fig2,
                 axes=axes2)
    
    axes21 = axes2.flatten()
    axes21[1].scatter([speed,speed],[p_max_mts,p_min_mts],s = 50, color= 'orange', edgecolor = "black")
    axes21[1].axvline(speed, linestyle = '--', label= f'@{speed}rpm')
    axes21[1].legend()
