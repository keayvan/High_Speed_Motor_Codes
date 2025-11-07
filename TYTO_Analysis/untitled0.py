# -*- coding: utf-8 -*-
"""
Created on Thu Oct 30 15:44:18 2025

@author: kkeramati
"""

import numpy as np
from matplotlib import pyplot as plt


x=np.linspace(0, 1000,100)
def model_exp(x, a,b):
    return a * np.exp(b*x)


y = model_exp(x,1,0.01)
plt.figure
plt.plot(x,y , 'o-')