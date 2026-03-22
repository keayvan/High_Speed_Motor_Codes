import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# === Load your CSV file ===
df = pd.read_csv("./Results_TYTO/MGM_100A_steps5s.csv")  # or full path if needed

# Extract relevant columns
x = df["Powertrain 1 - rotation speed (rpm)"].values
y = df["Powertrain 1 - current (A)"].values

# Clean data (remove NaN or Inf)
mask = np.isfinite(x) & np.isfinite(y)
x = x[mask]
y = y[mask]

# === Define the exponential model ===
def expo(x, a, b):
    return a * np.exp(b * x)

# === Fit the model ===
popt, _ = curve_fit(expo, x, y, p0=[1, 1e-4], maxfev=200000)
a, b = popt

# === Compute fitted curve ===
x_fit = np.linspace(min(x), max(x), 500)
y_fit = expo(x_fit, a, b)

# === Compute R² ===
y_pred = expo(x, a, b)
ss_res = np.sum((y - y_pred)**2)
ss_tot = np.sum((y - np.mean(y))**2)
r2 = 1 - ss_res / ss_tot

# === Plot ===
plt.figure(figsize=(8,6))
plt.scatter(x, y, label="Data", alpha=0.7)
plt.plot(x_fit, y_fit, 'r-', label=f"Fit: y = {a:.3f} * exp({b:.6f}x)\nR²={r2:.4f}")
plt.xlabel("Powertrain 1 - rotation speed (rpm)")
plt.ylabel("Powertrain 1 - current (A)")
plt.title("Exponential Fit (no offset): Speed → Current")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

# === Print fitted parameters ===
print(f"a = {a:.6f}")
print(f"b = {b:.6f}")
print(f"R² = {r2:.6f}")
