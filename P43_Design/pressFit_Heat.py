import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
rcParams['font.family'] = 'Century Gothic'


# --- Material properties (1/°C) ---
CTE_steel = 12e-6       # Steel coefficient of thermal expansion
CTE_aluminum = 23e-6    # Aluminum coefficient of thermal expansion

# --- Select configuration ---
# Case 1: Steel shaft in Aluminum hub
CTE_shaft = CTE_steel
CTE_hub = CTE_aluminum

# Case 2 (optional): Aluminum shaft in Steel hub
# CTE_shaft = CTE_aluminum
# CTE_hub = CTE_steel

# --- Geometry and fit parameters ---
D = 8               # nominal diameter [mm]
interference_0 = 0.0018   # initial interference [mm]
T0 = 120              # reference temperature [°C]

# --- Temperature range to analyze ---
T_min, T_max = -20, 120
temperatures = np.linspace(T_min, T_max, 200)

# --- Compute interference at each temperature ---
delta_T = interference_0 + D * (CTE_shaft - CTE_hub) * (temperatures - T0)

# --- Plot results ---
plt.figure(figsize=(8,5))
plt.plot(temperatures, delta_T, label='Interference vs Temperature', color='#0F3878')
plt.axhline(0, color='#ff596c', linestyle='--', label='Zero Interference')
plt.xlabel('Temperature [°C]')
plt.ylabel('Interference [mm]')
plt.title('Press Fit Behavior vs Temperature for Shaft & Casing')
plt.legend()
plt.grid(True)
plt.show()

# --- Print results ---
delta_low = delta_T[0]
delta_high = delta_T[-1]

T = 20
corresponding_value = np.interp(T, temperatures, delta_T)

print(f"=== Press Fit Analysis Shaft region ===")
print(f"Nominal diameter: {D:.1f} mm")
print(f"Initial interference at {T0}°C: {interference_0:.4f} mm")
print(f"Interference at {T_min}°C: {delta_low:.4f} mm")
print(f"Interference at {T_max}°C: {delta_high:.4f} mm")
print(f"Interference at {T}°C: {corresponding_value:.4f} mm {corresponding_value*1000:.1f} µm")


# --- Interpret results correctly ---
if delta_high < 0:
    print(f"⚠️ At {T_max}°C, the fit becomes LOOSE (clearance fit).")
else:
    print(f"✅ At {T_max}°C, the fit remains TIGHT (still interference).")

if delta_low > 0:
    print(f"✅ At {T_min}°C, the fit remains TIGHT (interference increases when cold).")
else:
    print(f"⚠️ At {T_min}°C, the fit becomes LOOSE (clearance when cold).")

# --- Summary of configuration ---
if CTE_shaft < CTE_hub:
    print("\nConfiguration: Steel shaft in Aluminum hub → fit loosens when hot.")
else:
    print("\nConfiguration: Aluminum shaft in Steel hub → fit tightens when hot.")
    
    
CTE_shaft = CTE_aluminum
CTE_hub = CTE_steel 

# Case 2 (optional): Aluminum shaft in Steel hub
# CTE_shaft = CTE_aluminum
# CTE_hub = CTE_steel

# --- Geometry and fit parameters ---
D = 39              # nominal diameter [mm]
interference_0 = 0.0012   # initial interference [mm]
T0 = -20               # reference temperature [°C]

# --- Temperature range to analyze ---
T_min, T_max = -20, 120
temperatures = np.linspace(T_min, T_max, 200)

# --- Compute interference at each temperature ---
delta_T = interference_0 + D * (CTE_shaft - CTE_hub) * (temperatures - T0)

# --- Plot results ---
plt.figure(figsize=(8,5))
plt.plot(temperatures, delta_T, label='Interference vs Temperature', color='#0F3878')
plt.axhline(0, color='#ff596c', linestyle='--', label='Zero Interference')
plt.xlabel('Temperature [°C]')
plt.ylabel('Interference [mm]')
plt.title('Press Fit Behavior vs Temperature for Rotor & Casing')
plt.legend()
plt.grid(True)
plt.show()

# --- Print results ---
delta_low = delta_T[0]
delta_high = delta_T[-1]

T = 20

corresponding_value = np.interp(T, temperatures, delta_T)


print(f"=== Press Fit Analysis Rotor region===")
print(f"Nominal diameter: {D:.1f} mm")
print(f"Initial interference at {T0}°C: {interference_0:.4f} mm")
print(f"Interference at {T_min}°C: {delta_low:.4f} mm")
print(f"Interference at {T_max}°C: {delta_high:.4f} mm")
print(f"Interference at {T}°C: {corresponding_value:.4f} mm & {corresponding_value*1000:.1f} µm")


# --- Interpret results correctly ---
if delta_high < 0:
    print(f"⚠️ At {T_max}°C, the fit becomes LOOSE (clearance fit).")
else:
    print(f"✅ At {T_max}°C, the fit remains TIGHT (still interference).")

if delta_low > 0:
    print(f"✅ At {T_min}°C, the fit remains TIGHT (interference increases when cold).")
else:
    print(f"⚠️ At {T_min}°C, the fit becomes LOOSE (clearance when cold).")

# --- Summary of configuration ---
if CTE_shaft < CTE_hub:
    print("\nConfiguration: Steel shaft in Aluminum hub → fit loosens when hot.")
else:
    print("\nConfiguration: Aluminum shaft in Steel hub → fit tightens when hot.")

