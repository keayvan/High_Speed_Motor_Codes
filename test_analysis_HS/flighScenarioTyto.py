# -*- coding: utf-8 -*-
"""
Created on Wed Nov 19 13:36:10 2025

@author: kkeramati
"""

from test_result_Analysis_TYTO import plot_parameters_multi as plot
from test_result_Analysis_TYTO import read_result
from test_result_Analysis_TYTO import steps_average as stp
from test_result_Analysis_TYTO import fitting_expo as fit
from matplotlib import pyplot as plt
from test_result_Analysis_TYTO import analysis_fit_compare as ana
from test_result_Analysis_TYTO import integral

plt.rcParams["font.family"] = "Century Gothic"

powertrain0 = 'MGM_flightTest'
file_path = "./Results_TYTO/MGM_flightTest70%_400s.csv"  # change path if needed
df0 = read_result(file_path, powertrain=powertrain0,remove_ESC_min = None)
pars = ['electrical power (W)',
              'voltage (V)',
              'current (A)',
              'ESC throttle (μs)',
              'rotation speed (rpm)',
              'force Fz (thrust) (N)',
              'torque MZ (torque) (N⋅m)',
              'powertrain efficiency (N/W)']
plot(dfs = [df0],
     parameters = pars,
     x='Time (s)',
     description="",
     n_rows=None,
     markersize=4)

df0_ave = stp(
    df=df0,
    par_step= "ESC throttle (μs)",
    mean_min= 10,
    mean_max= 20,
    start_df = 0,
    end_df = None)

speed_fit_df0, y_pred_df0, (a,b,c),errors = fit (df = df0_ave,
                                               x_param = 'rotation speed (rpm)',
                                               y_param = 'current (A)',
                                               v_output = (0,15000))


powertrain1 = 'MGM'
file_path = "./Results_TYTO/MGM_flightTest.csv"  # change path if needed
df1 = read_result(file_path, powertrain=powertrain1, remove_ESC_min = None)

pars = ['electrical power (W)',
              'voltage (V)',
              'current (A)',
              'ESC throttle (μs)',
              'rotation speed (rpm)',
              'torque MZ (torque) (N⋅m)'
              ]
plot(dfs = [df0],
     parameters = pars,
     x='Time (s)',
     description="",
     n_rows=None,
     markersize=2)

df1_ave = stp(
    df=df1,
    par_step= "ESC throttle (μs)",
    mean_min= 10,
    mean_max= 20,
    start_df = 0,
    end_df = None)

speed_fit_df1, y_pred_df1, (a,b,c),errors = fit (df = df1_ave,
                                               x_param = 'rotation speed (rpm)',
                                               y_param = 'current (A)',
                                               v_output = (0,15000))

pars1 = [     'voltage (V)',
              'current (A)',
              'rotation speed (rpm)',
              'torque MZ (torque) (N⋅m)',
              'force Fz (thrust) (kgf)',
              'electrical power (W)'
              ]
plot(dfs = [df0],
     parameters = pars1,
     x='Time (s)',
     description="",
     n_rows=None,
     markersize=2)


plt.figure()
plt.plot(df0[powertrain0 + ' rotation speed (rpm)'], df0[powertrain0+' current (A)'],'.', alpha = 0.3,label = powertrain0 + 'experimental')
plt.plot(df0_ave[powertrain0 + ' rotation speed (rpm)'], df0_ave[powertrain0+' current (A)'],'o',ms=2, color = 'red',label = powertrain0 + 'steps_average')
plt.plot(speed_fit_df0, y_pred_df0, color = '#00d0b8', label = powertrain0 + 'Exponential fitting')

plt.plot(df1[powertrain1 + ' rotation speed (rpm)'], df1[powertrain1+' current (A)'],'.', alpha = 0.3,label = powertrain1 + 'experimental')
plt.plot(df1_ave[powertrain1 + ' rotation speed (rpm)'], df1_ave[powertrain1+' current (A)'],'o',ms=2, color = '#29e2ecff',label = powertrain1 + 'steps_average')
plt.plot(speed_fit_df1, y_pred_df1, color = '#0f75bcff', label = powertrain1 + 'Exponential fitting')
plt.xlabel('Rotational speed (rpm)')
plt.ylabel('Current (A)')
plt.legend()
plt.grid(True)  

powetrains = ['MGM','DPWM_MIN']
fitting_all = [y_pred_df1,y_pred_df0]
skip = 50
ref_I = ['MGM']
curve_I = ['DPWM_MIN']

plt.figure()

