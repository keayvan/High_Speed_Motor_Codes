# -*- coding: utf-8 -*-
"""
Created on Fri Dec 26 10:40:24 2025

@author: kkeramati
"""
from test_result_Analysis_TYTO import read_result
from test_result_Analysis_TYTO import plot_parameters_multi as plot
from test_result_Analysis_TYTO import steps_average as ave
from test_result_Analysis_TYTO import fitting_expo

from scipy.optimize import curve_fit, least_squares
from matplotlib import pyplot as plt
import numpy as np

def linearFit_df(x, y,
                 x_par, y_par,
                 x_fit= None,
                 b=None):

    def linear_fit(x, y, x_fit = None, b=b):
        
    
        x = np.asarray(x, dtype=float)
        y = np.asarray(y, dtype=float)
        if x_fit is None:
            x_fit = x

        
        def linear(x, a, b):
            return a * x + b
        

        if b is None:
            # fit a and b
            popt, cov = curve_fit(linear, x, y)
            a_fit, b_fit = popt
            y_fit = linear(x_fit, a_fit, b_fit)
            return a_fit, b_fit, cov, x_fit, y_fit
    
        else:
            # fit only a, keep b fixed
            def linear_fixed_b(x, a):
                return a * x + b
    
            popt, cov = curve_fit(linear_fixed_b, x, y)
            a_fit = popt[0]
            y_fit = linear_fixed_b(x_fit, a_fit)
            return a_fit, b, cov, x_fit, y_fit
    
    a, b, cov,xx, yy = linear_fit(x, y, 
                                  x_fit = x_fit,
                                  b=b)   
    return a, b, cov,xx, yy

powertrain0 = 'ARC_1Hz'
df0 = read_result(file_path =  "./Results_TYTO/ARC_steps50ms_5s_r1.csv",
                 powertrain=powertrain0,
                 remove_ESC_min = 1000)

df0[powertrain0+' '+'T/Q'] = df0[powertrain0+' '+'force Fz (thrust) (kgf)']*9.8/df0[powertrain0+' '+'torque MZ (torque) (N⋅m)']

pars = ['ESC throttle (μs)', 'force Fz (thrust) (kgf)', 'torque MZ (torque) (N⋅m)', 'voltage (V)',
              'current (A)', 'rotation speed (rpm)', 'electrical power (W)', 'mechanical power (W)',
              'motor & ESC efficiency (%)', 'propeller efficiency (gf/W)', 'powertrain efficiency (gf/W)','T/Q']
# plot(dfs = [df0],
#             parameters = pars,
#             x='Time (s)',
#             description="VS Time (s)",
#             n_rows=None,
#             markersize=1.5)

# plot(dfs = [df0],
#             parameters = pars,
#             x='ESC throttle (μs)',
#             description="VS throttle (μs)",
#             n_rows=None,
#             markersize=1.5)

# plot(dfs = [df0],
#             parameters = pars,
#             x='rotation speed (rpm)',
#             description="VS rotation speed (rpm)",
#             n_rows=None,
#             markersize=1.5)

# plot(dfs = [df0],
#             parameters = pars,
#             x='torque MZ (torque) (N⋅m)',
#             description="VS torque MZ (torque) (N⋅m)",
#             n_rows=None,
#             markersize=1.5)

# plot(dfs = [df0],
#             parameters = pars,
#             x='force Fz (thrust) (kgf)',
#             description="VS force Fz (thrust) (kgf)",
#             n_rows=None,
#             markersize=1.5)



df0_ave,win_stp=ave(
        df=df0,
        par_step="ESC throttle (μs)",
        mean_min= 25,
        mean_max= 35,
        start_df = 0,
        end_df = None,
        win=True)


x_par = 'ESC throttle (μs)'
y_par = 'rotation speed (rpm)'
x = df0 [powertrain0 +' ' +x_par] 
y = df0 [powertrain0 +' ' +y_par] 

x_ave = df0_ave [powertrain0 +' ' +x_par]
y_ave = df0_ave [powertrain0 +' ' +y_par] 

plt.figure()
plt.plot(x,y , '.', alpha = 0.4)
plt.plot(x_ave,y_ave , '.', color = 'red')

plt.xlabel (x_par)
plt.ylabel(y_par)


plot(dfs = [df0,df0_ave],
            parameters = pars,
            x="ESC throttle (μs)",
            description="VS ESC throttle (μs)",
            n_rows=None,
            markersize=1.5)

x_par = 'torque MZ (torque) (N⋅m)'
y_par = 'ESC throttle (μs)'


x = df0 [powertrain0 +' ' +x_par] 
y = df0 [powertrain0 +' '+y_par] 

x_ave = df0_ave [powertrain0 +' ' +x_par] 
y_ave = df0_ave [powertrain0 +' '+y_par] 
x_fit = np.linspace(x.min(),x.max(), 50)

a_input, b_input, cov_input,xx_input, yy_input= linearFit_df(x, y,
                                                             x_par,
                                                             y_par,
                                                             x_fit= x_fit,
                                                             b=1050)

