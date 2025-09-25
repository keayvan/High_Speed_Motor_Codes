#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 20 17:02:58 2025

@author: kkeramati
"""

# Detect file encoding
import chardet
import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
def phseToWinding(R_phase,connection,ty ='R'):
    if connection == 'Delta':
        R_winding = 3/2*R_phase
    elif connection =='Star':
        R_winding = R_phase/2
    print('***********************')     
    print (f'{ty}_winding_{connection}: {R_winding}')
    return R_winding

def windingToPhase(R_winding,connection):
    if connection == 'Delta':
        R_phase = 2/3*R_winding
    elif connection =='Star':
        R_phase = R_winding*2
    print('***********************')     
    print (f'R_phase_{connection}: {R_phase}')
    return R_phase


motor = 'motor01/'
tstNo = 'LdLq/'
fldr =  'L_measurment_LCR_28Feb2025/'
# fldr =  ''

file_path = './data/motorParameters/'
file_path = file_path+fldr+motor+tstNo
files = ['RY','YB', 'BR2'] 
# files = ['BR1','BR','BR2'] 


df_all = []
for i in range(len(files)):
    with open(f'{file_path+files[i]}.csv', "rb") as f:
        raw_data = f.read(10000)  # Read a portion of the file for detection
    
    encoding_info = chardet.detect(raw_data)
    encoding_info
    df = pd.read_csv(f'{file_path+files[i]}.csv', skiprows=11)
    df['thetaRad']=df['Θd[°]']*np.pi/180
    
    df['reactance'] = 2*np.pi * df['Frequency[Hz]']*df['Ls[H]'] 
    
    df['resistance_theta'] =  df['Z[Ohm]']*np.cos(df['thetaRad'])
    # df['resistance_sqrt'] =  np.sqrt(df['Z[Ohm]']**2 - df['reactance']**2)
    
    df['inductance_theta'] =  df['Z[Ohm]']*np.sin(df['thetaRad'])/np.pi/2/df['Frequency[Hz]']
    # df['inductance_sqrt'] =  (np.sqrt(df['Z[Ohm]']**2 -df['R[Ohm]']**2))/np.pi/2/df['Frequency[Hz]']

    # df['calc_reactance'] = np.sqrt(df['Z[Ohm]']**2-0.0086**2)
    # df['calc_inductance'] = df['calc_reactance']/2/np.pi/df['Frequency[Hz]']

    df = df.applymap(lambda x: pd.to_numeric(x, errors='coerce'))
    df_all.append(df)

colors_dict = {
    "dark_red": "#9e0012ff",
    "orange": "#f7941d",
    "gray": "#525252ff",
    "teal": "#009494ff",
    "turquoise": "#00d0b8",
    "navy_blue": "#0F3878",
    "sky_blue": "#0FAAF0",
    "red": "#f74242ff",
    "black": "black"}
colors = list(colors_dict.values())

columns = ['Ls[H]','R[Ohm]', 'Z[Ohm]'] 
max_var = [2e-5, 0.03,0.06]
fig, ax = plt.subplots(3, 3, figsize=(10, 10))
fig.tight_layout(pad=6.0)

result = []
for j in range(len(files)):
    print('*************************')
    for i, column in enumerate(columns):

        print(f'{column}_{files[j]}: {df_all[j][column][100:].mean()}')
        result.append(df_all[j][column][100:].mean())
        ax[j,i].plot(df_all[j]['Frequency[Hz]'], df_all[j][column], label=f'{column}_{files[j]}', marker = 'o', color = colors[i+2])
    
        ax[j, i].set_xlabel("Frequency[Hz]")
        ax[j, i].set_ylabel(f"{column}")
        ax[j, i].set_title(f"{column}")
        ax[j, i].set_ylim(0,max_var[i])
        ax[j, i].legend(loc="upper right")
        ax[j, i].grid(True)
    
    plt.show()

fig, ax = plt.subplots(1,3 , figsize = (10, 5))
ax = np.ravel([ax])
for k in range(len(files)):
    for i in range(len(columns)):
        ax[i].plot(df_all[k]['Frequency[Hz]'], df_all[k][columns[i]], color= colors[k], lw = 2, label = f'{files[k]}')
        ax[i].grid()
        ax[i].legend()
        ax[i].set_ylim(0,max_var[i])
        ax[i].set_title(columns[i])
plt.show()

    
L_mean = (result[0]+result[3]+result[6])/3 
R_mean = (result[1]+result[4]+result[7])/3 


print(f'L_mean: {L_mean}')
print(f'R_mean: {R_mean}')

print(f'error_YB:{((result[0]+result[3]+result[6])/3-result[0])/result[0]*100}')
print(f'error_RY:{((result[0]+result[3]+result[6])/3-result[3])/result[3]*100}')
print(f'error_BR:{((result[0]+result[3]+result[6])/3-result[6])/result[6]*100}')


     
connection = 'Delta'
R_phase = R_mean
R_winding = phseToWinding(R_phase,connection,ty='R')

L_phase = L_mean
R_winding = phseToWinding(L_phase,connection,ty='L')