for i in range(len(curve_I)):
    f1 = powetrains.index(ref_I[i])
    f2 = powetrains.index(curve_I[i])
    result_exponential = [((x) - (y))/(x)*100 for x, y in zip(fitting_all[f1], fitting_all[f2])][skip:]
    xx = speed_fit_df1[skip:]
    
    plt.plot(xx,result_exponential,'o-',color = 'gray',mfc = 'red',ms =2, label = curve_I[i]+'_'+ref_I[i])
    plt.grid(True)
    plt.xlabel('Rotational speed (rpm)')
    plt.ylabel('Current reduction %')
    plt.title(f'result {powertrain0} to {powertrain1}')
    plt.legend()


df4, ave4, [speed_fit4,y_pred4], [x_plot4,y_plot4] =  ana(file_name = 'MGM_steps' ,
                                                    powertrain = 'MGM',
                                                    x_par = 'rotation speed (rpm)',
                                                    y_par = 'current (A)')


plot(dfs = [ave4.iloc[1:-1,:]],
     parameters = pars1,
     x='Time (s)',
     description="",
     n_rows=None,
     markersize=2)


df5, ave5, [speed_fit5,y_pred5], [x_plot5,y_plot5] =  ana(file_name = 'MGM_flightScenario70%' ,
                                                    powertrain = 'MGM',
                                                    x_par = 'rotation speed (rpm)',
                                                    y_par = 'current (A)')

plot(dfs = [df5],
     parameters = pars1,
     x='Time (s)',
     description="",
     n_rows=None,
     markersize=2)

df5['MGM force Fz (thrust) (kgf)'] = df5['MGM force Fz (thrust) (kgf)']*-1

df6, ave6, [speed_fit6,y_pred6], [x_plot6,y_plot6] =  ana(file_name = 'ARC_steps_v1' ,
                                                    powertrain = 'ARC_v1',
                                                    x_par = 'ESC throttle (μs)',
                                                    y_par = 'current (A)')

df6_1, ave6_1, [speed_fit6_1,y_pred6_1], [x_plot6_1,y_plot6_1] =  ana(file_name = 'ARC_steps_v1-1' ,
                                                    powertrain = 'ARC_v1-1',
                                                    x_par = 'ESC throttle (μs)',
                                                    y_par = 'current (A)')

plot(dfs = [ave4.iloc[1:-1,:],ave6.iloc[1:-1,:]],
     parameters = ['torque MZ (torque) (N⋅m)'],
     x='ESC throttle (μs)',
     description="",
     n_rows=None,
     markersize=2)

plot(dfs = [ave6.iloc[1:-1,:],ave6_1.iloc[1:-1,:]],
     parameters = ['rotation speed (rpm)'],
     x='Time (s)',
     description="",
     n_rows=None,
     markersize=2)

plot(dfs = [df6.iloc[1:-1,:],df6_1.iloc[1:-1,:]],
     parameters = ['rotation speed (rpm)','ESC throttle (μs)'],
     x='Time (s)',
     description="",
     n_rows=None,
     markersize=2)

plt.figure()
plt.plot(df6.iloc[:,1], df6.iloc[:,6],'o-',ms=1)
plt.plot(ave6.iloc[:,1], ave6.iloc[:,6],'o-',ms=1)

df7, ave7, [speed_fit7,y_pred7], [x_plot7,y_plot7] =  ana(file_name = 'ARC_flightScenarioFromMGM70%' ,
                                                    powertrain = 'ARC',
                                                    x_par = 'rotation speed (rpm)',
                                                    y_par = 'current (A)')
df7 = df7.iloc[20:,:]
df7['Time (s)'] = df7['Time (s)'] - df7['Time (s)'].min()
df7['ARC force Fz (thrust) (kgf)'] = df7['ARC force Fz (thrust) (kgf)']*-1
pars1 = [     'voltage (V)',
              'current (A)',
              'rotation speed (rpm)',
              'torque MZ (torque) (N⋅m)',
              'force Fz (thrust) (kgf)',
              'electrical power (W)'
              ]
plot(dfs = [df5,df7],
     parameters = pars,
     x='Time (s)',
     description="",
     n_rows=None,
     markersize=1)




integral5 = integral (df5, par='Time (s)')
integral7 = integral (df7, par='Time (s)')
print (f'MGM = {integral5.iloc[7]} W.s')
print (f'ARC = {integral7.iloc[7]} W.s')


xx= (integral5.iloc[7]-integral7.iloc[7])/integral5.iloc[7]*100
print(f'differenc: {xx}%')