plt.rcParams["font.family"] = "Century Gothic"
plt.figure()
plt.plot(x,y,'.', alpha = 0.3,label = 'experimental')
plt.plot(x_ave,y_ave,'.', alpha = 0.6, mfc = 'red', mec = 'red',label = 'Average')
plt.plot(xx_input, yy_input, color = '#ff596c', label = 'Fitting')
plt.xlabel(x_par)
plt.ylabel(y_par)
plt.legend()
plt.grid('both')
plt.text(
    0.05, 0.95, (f'y = {a_input:4f}*x + {b_input}'),
    transform=plt.gca().transAxes,
    fontsize=11,
    verticalalignment="top",
    bbox=dict(boxstyle="round", alpha=0.8)
    )
df0_sorted = df0.sort_values(by=powertrain0 +' ' +x_par)


plot(dfs = [df0_sorted],
            parameters = pars,
            x=x_par,
            description="VS Torque",
            n_rows=None,
            markersize=1.5)

powertrain1 = 'ARC_Off'

df1 = read_result(file_path =  "./Results_TYTO/ARC_steps_v1-1_off.csv",
                 powertrain=powertrain1,
                 remove_ESC_min = 1000)


df1_ave=ave(
        df=df1,
        par_step="ESC throttle (μs)",
        mean_min= 8,
        mean_max= 22,
        start_df = 0,
        end_df = None
    )

plot(dfs = [df1,df0],
            parameters = pars,
            x="ESC throttle (μs)",
            description="VS ESC throttle (μs)",
            n_rows=None,
            markersize=1.5)

df1_sorted = df1.sort_values(by=powertrain1 +' ' +x_par)



plot(dfs = [df1_sorted,df0_sorted],
            parameters = pars,
            x=x_par,
            description="VS ESC throttle (μs)",
            n_rows=None,
            markersize=1.5)


powertrain2 = 'MGM_1Hz'
df2 = read_result(file_path =  "./Results_TYTO/MGM_steps.csv",
                 powertrain=powertrain2,
                 remove_ESC_min = 1000)


df2_ave=ave(
        df=df2,
        par_step="ESC throttle (μs)",
        mean_min= 8,
        mean_max= 22,
        start_df = 0,
        end_df = None)
df2_sorted = df2.sort_values(by=powertrain2 +' ' +x_par)

powertrain3 = 'MGM_off'
df3 = read_result(file_path =  "./Results_TYTO/MGM_steps_off.csv",
                 powertrain=powertrain3,
                 remove_ESC_min = 1000)


df3_ave=ave(
        df=df3,
        par_step="ESC throttle (μs)",
        mean_min= 8,
        mean_max= 22,
        start_df = 0,
        end_df = None)
df3_sorted = df3.sort_values(by=powertrain3 +' ' +x_par)

plot(dfs = [df2,df3],
            parameters = pars,
            x='ESC throttle (μs)',
            description="VS ESC throttle (μs)",
            n_rows=None,
            markersize=1.5)

plot(dfs = [df0_sorted,df2_sorted],
            parameters = pars,
            x=x_par,
            description="VS Torque)",
            n_rows=None,
            markersize=1.5)

x_par = 'rotation speed (rpm)'
speed_fit_df0, y_pred_df0, params_df0,error_df0 = fitting_expo (df =df0_ave,
                                      x_param = x_par,
                                      y_param = 'current (A)',
                                      v_output = (0,0.25))

x_par_plot = powertrain0 + ' '+x_par
y_par_plot = powertrain0 + ' current (A)'

x_plot = df0[x_par_plot]
y_plot =  df0[y_par_plot]

x_ave = df0_ave[x_par_plot]
y_ave = df0_ave[y_par_plot]

x_fit = speed_fit_df0
y_fit = y_pred_df0



speed_fit_df2, y_pred_df2, params_df2,error_df2 = fitting_expo (df =df2_ave,
                                      x_param = x_par,
                                      y_param = 'current (A)',
                                      v_output = (0,15000))

x2_par_plot = powertrain2 + ' '+x_par
y2_par_plot = powertrain2 + ' current (A)'

x2_plot = df2[x2_par_plot]
y2_plot =  df2[y2_par_plot]

x2_ave = df2_ave[x2_par_plot]
y2_ave = df2_ave[y2_par_plot]

x2_fit = speed_fit_df2
y2_fit = y_pred_df2

plt.figure()
plt.plot(x_plot, y_plot,'.', alpha = 0.3,label = 'experimental' + ' '+powertrain0)
plt.plot(x_ave, y_ave,'o',ms=5, color = 'blue',label = 'steps_average'+'_'+powertrain0)
plt.plot(x_fit, y_fit, color = '#00d0b8', label = 'Exponential fitting'+'_'+powertrain0)
# plt.plot(x2_plot, y2_plot,'.', alpha = 0.3,label = 'experimental'+'_'+powertrain2)
# plt.plot(x2_ave, y2_ave,'o',ms=5, color = 'red',label = 'steps_average'+'_'+powertrain2)
# plt.plot(x2_fit, y2_fit, color = 'gray', label = 'Exponential fitting'+'_'+ powertrain2)
plt.title(' results')
plt.legend()
plt.grid(True)  

result_expo = [abs(y - x)/x*100 for x, y in zip(y_pred_df2, y_pred_df0)]

plt.figure()
plt.plot(y2_fit[40:],result_expo[40:],'o-',c='orange',ms=2,mfc='gray',mec='gray', label = '')
plt.grid()
plt.xlabel(x_par)
plt.ylabel('Current reduction %')
plt.legend()
    






