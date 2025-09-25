# -*- coding: utf-8 -*-
"""
Created on Tue Sep  9 15:56:10 2025

@author: kkeramati
"""


import pandas as pd
import matplotlib.pyplot as plt

# Read the CSV file
def read_csv(file_path):
    df = pd.read_csv(file_path)
    return df

# Function to plot chosen parameters vs time in separate subplots
def plot_parameters(df, parameters,color='blue'):
    n = len(parameters)
    fig, axes = plt.subplots(n, 1, figsize=(8, 8), sharex=True)
    colrs= ['#009494ff', '#0F3878', '#ff596c', '#f7941dff', '#525252ff']

    if n == 1:
        axes = [axes]
        

    for i, param in enumerate(parameters):
        if param in df.columns:
            axes[i].plot(df['Time (s)'], df[param], 'o-', label=param,color = colrs[i], ms = 4)
            axes[i].set_ylabel(param)
            axes[i].legend()
            axes[i].grid(True)
        else:
            print(f"Warning: {param} not found in dataframe columns")

    axes[-1].set_xlabel("Time (s)")
    plt.suptitle("Selected Parameters vs Time", fontsize=14)
    plt.tight_layout(rect=[0, 0, 1, 0.97])
    plt.show()

# Example usage
if __name__ == "__main__":
    file_path = "Throttle_1800.csv"  # change path if needed
    df = read_csv(file_path)

    # Example: plot thrust, current, and rpm vs time
    plot_parameters(df, [
        'Powertrain 1 - electrical power (W)',
        'Powertrain 1 - mechanical power (W)',
        'Powertrain 1 - motor & ESC efficiency (%)'
    ])
    
    plot_parameters(df, [
        'Powertrain 1 - electrical power (W)',
        'Powertrain 1 - voltage (V)',
        'Powertrain 1 - current (A)'],color='red')
    
    plot_parameters(df, [
        'Powertrain 1 - mechanical power (W)',
        'Powertrain 1 - rotation speed (rpm)',
        'Powertrain 1 - torque MZ (torque) (N⋅m)'],color='green')
    plot_parameters(df, [
        'Powertrain 1 - force Fz (thrust) (N)',
        'Powertrain 1 - torque MZ (torque) (N⋅m)'],color='green')