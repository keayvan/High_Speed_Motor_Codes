# -*- coding: utf-8 -*-
"""
Created on Thu Sep 25 17:34:14 2025

@author: kkeramati
"""

import matplotlib.pyplot as plt
palette = {
"teal_dark": "#009494ff",
"teal_light": "#00d0b8",
"lime_green": "#0AFFA0",
"navy_dark": "#0F3878",
"blue_medium": "#0f75bcff",
"sky_blue": "#0FAAF0",
"cyan_bright": "#29e2ecff",
"crimson_dark": "#9e0012ff",
"red_bright": "#f74242ff",
"coral_pink": "#ff596c",
"taupe": "#95755A",
"orange_bright": "#f7941dff",
"peach_orange": "#ffad5aff",
"gray_dark": "#525252ff",
"gray_medium": "#848484ff"
}

colors = list(palette.values())
# Natural frequencies in Hz
x= [1,2,3,4,5]
frequencies = [5503.8, 7421.5, 7421.6, 7754, 9775.3]

# Motor speeds in RPM
motor_speeds_rpm = [15000, 20000, 25000, 30000]

# Convert RPM to Hz (1 RPM = 1/60 Hz)
motor_speeds_hz = [rpm / 60 for rpm in motor_speeds_rpm]

# Plot natural frequencies as horizontal lines
# for f in frequencies:
#     plt.axhline(y=f, color='blue', linestyle='--', alpha=0.7, label=f"Nat. freq {f} Hz" if f == frequencies[0] else "")
plt.figure()
plt.plot(x, frequencies,'o-',color = palette["red_bright"],mfc= palette["cyan_bright"], label ='Natural frequencies')
# Plot motor speeds as vertical lines
for i, speed in enumerate(motor_speeds_hz):
    plt.axhline(y=speed, color=colors[i-1], linestyle='-', alpha=0.7, label=f"frequency @{motor_speeds_rpm[i]} rpm" )

# Labels & Legend
plt.xlabel("Natural Frequency No.")
plt.ylabel("Frequency [Hz]")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()