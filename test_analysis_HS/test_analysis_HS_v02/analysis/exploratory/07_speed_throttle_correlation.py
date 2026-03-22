# -*- coding: utf-8 -*-
"""
Created on Sat Feb 14 18:51:51 2026

@author: kkeramati
"""
from pathlib import Path
import sys
from scipy.interpolate import interp1d
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
try:
    PROJECT_ROOT = Path(__file__).resolve().parents[2]
except NameError:
    # fallback for notebooks / interactive
    PROJECT_ROOT = Path.cwd().parent.parent

sys.path.insert(0, str(PROJECT_ROOT))
print(PROJECT_ROOT)

from analysis.features.TYTO_general import read_result
from analysis.features.general_functions import find_params_in_df
PROCESSED_DIR_TYTO = PROJECT_ROOT / "data" / "raw" / "TYTO"
PROCESSED_DIR_Salea = PROJECT_ROOT / "data" / "processed" 
SAVING_folder = PROJECT_ROOT / "data" / "post_proccessings"

plt.rcParams["font.family"] = "DejaVu Sans"

electronics = "ARC"
motors="P43_32193"
powertrain = electronics + "_" + motors
freq = ""
study_name = "correlation" 
speed_test = "steps"
time_format = "ms"
resampling_2nd = "manual"

TYTO_FILES_manual = f"{powertrain}_{study_name}{freq}_{speed_test}_{resampling_2nd}"
TYTO_csv_manual = TYTO_FILES_manual+".csv"

df_TYTO_manual = read_result(PROCESSED_DIR_TYTO / TYTO_csv_manual,
                 powertrain = powertrain,
                 Time = time_format)

params_to_find = [ "speed", "throttle"]
param_to_find = find_params_in_df(df_TYTO_manual, params_to_find)

df_correlation = df_TYTO_manual[param_to_find]

x_ARC = df_correlation.iloc[0:,1]
y_ARC = df_correlation.iloc[0:,0]

f = interp1d(x_ARC, y_ARC, kind='quadratic',fill_value = 'extrapolate')  # 'linear', 'quadratic', 'cubic'
speed_points = np.linspace(0, 15000, 1000)
throttle =[]
for i, v in enumerate(speed_points):
    th = f(v)
    throttle.append(float(np.round(th,2)))
    
############## Speed for Correlation
electronics1 = "MGM"
motors1="scorpion"
powertrain1 = electronics1 + "_" + motors1
freq1 = ""
study_name1 = "3phase_comparision" 
speed_test1 = "steps"
time_format1 = "ms"
resampling_2nd1 = "manual"
MGM_manual = f"{powertrain1}_{study_name1}{freq1}_{speed_test1}_{resampling_2nd1}"
MGM_csv_manual = MGM_manual+".csv"

df_MGM_manual = read_result(PROCESSED_DIR_TYTO / MGM_csv_manual,
                 powertrain = powertrain1,
                 Time = time_format)
indx_starting = 1
speed_param = f"{powertrain1} rotation speed (rpm)"
speed_points_from_MGM = list(df_MGM_manual[speed_param])[indx_starting:]

throttle_param = f"{powertrain1} ESC throttle (μs)"
throttle_points_from_MGM = list(df_MGM_manual[throttle_param])[indx_starting:]

num_points = len(speed_points_from_MGM)
step = 5

Time = [i * step for i in range(num_points)]

throttle_from_MGM1 =[]
for i, v in enumerate(speed_points_from_MGM):
    th = f(v)
    throttle_from_MGM1.append(float(np.round(th,2)))
throttle_from_MGM_fitting = [min(max(x, 1000), 2000) for x in throttle_from_MGM1]

plt.figure ()
plt.plot(x_ARC, y_ARC, '-o', color = "#0FAAF0", label = f"{powertrain}")
plt.plot(speed_points_from_MGM, throttle_points_from_MGM, '-o',color="orange", label = f"{powertrain1}")
plt.xlabel("Speed (rpm)")
plt.ylabel("Throttle")
plt.legend()
plt.grid("both")

plt.figure()
plt.plot(x_ARC, y_ARC, '-o', color = "#0FAAF0", label = f"Manual recorded {powertrain}")
plt.plot(speed_points, throttle, color = "#f74242ff", label = f"fitting for {powertrain}")
plt.plot(speed_points_from_MGM, throttle_from_MGM_fitting, 'o',mfc="orange", label = f"Test Points for {powertrain} from {powertrain1}")
plt.xlabel("Speed (rpm)")
plt.ylabel("Throttle")
plt.title("Correlation Pulsar")
plt.legend()
plt.grid("both")

print(throttle_from_MGM_fitting)

df = pd.DataFrame({
    "Time (s)": Time,
    "Take sample": "x",   # constant value (you can change this)
    "Powertrain 1 ESC throttle - target (μs)": throttle_from_MGM_fitting
})

# df.to_csv(PROCESSED_DIR_TYTO / "InputTYTO" / f"{powertrain}_profile_from_MGM.csv", index=False, encoding="utf-8-sig")

# print("File saved successfully.")