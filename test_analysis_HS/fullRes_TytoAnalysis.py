# -*- coding: utf-8 -*-
"""
Created on Tue Jan 13 13:41:37 2026

@author: kkeramati
"""

import pandas as pd
from matplotlib import pyplot as plt

# Load the file
plt.rcParams["font.family"] = "Century Gothic"

def param_resolution (df):
    time_col = "Time (s)"
    
    # Dictionary to store the separate DataFrames
    dataframes = {}
    
    for col in df.columns:
        if col == time_col:
            continue
    
        # Select rows where this column has a value
        temp_df = df[[time_col, col]].dropna()
    
        # Only keep if there is actual data
        if not temp_df.empty:
            dataframes[col] = temp_df.reset_index(drop=True)
    return dataframes


df = pd.read_csv("./Results_TYTO/ARC_steps50ms_5s_r1_fullRes.csv")
df_res = param_resolution(df)
powertrain = 'Powertrain 1'
par0 = 'rotation speed (rpm)'
speed_ARC = df_res[f'{powertrain} - {par0}']

plt.figure()
plt.plot(speed_ARC.iloc[:,0],speed_ARC.iloc[:,1],color = '#0F3878')
plt.grid()
plt.xlabel('Time (s)')
plt.ylabel(par0)
plt.title('ARC')
par0 = 'current (A)'
current_ARC = df_res[f'{powertrain} - {par0}']
par0 = 'voltage (V)'
volt_MGM = df_res[f'{powertrain} - {par0}']
plt.figure()
plt.plot(current_ARC.iloc[:,0],current_ARC.iloc[:,1],color = '#0F3878')
plt.grid()
plt.xlabel('Time (s)')
plt.ylabel(par0)
plt.title('ARC')

par0 = 'electrical power (W)'

power_ARC = df_res[f'{powertrain} - {par0}']

par0 = 'voltage (V)'

Volt_ARC = df_res[f'{powertrain} - {par0}']
plt.figure()
plt.plot(power_ARC.iloc[:,0],power_ARC.iloc[:,1],color = '#0F3878')
plt.grid()
plt.xlabel('Time (s)')
plt.ylabel(par0)
plt.title('ARC')


#######################################################
df = pd.read_csv("./Results_TYTO/ARC_steps50ms_5s_r1.csv")
df_res = param_resolution(df)
powertrain = 'Powertrain 1'
par0 = 'rotation speed (rpm)'
speed_MGM = df_res[f'{powertrain} - {par0}']

plt.figure()
plt.plot(speed_MGM.iloc[:,0],speed_MGM.iloc[:,1],color = '#0F3878')
plt.grid()
plt.xlabel('Time (s)')
plt.ylabel(par0)
plt.title('MGM')

plt.figure()
plt.plot(speed_ARC.iloc[:,0],speed_ARC.iloc[:,1],color = '#0F3878', label = 'Full resolution')
plt.plot(speed_MGM.iloc[:,0],speed_MGM.iloc[:,1],color = 'red', label = 'filtering')

plt.legend()
plt.grid()
plt.xlabel('Time (s)')
plt.ylabel(par0)
plt.title('')

par0 = 'current (A)'
current_MGM = df_res[f'{powertrain} - {par0}']
par0 = 'electrical power (W)'

power_MGM = df_res[f'{powertrain} - {par0}']

par0 = 'voltage (V)'

Volt_MGM = df_res[f'{powertrain} - {par0}']
plt.figure()
plt.plot(current_ARC.iloc[:,0],current_ARC.iloc[:,1],color = '#0F3878', label = 'Full resolution')
plt.plot(current_MGM.iloc[:,0],current_MGM.iloc[:,1],color = 'red', label = 'filtering')

plt.grid()
plt.xlabel('Time (s)')
plt.ylabel(par0)
plt.title('')
plt.legend()



plt.figure()
plt.plot(power_ARC.iloc[:,0],power_ARC.iloc[:,1],color = '#0F3878', label = 'Full resolution')
plt.plot(power_MGM.iloc[:,0],power_MGM.iloc[:,1],color = 'red', label = 'filtering')

plt.legend()
plt.grid()
plt.xlabel('Time (s)')
plt.ylabel(par0)
plt.title('')

plt.figure()
plt.plot(Volt_ARC.iloc[:,0],Volt_ARC.iloc[:,1],color = '#0F3878', label = 'Full resolution')
plt.plot(Volt_MGM.iloc[:,0],Volt_MGM.iloc[:,1],color = 'red', label = 'filtering')

plt.legend()
plt.grid()
plt.xlabel('Time (s)')
plt.ylabel(par0)
plt.title('')

d_current = current_ARC.iloc[:,1] - current_MGM.iloc[:,1]

plt.figure()
plt.plot(current_ARC.iloc[:,0], d_current)
