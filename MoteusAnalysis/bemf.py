# -*- coding: utf-8 -*-
"""
Created on Thu Mar  6 14:27:57 2025

@author: kkeramati
"""
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
def filter_close_numbers(numbers, threshold=20):
    filtered = []
    for num in numbers:
        if not filtered or (num - filtered[-1]) >= threshold:
            filtered.append(num)
    return filtered

colors_dict = {
    "dark_red": "#9e0012ff",
    "orange": "#f7941d",
    "gray": "#525252ff",
    "teal": "#009494ff",
    "turquoise": "#00d0b8",
    "navy_blue": "#0F3878",
    "sky_blue": "#0FAAF0",
    "red": "#f74242ff",
    "black": "black"}
colors = list(colors_dict.values())

phases = ['BR']
fldr_path = './data/motorParameters/motor00_parameters/Bemf/'

file_neme = f'{phases[0]}_speed2.csv'
file_path = fldr_path + file_neme
# Inspect the raw contents of the file to check for delimiter issues
with open(file_path, "r", encoding="utf-8") as file:
    lines = file.readlines()

lines[:10]

data_start_index = next(i for i, line in enumerate(lines) if not line.startswith('%'))

df = pd.read_csv(file_path, skiprows=data_start_index)


df.columns = ["Time (s)", "Channel A (V)"]
df["Time (s)"] = df["Time (s)"] -df["Time (s)"].min()
signal = df["Channel A (V)"].values
time = df["Time (s)"].values

dt = np.mean(np.diff(time))  # Average time step

zero_indices = df.index[df['Channel A (V)'] == 0].tolist()
zero_indices = filter_close_numbers(zero_indices, threshold=20)
    
    
    
plt.figure(figsize=(10, 5))
    
plt.plot(df["Time (s)"][zero_indices[0]:zero_indices[2]], df["Channel A (V)"][zero_indices[0]:zero_indices[2]], label="Channel A", color=colors[0])
plt.xlabel("Time (s)")
plt.ylabel("Voltage (V)")
plt.title("Oscilloscope Data - Channel A")
plt.legend()
plt.grid()
plt.show()


signal = df["Channel A (V)"][zero_indices[0]:zero_indices[2]]*10

n = len(signal)
F = 50
H=[1]
# Generate time vector
# time = np.linspace(1 / (F * n), 1 / F, n)
time = df["Time (s)"][zero_indices[0]:zero_indices[2]]
time = time - time.min()
# Compute Fourier Transform
fft_values = np.fft.fft(signal)/len(signal)*2
frequencies = np.fft.fftfreq(len(signal), d=dt)
positive_freqs = frequencies[:len(frequencies)//2]
positive_fft = np.abs(fft_values[:len(frequencies)//2])

phase_angle = np.angle(fft_values)

max_v = positive_fft.max()
max_freq = positive_freqs[np.where(positive_fft==max_v)][0]

max_v = np.round(max_v, 3)
max_freq = np.round(max_freq, 3)

print(f'voltage{max_v} (V)@ {max_freq}Hz')
# Compute OUT matrix
# OUT = np.zeros((len(time), len(H)))
# for i, h in enumerate(H):
#     if h - 1 < len(Fourier2):  # Avoid index errors
#         OUT[:, i] = Fourier2[h - 1] * np.cos(h * 2 * np.pi * F * time + Angles[h - 1])

# Plot FFT Spectrum
# frequencies = np.fft.fftfreq(n, d=1/(F*n))[:n//2]
# frequencies1 = np.fft.fftfreq(len(signal), d=dt)
# positive_freqs = frequencies1[:len(frequencies1)//2]

plt.figure(figsize=(10, 5))
plt.plot(positive_freqs, positive_fft, label="Magnitude Spectrum", color='r')
plt.xlabel("Frequency (Hz)")
plt.ylabel("Amplitude")
plt.title("FFT of the Signal")
plt.grid()
plt.legend()
plt.show()

plt.figure()
first_harmonic = max_v * np.sin(1 * 2 * np.pi * max_freq * time + phase_angle.max())
plt.plot( first_harmonic)
plt.plot(signal)
plt.grid()
# Plot First Harmonic
# if len(H) > 0:
#     h1 = H[0]  # First harmonic
#     if h1 - 1 < len(Fourier2):
#         first_harmonic = Fourier2[h1 - 1] * np.cos(h1 * 2 * np.pi * F * time + Angles[h1 - 1])
#         plt.figure(figsize=(10, 5))
#         plt.plot(time, first_harmonic, label=f"First Harmonic (H={h1})", color='b')
#         plt.plot()
#         plt.xlabel("Time (s)")
#         plt.ylabel("Amplitude")
#         plt.title("First Harmonic of the Signal")
#         plt.grid()
#         plt.legend()
#         plt.show()
    

