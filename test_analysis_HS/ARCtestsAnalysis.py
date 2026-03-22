# -*- coding: utf-8 -*-
"""
Created on Mon Jan  5 12:47:50 2026

@author: kkeramati
"""


from test_result_Analysis_TYTO import read_result
from test_result_Analysis_TYTO import plot_parameters_multi as plot
from test_result_Analysis_TYTO import steps_average as ave
from test_result_Analysis_TYTO import fitting_expo
from test_result_Analysis_TYTO import abs_thrust
from test_result_Analysis_TYTO import T_Q
import pandas as pd
powertrains = ['ARC','MGM']
test_files = ['ARC_steps50_5s_r2','MGM_steps50ms_10s_r1']
remove_ESC_min = [1000,1000]
mean_mins = [10,20]
mean_maxs = [30,80]
dfs = []
dfs_ave = []
win_stps = []
dfs_sorted_torque = []
dfs_sorted_speed = []
for i, v in enumerate(powertrains):
    df0 = read_result(file_path =  f"./Results_TYTO/{test_files[i]}.csv",
                     powertrain=v,
                     remove_ESC_min = remove_ESC_min[i])
    df0 = T_Q(df0, v)
    df0=abs_thrust(df0)
    df0_ave,win_stp=ave(
            df=df0,
            par_step="ESC throttle (μs)",
            mean_min= mean_mins[i],
            mean_max= mean_maxs[i],
            start_df = 0,
            end_df = None,
            win=True)
    df0_sorted_torque = df0.sort_values(by=v +' ' +'torque MZ (torque) (N⋅m)')
    df0_sorted_speed = df0.sort_values(by=v +' ' +'rotation speed (rpm)')


    
    dfs.append(df0)
    dfs_ave.append(df0_ave)
    win_stps.append(win_stp)
    dfs_sorted_torque.append(df0_sorted_torque)
    dfs_sorted_speed.append(df0_sorted_speed)
    
pars = ['ESC throttle (μs)', 'force Fz (thrust) (kgf)', 'torque MZ (torque) (N⋅m)', 'voltage (V)',
              'current (A)', 'rotation speed (rpm)', 'electrical power (W)', 'mechanical power (W)',
              'motor & ESC efficiency (%)', 'propeller efficiency (gf/W)', 'powertrain efficiency (gf/W)','T/Q']
plot(dfs = [dfs_ave[0]],
            parameters = pars,
            x="ESC throttle (μs)",
            description="",
            n_rows=None,
            markersize=1.5)

plot(dfs = [dfs_ave[1]],
            parameters = pars,
            x="ESC throttle (μs)",
            description="",
            n_rows=None,
            markersize=1.5)

x_par = 'rotation speed (rpm)'
y_par = 'ESC throttle (μs)'
x_ARC = dfs_ave[0][powertrains[0]+' '+ x_par]
y_ARC = dfs_ave[0][powertrains[0]+' '+ y_par]
new_value = 0
new_index = 0

x_ARC= pd.concat([
    pd.Series([0], index=[0]),
    x_ARC])

y_ARC= pd.concat([
    pd.Series([1000], index=[0]),
    y_ARC])

from matplotlib import pyplot as plt
from scipy.interpolate import interp1d
import numpy as np

plt.rcParams["font.family"] = "Century Gothic"

f = interp1d(x_ARC, y_ARC, kind='quadratic',fill_value = 'extrapolate')  # 'linear', 'quadratic', 'cubic'
x_ARC_new = np.linspace(0, 14500, 1000)
y_ARC_new = f(x_ARC_new)
speed_points = [2000, 4000, 6000, 8000, 10000, 12000, 14000, 15000]
throttle =[]
for i, v in enumerate(speed_points):
    th = f(v)
    throttle.append(float(np.round(th,2)))
    
# pd.DataFrame(throttle, columns=["values"]).to_csv("C:/Users/kkeramati/OneDrive - ARQUIMEA GROUP/Documentos/data.csv", index=False)

print (f"throttle at 10000rpm {f(10000)}")
plt.figure()
plt.plot(x_ARC , y_ARC, '-o',mfc = 'red',label = 'ARC')
plt.plot(x_ARC_new , y_ARC_new,color = 'orange', label = 'ARC_fit')
plt.xlabel (x_par)
plt.ylabel(y_par)
plt.grid('both')
plt.legend()

x_MGM = dfs_ave[1][powertrains[1]+' '+ x_par]
y_MGM = dfs_ave[1][powertrains[1]+' '+ y_par]

y_ARC_new_MGM = f(x_MGM)


plt.figure()
plt.plot(x_ARC , y_ARC, '-o',mfc = 'red',label = 'ARC')
plt.plot(x_ARC_new , y_ARC_new,color = 'gray', label = 'ARC_fit')
plt.plot(x_MGM , y_ARC_new_MGM,'-o',color = 'orange', label = 'MGM_fitting')


plt.xlabel (x_par)
plt.ylabel(y_par)
plt.grid('both')
plt.legend()

powertrains_flights = ['MGM_flight']
test_files_flights = ['MGM_flightScenario70%']
remove_ESC_min_flights = [None]
dfs_fligh = []
dfs_sorted_torque_flights = []
dfs_sorted_speed_flights = []
for i, v in enumerate(powertrains_flights):
    df_flight = read_result(file_path =  f"./Results_TYTO/{test_files_flights[i]}.csv",
                     powertrain=v,
                     remove_ESC_min = remove_ESC_min_flights[i])
    
    df_flight = T_Q(df_flight, v)
    df_flight=abs_thrust(df_flight)

    df_sorted_torque_flight = df_flight.sort_values(by=v +' ' +'torque MZ (torque) (N⋅m)')
    df_sorted_speed_flight = df_flight.sort_values(by=v +' ' +'rotation speed (rpm)')


    
    dfs_fligh.append(df_flight)
    dfs_sorted_torque_flights.append(df_sorted_torque_flight)
    dfs_sorted_speed_flights.append(df_sorted_speed_flight)
    
plot(dfs = [dfs_fligh[0]],
            parameters = pars,
            x="Time (s)",
            description="",
            n_rows=None,
            markersize=1.5)

speed_MGM_flight = dfs_fligh[0][powertrains_flights[0]+' '+ x_par]
ESC_MGM_flight = dfs_fligh[0][powertrains_flights[0]+' '+ y_par]

ESC_generated = f(speed_MGM_flight)

plt.figure()
plt.plot(dfs_fligh[0]['Time (s)'],ESC_generated)