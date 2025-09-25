#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 19 15:49:16 2025

@author: kkeramati
"""

import ArcDefenceData as ARC
import moteusData as Moteus
import function
from matplotlib import pyplot as plt
import numpy as np

def Power_MoteusVsARC(df_Arc_sorted, df_moteus_sorted, expan_factor = 0.01, curveTofit = "3D"):
    x_param = 'SPEED (rpm)'
    y_params = ["POWER (W)"]
    x_new = None
    
    b_max_Arc, b_min_Arc,coef_max_Arc, coef_min_Arc, params_Arc = function.boundary_curve(df_Arc_sorted,
                                                                             x_param,
                                                                             y_params,
                                                                             x_new,
                                                                             expan_factor,
                                                                             curveTofit)
    
    fig, axes = plt.subplots(1, 1, figsize=(10, 8))
    function.plotData(df=df_Arc_sorted,
                x_parm=x_param,
                y_parms= y_params,
                transparency= 0.2,
                upper_bound=b_max_Arc,
                lower_bound=b_min_Arc,
                bound_color=6,
                x_new = None,
                n_rows = 1,
                title = 'Data',
                plot_type = 'dot',
                fig = fig,
                axes = axes,
                label = 'ARC',
                colorCode = 2,
                annotation_max=False)
    
    b_max_Moteus, b_min__Moteus, coef_max_Moteus, coef_min_Moteus,params_Moteus = function.boundary_curve(df_moteus_sorted[0],
                                                                             x_param,
                                                                             y_params,
                                                                             x_new,
                                                                             expan_factor,
                                                                             curveTofit)
    
    function.plotData(df=df_moteus_sorted[0],
                x_parm=x_param,
                y_parms= y_params,
                transparency=0.2,
                upper_bound=b_max_Moteus,
                lower_bound=b_min__Moteus,
                bound_color=7,
                x_new = None,
                n_rows = 1,
                title = 'Power New Controller vs Arc',
                plot_type = 'dot',
                fig = fig,
                axes = axes,
                label = 'New_Conroller',
                colorCode = 0,
                annotation_max=False)
def MoteusVsARC_predictions(df_Arc_sorted, df_moteus_sorted, speed= 15000 ,expan_factor = 0.01, curveTofit = "3D"):
    x_param = 'SPEED (rpm)'
    y_params = ["POWER (W)"]
    x_new = None
    
    b_max_Arc, b_min_Arc,coef_max_Arc, coef_min_Arc, params_Arc = function.boundary_curve(df_Arc_sorted,
                                                                             x_param,
                                                                             y_params,
                                                                             x_new,
                                                                             expan_factor,
                                                                             curveTofit)
    speed, p_max_Arc, p_min_Arc = function.valueSpeed(speed,  y_params[0],
                                                      coef_max_Arc, coef_min_Arc,
                                                      params_Arc,
                                                      label = 'ARC Controller',
                                                      typef = curveTofit)
    p_mean_Arc = 0.5*(p_max_Arc+p_min_Arc)
    
    fig1, axes1 = plt.subplots(1, 1, figsize=(10, 8))
    function.plotData(df=df_Arc_sorted,
                x_parm=x_param,
                y_parms= y_params,
                transparency= 0.2,
                upper_bound=b_max_Arc,
                lower_bound=b_min_Arc,
                bound_color=6,
                x_new = None,
                n_rows = 1,
                title = 'data',
                plot_type = 'dot',
                fig = fig1,
                axes = axes1,
                label = 'ARC',
                colorCode = 2,
                annotation_max=False)
    import numpy as np
    x_new = None
    x_new = np.linspace(0, 15000,15001)
    
    b_max_Moteus, b_min__Moteus, coef_max_Moteus, coef_min_Moteus,params_Moteus = function.boundary_curve(df_moteus[0],
                                                                             x_param,
                                                                             y_params,
                                                                             x_new,
                                                                             expan_factor,
                                                                             curveTofit)
    speed, p_max_Moteus, p_min_Moteus = function.valueSpeed(speed,  y_params[0],
                                                      coef_max_Moteus, coef_min_Moteus,
                                                      params_Moteus,
                                                      label = 'Moteus',
                                                      typef = curveTofit)
    p_mean_Moteus = 0.5*(p_max_Moteus+p_min_Moteus)
    function.plotData(df=df_moteus[0],
                x_parm=x_param,
                y_parms= y_params,
                transparency=0.2,
                upper_bound=b_max_Moteus,
                lower_bound=b_min__Moteus,
                bound_color=7,
                x_new = x_new,
                n_rows = 1,
                title = 'Power Prediction',
                plot_type = 'dot',
                fig = fig1,
                axes = axes1,
                label = 'New_Conroller',
                colorCode = 0,
                annotation_max=False)
    
    
    axes1.scatter([speed]*2,[p_max_Arc,p_min_Arc],s = 60, color= 'orange', edgecolor = "black")
    axes1.scatter([speed]*2,[p_max_Moteus,p_min_Moteus],s = 60, color= 'red', edgecolor = "black")
    axes1.axvline(speed, linestyle = '--', label= f'@{speed}rpm')
    x = [speed]*2
    y= [p_max_Arc,p_min_Arc]
    y1= [p_max_Moteus,p_min_Moteus]
    
    y = [round(num, 0) for num in y] 
    y1 = [round(num, 0) for num in y1] 
    
    for i in range(len(x)):
        axes1.annotate(f"Arc:{y[i]}W",
                           (x[i], y[i]),
                           textcoords="offset points",
                           xytext=(-100,20),
                           fontsize=9,
                           color="#0F3878",
                           arrowprops=dict(arrowstyle="->", color="#0F3878", lw=1.5))
        axes1.annotate(f"New:{y1[i]}W",
                           (x[i], y1[i]),
                           textcoords="offset points",
                           xytext=(10,-40),
                           fontsize=9,
                           color="#9e0012ff",
                           arrowprops=dict(arrowstyle="->", color="#9e0012ff", lw=1.5))
    
    axes1.legend()
    print('****************************')
    print('improvments:')
    print (f'min to min improvment:{round((p_min_Arc-p_min_Moteus)/p_min_Arc*100,1)}%')
    print (f'max to max improvment:{round((p_max_Arc-p_max_Moteus)/p_max_Arc*100,1)}%')
    print (f'mean to mean improvment:{round((p_mean_Arc-p_mean_Moteus)/p_mean_Arc*100,1)}%')
    return [p_min_Arc,p_max_Arc,  p_mean_Arc], [p_min_Moteus,p_max_Moteus,  p_mean_Moteus]

if __name__ =='__main__':
    filename = "prueba 4.csv"
    # filename = "Telem ESC 01_2025.csv"
    filenames = ['KPKIV38'] 
    curvefit = '3D'
    df_Arc,df_Arc_sorted  = ARC.readArc_csv(filename,  test = 'testbench')
    df_moteus, df_moteus_sorted = Moteus.process_csv_files(filenames)
    
    Power_MoteusVsARC(df_Arc_sorted, df_moteus_sorted, expan_factor = 0.01, curveTofit = curvefit)
    ARC, Moteus = MoteusVsARC_predictions(df_Arc_sorted, df_moteus_sorted, speed= 14000 ,expan_factor = 0.01, curveTofit = "4D")

    _,_, coef_max_Moteus, coef_min_Moteus,params_Moteus = function.boundary_curve(df_moteus_sorted[0],
                                                                             x_param= 'SPEED (rpm)',
                                                                             y_params = ['POWER (W)'],
                                                                             x_new = None,
                                                                             expan_factor = 0.01,
                                                                             curveTofit =curvefit)
    
    speedList, p_max_Moteus, p_min_Moteus,p_mean_Moteus= function.valueSpeedlist(speed = list(np.linspace(0, 16000,16001)),
                                                   parameter='POWER (W)',
                                                   coef_max=coef_max_Moteus,
                                                   coef_min=coef_min_Moteus,
                                                   params=["POWER (W)"],
                                                   typef=curvefit)
    
    _,_, coef_max_Arc, coef_min_Arc,params_Moteus = function.boundary_curve(df_Arc_sorted,
                                                                             x_param= 'SPEED (rpm)',
                                                                             y_params = ['POWER (W)'],
                                                                             x_new = None,
                                                                             expan_factor = 0.01,
                                                                             curveTofit = curvefit)
    speedList, p_max_Arc, p_min_Arc,p_mean_Arc= function.valueSpeedlist(speed = list(np.linspace(0, 16000,16001)),
                                                   parameter='POWER (W)',
                                                   coef_max=coef_max_Arc,
                                                   coef_min=coef_min_Arc,
                                                   params=["POWER (W)"],
                                                   typef=curvefit)
    
    
    diffMeanP, mean_percent=[], []
    speedList = speedList[1:]
    p_mean_Arc = p_mean_Arc[1:]
    p_mean_Moteus = p_mean_Moteus[1:]
    for i, v in enumerate(speedList):

        mean_p = (p_mean_Arc[i]-p_mean_Moteus[i]) /p_mean_Arc[i]*100
        diffMeanP0 = (p_mean_Arc[i]-p_mean_Moteus[i])
        mean_percent.append(mean_p)
        diffMeanP.append(diffMeanP0)
        
    fig, axes = plt.subplots(1,3,figsize=(15,5))
    axes = np.ravel([axes])
    fig.tight_layout(pad=6.0)

    axes[0].plot(speedList,p_mean_Moteus, label = 'New Controller', color = "#9e0012ff",lw = 3)
    axes[0].plot(speedList,p_mean_Arc, label= 'ARC Board',color = "#0F3878", lw = 3)
    axes[0].set_xlabel('Speed(rpm)')
    axes[0].set_ylabel('Mean Power Consumption (W)')
    axes[0].legend()
    axes[0].grid()

    
    axes[1].plot (speedList,diffMeanP, color = "#525252ff", lw = 3)
    axes[1].set_xlabel('Speed(rpm)')
    axes[1].set_ylabel('Power difference (W)')
    axes[1].grid()

        
    axes[2].plot (speedList,mean_percent, color = "#00d0b8", lw = 3)
    axes[2].set_xlabel('Speed(rpm)')
    axes[2].set_ylabel('Power Consumption Improvment %')
    axes[2].grid()
    