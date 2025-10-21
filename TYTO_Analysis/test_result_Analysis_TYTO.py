# -*- coding: utf-8 -*-
"""
Created on Tue Sep  9 15:56:10 2025

@author: kkeramati
"""


import pandas as pd
import matplotlib.pyplot as plt
import os
import math

# Function to plot chosen parameters vs time in separate subplots
def plot_parameters(df, parameters, x='Time (s)', description="", n_rows=None):
    cols = df.columns[1:].tolist()
    Powertrain = os.path.commonprefix(cols)
    
    n_params = len(parameters)
    if n_rows is None:
        # Automatically choose number of rows (try to make it roughly square)
        n_rows = math.ceil(math.sqrt(n_params))
    n_cols = math.ceil(n_params / n_rows)

    params = [Powertrain + p for p in parameters]
    if x != 'Time (s)':
        x = Powertrain + x

    fig, axes = plt.subplots(n_rows, n_cols, figsize=(5 * n_cols, 3 * n_rows), sharex=True)
    axes = axes.flatten() if n_params > 1 else [axes]
    
    colrs = ['#009494ff', '#0F3878', '#ff596c', '#f7941dff', '#525252ff',
             '#009494ff', '#0F3878', '#ff596c', '#f7941dff', '#525252ff']
    
    xx = df[x]
    for i, param in enumerate(params):
        if param in df.columns:
            axes[i].plot(xx, df[param], 'o-', label=param, color=colrs[i % len(colrs)], lw=1, ms=2)
            axes[i].set_ylabel(parameters[i])
            axes[i].legend(fontsize=8)
            axes[i].grid(True)
        else:
            print(f"Warning: {param} not found in dataframe columns")

    # Hide unused subplots (if any)
    for j in range(len(params), len(axes)):
        fig.delaxes(axes[j])

    axes[-1].set_xlabel("Time (s)")
    plt.suptitle(f"Results {description}", fontsize=14)
    plt.tight_layout(rect=[0, 0, 1, 0.97])
    plt.show()
    

def plot_parameters_multi(dfs, parameters, x='Time (s)', description="", n_rows=None):
    n_params = len(parameters)

    # Automatically determine grid shape if not specified
    if n_rows is None:
        n_rows = math.ceil(math.sqrt(n_params))
    n_cols = math.ceil(n_params / n_rows)

    fig, axes = plt.subplots(n_rows, n_cols, figsize=(5 * n_cols, 3 * n_rows), sharex=True)
    axes = axes.flatten() if n_params > 1 else [axes]

    colors = ['#009494ff', '#0F3878', '#ff596c', '#f7941dff', '#525252ff'
              ]

    for i, param in enumerate(parameters):
        ax = axes[i]
        for j, df in enumerate(dfs):
            cols = df.columns[1:].tolist()
            Powertrain = os.path.commonprefix(cols)
            param_col = Powertrain + param
            x_col = Powertrain + x if x != 'Time (s)' else x

            if param_col in df.columns:
                ax.plot(
                    df[x_col], df[param_col],
                    'o-', lw=1, ms=1.5,
                    color=colors[j % len(colors)],
                    label=f"{Powertrain}"
                )
            else:
                print(f"Warning: {param_col} not found in dataframe {Powertrain}")
        
        ax.set_ylabel(param)
        ax.legend(fontsize=8)
        ax.grid(True)

    # Hide unused subplots (if grid is larger than needed)
    for j in range(n_params, len(axes)):
        fig.delaxes(axes[j])

    axes[-1].set_xlabel(x)
    plt.suptitle(f"Results {description}", fontsize=14)
    plt.tight_layout(rect=[0, 0, 1, 0.97])
    plt.show()
    
def read_result(file_path):
    df = pd.read_csv(file_path)
    
    return df

def cycle_func(dfff, n_cycle = 2):
    df_list = []
    dff = dfff.copy()
    time = dff.iloc[0:int(len(dff)/n_cycle),0]

    for i in range(n_cycle):
        df11 = dff.iloc[i*int(len(dff)/n_cycle):(i+1)*int(len(dff)/n_cycle),:]
        df11.iloc[:,0] = time
        df_list.append(df11)
    
    return df_list

# Example usage
if __name__ == "__main__":
    file_path = "./Results_TYTO/withPropeller_MGM_MaxSpeed.csv"  # change path if needed
    df0 = read_result(file_path)
    df0 = df0.iloc[:,:]
    
    file_path1 = "./Results_TYTO/MGM_Propeller.csv"
    df1 = read_result(file_path1)
    df1=df1.iloc[:,:]
    
    df_s =  cycle_func(df0, n_cycle = 2)
    plot_parameters_multi([df1], [
        'electrical power (W)',
        'voltage (V)',
        'current (A)',
        'ESC throttle (μs)',
        'rotation speed (rpm)',
        'force Fz (thrust) (N)',
        'torque MZ (torque) (N⋅m)',
        'powertrain efficiency (N/W)'
        ],n_rows =3)
    

    
    plot_parameters_multi([df_s[0],df1.iloc[:-70,:]], [
        'electrical power (W)',
        'powertrain efficiency (N/W)',
        'current (A)'],
        x= 'rotation speed (rpm)')
    
    # plot_parameters_multi(dfs=[dff[0],df1.iloc[:-20,:]],
    #                       parameters=['electrical power (W)','voltage (V)','current (A)'],
    #                       description="Comparision With Propeller",
    #                       x= 'rotation speed (rpm)') 
    
    # plot_parameters_multi(dfs=dff,
    #                       parameters=['electrical power (W)','voltage (V)','current (A)'],
    #                       description="Comparision With Propeller",
    #                       x= 'rotation speed (rpm)') 
    
    # plot_parameters_multi(dfs=[df1],
    #                       parameters=['torque MZ (torque) (N⋅m)','rotation speed (rpm)','current (A)'],
    #                       description="Throttle Correlatin",
    #                       x= 'ESC throttle (μs)')
    
    # plt.figure()
    # plt.plot(df['Time (s)'],df['Powertrain 1 - torque MZ (torque) (N⋅m)'])
    # x=int(len(df['Powertrain 1 - torque MZ (torque) (N⋅m)'])/2)
    # plt.figure()
    # plt.plot (range(len(df['Powertrain 1 - torque MZ (torque) (N⋅m)'][:x])),df['Powertrain 1 - torque MZ (torque) (N⋅m)'][:x])
    # plt.plot (range(len(df['Powertrain 1 - torque MZ (torque) (N⋅m)'][x:])),df['Powertrain 1 - torque MZ (torque) (N⋅m)'][x:])
    
    # plt.figure()
    # plt.plot (range(len(df['Powertrain 1 - torque MZ (torque) (N⋅m)'][:x])),df['Powertrain 1 - current (A)'][:x])
    # plt.plot (range(len(df['Powertrain 1 - torque MZ (torque) (N⋅m)'][x:])),df['Powertrain 1 - current (A)'][x:])
    
    # plt.figure()
    # plt.plot (range(len(df['Powertrain 1 - torque MZ (torque) (N⋅m)'][:x])),df['Powertrain 1 - rotation speed (rpm)'][:x])
    # plt.plot (range(len(df['Powertrain 1 - torque MZ (torque) (N⋅m)'][x:])),df['Powertrain 1 - rotation speed (rpm)'][x:])