#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 18 17:24:24 2025

@author: kkeramati
"""
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def func4d (x, coef):
    a, b, c = coef[0], coef[1], coef[2]
    return a*x*x*x*x+b*x*x*x + c*x*x 

def func3d(x,coef):
    a, b, c = coef[0], coef[1], coef[2]

    return a*x*x*x+b*x*x + c*x 

def func2d(x,coef):
    b, c, d = coef[0], coef[1], coef[2]

    return b*x*x + c*x + d
def funcToFit(typef, x, coef):
    if typef == '4D':
        return func4d(x, coef)
    elif typef == '3D':
        return func3d(x, coef)
    elif typef == 'exp':
        return func2d(x, coef)
    else:
        raise ValueError("Unsupported degree. Choose 2, 3, or 4.")
        
def fit_curve(x, y, degree=3, extrapolate_x=None):
    if len(x) > degree:
        coeffs = np.polyfit(x, y, degree)
        poly_func = np.poly1d(coeffs)
        if extrapolate_x is not None:
            return poly_func(extrapolate_x), coeffs
        return poly_func(x), coeffs
    
def boundary_curve(df_Arc_sorted, x_param,y_params,x_new, expan_factor,curveTofit,coefOut=False):
    from scipy.signal import argrelextrema
    from scipy.optimize import curve_fit
    if curveTofit == "3D":
        def fit_func(x,a, b, c):
            return a*x*x*x+b*x*x + c*x
    elif curveTofit == "exp":
        def fit_func(x, a, b):
            return a*np.exp(b*x)
        
    elif curveTofit == "4D":
        def fit_func(x,a, b, c):
            return a*x*x*x*x+b*x*x*x +c*x*x
   
    
    bound_max_all_3D = []
    bound_min_all_3D = []
    coef_max_all = []
    coef_min_all = []
    xAxis = df_Arc_sorted[x_param].to_numpy()
    if x_new is None:
        x_new = xAxis
    for i in range(len(y_params)):
        sig = df_Arc_sorted[y_params[i]].to_numpy()

        bound_range = np.max(sig) - np.min(sig)
        expansion_factor = expan_factor * bound_range
        
        local_max_indx = argrelextrema(sig, np.greater, order=3)[0]
        local_min_indx = argrelextrema(sig, np.less, order=3)[0]
        
        local_max = sig[local_max_indx]
        local_max = local_max + expansion_factor

        max_time = xAxis[local_max_indx]
        params_max_3D, covariance_max_3D = curve_fit(fit_func, max_time, local_max, bounds=(0, np.inf))
        upper_bound_PWR_3D = fit_func(x_new, *params_max_3D)
        # upper_bound_PWR_3D, params_max_3D = fit_curve(x=max_time,
        #                                               y=local_max,
        #                                               degree=3,
        #                                               extrapolate_x=x_new)
        bound_max_all_3D.append(upper_bound_PWR_3D)
        coef_max_all.append(params_max_3D)
        local_min = sig[local_min_indx]
        local_min = local_min - expansion_factor

        min_time = xAxis[local_min_indx]
        params_min_3D, covariance_min_3D = curve_fit(fit_func, min_time, local_min,  bounds=(0, np.inf))
        lower_bound_PWR_3D = fit_func(x_new, *params_min_3D)
        # lower_bound_PWR_3D, params_min_3D = fit_curve(x=min_time,
        #                                               y=local_min,
        #                                               degree=3,
        #                                               extrapolate_x=x_new)
        bound_min_all_3D.append(lower_bound_PWR_3D)
        coef_min_all.append(params_min_3D)
    return bound_max_all_3D, bound_min_all_3D, coef_max_all, coef_min_all, y_params

def annotate_max(ax, df, param, label, color, offset_index, x_param='time'):
    max_idx = df[param].idxmax()
    max_x = df[x_param][max_idx]
    max_value = df[param][max_idx]
    
    y_offset = 0.08 * (max_value if max_value != 0 else 1) * (offset_index % 2 * 2 - 1)  # Alternating offset
    ax.annotate(f"{max_value:.2f} @ {max_x:.2f}", 
                xy=(max_x, max_value), 
                xytext=(max_x, max_value + y_offset),
                textcoords="data",
                fontsize=10,
                color=color,
                bbox=dict(facecolor='white', alpha=0.6, edgecolor=color, boxstyle="round,pad=0.3"),
                arrowprops=dict(arrowstyle="->", color=color))
def valueSpeed(speed, parameter, coef_max, coef_min,params,label, typef):
    par_indx = params.index(parameter)
    p_max_mts = funcToFit(typef,speed,coef_max[par_indx])
    p_min_mts = funcToFit(typef, speed,coef_min[par_indx])
    print ('****************************')
    print(f"{parameter} Boundaries @ {speed} {label}")
    print(f"min: {p_min_mts}")
    print(f"max: {p_max_mts}")
    return speed, p_max_mts, p_min_mts

def valueSpeedlist(speed, parameter, coef_max, coef_min,params, typef):
    par_indx = params.index(parameter)
    p_max, p_min, p_mean = [],[],[]
    for i, v in enumerate(speed):
        p_max_mts = funcToFit(typef,v,coef_max[par_indx])
        p_min_mts = funcToFit(typef, v,coef_min[par_indx])
        p_mean_mts = (p_max_mts+p_min_mts)/2
        p_max.append(p_max_mts)
        p_min.append(p_min_mts)
        p_mean. append(p_mean_mts)
    return speed, p_max, p_min,p_mean
def plotData(df,
             x_parm,
             y_parms= ['SPEED (rpm)', 'CURRENT (A)'],
             transparency=None,
             upper_bound=None,
             lower_bound=None,
             bound_color = None,
             x_new = None,
             n_rows = 2,
             title = 'Data',
             plot_type = 'line',
             fig = None,
             axes = None,
             label = None,
             colorCode = 6,
             annotation_max=False):
    
    x_data = df[x_parm]
    colors_dict = {
        "gray": "#525252ff",
        "teal": "#009494ff",
        "turquoise": "#00d0b8",
        "sky_blue": "#0FAAF0",
        "red": "#f74242ff",
        "orange": "#f7941d",
        "navy_blue": "#0F3878",
        "dark_red": "#9e0012ff",
        "black": "black"}
    if label is None:
        label = ''
    else:
        label=f'({label})'
            
    colors = list(colors_dict.values())
    
    if len(y_parms)%n_rows ==0:
        n_cols = int(len(y_parms)/n_rows)
    elif  len(y_parms)/n_rows ==1:
        n_cols = 1
    else:
        n_cols = int(len(y_parms)/n_rows)+1
    if fig is not None:
        fig = fig
        axes = axes
    else:
        fig, axes = plt.subplots(n_rows, n_cols, figsize=(20, 14))
            
    fig.tight_layout(pad=6.0)
    axes = np.ravel([axes])
    fig.suptitle(f'{title}',fontsize = 20)
    fig.subplots_adjust(top=0.9)
    if transparency is not None:
        alpha = transparency
    else:
        alpha = 1
    if plot_type == 'line':
        marker = ''
        linestyle='-'
        markersize=0
    elif plot_type =='dot':
        marker = 'o'
        linestyle=''
        markersize=4
    for i,(ax, param) in enumerate(zip(axes, y_parms)):
        y_data = df[param]
        ax.plot(x_data, y_data, label=f'{param}{label}',alpha = alpha,linestyle = linestyle,marker=marker,markersize=markersize, color=colors[colorCode] )
        if annotation_max:
            annotate_max(ax, df, param, label, colors[colorCode], i, x_param =x_parm )

        if x_new is None:
            x_new = x_data
        if bound_color is not None:
            color1=colors[bound_color]
            color2=color1=colors[bound_color]
        else:
            color1 =colors_dict["red"]
            color2 =colors_dict["sky_blue"]
            
                
        if upper_bound is not None:
            
            ax.plot(x_new, upper_bound[i],color=color1,lw=2,label=f"Upper Bound {label}")
        if lower_bound is not None:
            ax.plot(x_new, lower_bound[i],color=color2,lw=2,label=f"lower Bound {label}")
        ax.set_xlabel(f'{x_parm}')
        ax.set_ylabel(param)
        # ax.set_ylim(y_data.min()-y_data.max()*0.3,y_data.max()*1.3)
        ax.set_title(f'{param} vs {x_parm}')
        ax.legend()
        ax.grid(True)