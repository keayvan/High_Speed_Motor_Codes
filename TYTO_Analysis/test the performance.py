# -*- coding: utf-8 -*-
"""
Created on Mon Sep 29 15:23:12 2025

@author: kkeramati
"""

import pandas as pd
FILE_PATH = './Results_TYTO/'
FILE_PATTERN = 'throttle_Speed_th1200.csv'
df = pd.read_csv(FILE_PATH+FILE_PATTERN)

time_col = 'Time (s)'
throttle_col = 'Powertrain 1 - ESC throttle (μs)'
thrust_col = 'Powertrain 1 - force Fz (thrust) (N)'
torque_col = 'Powertrain 1 - torque MZ (torque) (N⋅m)'
voltage_col = 'Powertrain 1 - voltage (V)'
current_col = 'Powertrain 1 - current (A)'
rpm_col = 'Powertrain 1 - rotation speed (rpm)'
power_col = 'Powertrain 1 - electrical power (W)'
mech_power_col = 'Powertrain 1 - mechanical power (W)'
efficiency_col = 'Powertrain 1 - motor & ESC efficiency (%)'
prop_eff_col = 'Powertrain 1 - propeller efficiency (N/W)'
sys_eff_col = 'Powertrain 1 - powertrain efficiency (N/W)'

numeric_cols_to_average = [
    thrust_col, torque_col, voltage_col, current_col, rpm_col,
    power_col, mech_power_col, efficiency_col, prop_eff_col, sys_eff_col]

df_averaged = df.groupby(throttle_col, as_index=False)[numeric_cols_to_average].mean()