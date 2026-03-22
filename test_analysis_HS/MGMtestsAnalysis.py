# -*- coding: utf-8 -*-
"""
Created on Fri Jan  2 13:28:59 2026

@author: kkeramati
"""

from test_result_Analysis_TYTO import read_result
from test_result_Analysis_TYTO import plot_parameters_multi as plot
from test_result_Analysis_TYTO import steps_average as ave
from test_result_Analysis_TYTO import fitting_expo
from test_result_Analysis_TYTO import abs_thrust
from test_result_Analysis_TYTO import T_Q


powertrain0 = 'MGM'
df0 = read_result(file_path =  "./Results_TYTO/MGM_steps50ms_10s_r1.csv",
                 powertrain=powertrain0,
                 remove_ESC_min = 1000)

df0 = T_Q(df0, powertrain0)
df0=abs_thrust(df0)

pars = ['ESC throttle (μs)', 'force Fz (thrust) (kgf)', 'torque MZ (torque) (N⋅m)', 'voltage (V)',
              'current (A)', 'rotation speed (rpm)', 'electrical power (W)', 'mechanical power (W)',
              'motor & ESC efficiency (%)', 'propeller efficiency (gf/W)', 'powertrain efficiency (gf/W)','T/Q']


df0_ave,win_stp=ave(
        df=df0,
        par_step="ESC throttle (μs)",
        mean_min= 20,
        mean_max= 80,
        start_df = 0,
        end_df = None,
        win=True)
x_par = 'rotation speed (rpm)'

df0_sorted = df0.sort_values(by=powertrain0 +' ' +x_par)
df0_ave_sorted = df0_ave.sort_values(by=powertrain0 +' ' +x_par)

plot(dfs = [df0],
            parameters = pars,
            x='Time (s)',
            description="VS Time (s)",
            n_rows=None,
            markersize=1.5)


plot(dfs = [df0,df0_ave],
            parameters = pars,
            x="Time (s)",
            description="VS ESC throttle (μs)",
            n_rows=None,
            markersize=1.5)


plot(dfs = [df0_ave_sorted],
            parameters = pars,
            x=x_par,
            description="VS Torque",
            n_rows=None,
            markersize=1.5)

powertrain1 = 'ARC'
df1 = read_result(file_path =  "./Results_TYTO/ARC_steps50ms_5s_r1.csv",
                 powertrain=powertrain1,
                 remove_ESC_min = 1000)
df1=abs_thrust(df1)

df1[powertrain1+' '+'T/Q'] = df1[powertrain1+' '+'force Fz (thrust) (kgf)']*9.8/df1[powertrain1+' '+'torque MZ (torque) (N⋅m)']

df1_ave,win_stp1=ave(
        df=df1,
        par_step="ESC throttle (μs)",
        mean_min= 20,
        mean_max= 80,
        start_df = 0,
        end_df = None,
        win=True)

df1_sorted = df1.sort_values(by=powertrain1 +' ' +x_par)
df1_ave_sorted = df1_ave.sort_values(by=powertrain1 +' ' +x_par)

plot(dfs = [df1,df1_ave],
            parameters = pars,
            x="Time (s)",
            description="VS ESC throttle (μs)",
            n_rows=None,
            markersize=1.5)


plot(dfs = [df0_ave_sorted,df1_ave_sorted],
            parameters = pars,
            x="rotation speed (rpm)",
            description="VS ESC throttle (μs)",
            n_rows=None,
            markersize=1.5)

powertrain2 = 'MGM_r2'
df2 = read_result(file_path =  "./Results_TYTO/MGM_steps_ts1150_stps50s_r2.csv",
                 powertrain=powertrain2,
                 remove_ESC_min = 1000)
df2=abs_thrust(df2)

df2[powertrain2+' '+'T/Q'] = df2[powertrain2+' '+'force Fz (thrust) (kgf)']*9.8/df2[powertrain2+' '+'torque MZ (torque) (N⋅m)']

df2_ave,win_stp2=ave(
        df=df2,
        par_step="ESC throttle (μs)",
        mean_min= 20,
        mean_max= 80,
        start_df = 0,
        end_df = None,
        win=True)

df2_sorted = df2.sort_values(by=powertrain2 +' ' +x_par)
df2_ave_sorted = df2_ave.sort_values(by=powertrain2 +' ' +x_par)

plot(dfs = [df2,df2_ave],
            parameters = pars,
            x="Time (s)",
            description="VS Time (s)",
            n_rows=None,
            markersize=1.5)


plot(dfs = [df0_ave,df1_ave,df2_ave],
            parameters = pars,
            x="Time (s)",
            description="VS Time (s)",
            n_rows=None,
            markersize=1.5)


            
plot(dfs = [df0_sorted, df1_sorted, df2_sorted],
            parameters = pars,
            x=x_par,
            description="VS Time (s)",
            n_rows=None,
            markersize=1.5)

powertrain4 = 'ARC_1Hz'
df4 = read_result(file_path =  "./Results_TYTO/ARC_steps_ts1150_stps5s.csv",
                 powertrain=powertrain4,
                 remove_ESC_min = 1000)
df4=abs_thrust(df4)


df4[powertrain4+' '+'T/Q'] = df4[powertrain4+' '+'force Fz (thrust) (kgf)']*9.8/df4[powertrain4+' '+'torque MZ (torque) (N⋅m)']
df4_ave,win_stp4=ave(
        df=df4,
        par_step="ESC throttle (μs)",
        mean_min= 30,
        mean_max= 40,
        start_df = 0,
        end_df = None,
        win=True)

df4_sorted = df4.sort_values(by=powertrain4 +' ' +x_par)
df4_ave_sorted = df4_ave.sort_values(by=powertrain4 +' ' +x_par)

plot(dfs = [df4,df4_ave],
            parameters = pars,
            x="Time (s)",
            description="VS Time (s)",
            n_rows=None,
            markersize=1.5)

plot(dfs = [df1_ave_sorted, df4_ave_sorted],
            parameters = pars,
            x=x_par,
            description="VS Time (s)",
            n_rows=None,
            markersize=1.5)

