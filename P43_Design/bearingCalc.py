# -*- coding: utf-8 -*-
"""
Created on Wed Sep 10 13:22:56 2025

@author: kkeramati
"""

from matplotlib import pyplot as plt

def required_C_deep_groove(T, d, n, L10h):
    """
    Calculate required basic dynamic load rating C for a deep-groove ball bearing.
    
    Parameters:
        T (float): Shaft torque in N·m
        d (float): Effective diameter where torque is transmitted (m)
        n (float): Speed in rpm
        L10h (float): Desired bearing life in hours
    
    Returns:
        C (float): Required basic dynamic load rating (N)
        P (float): Equivalent dynamic load (N)
        L10 (float): Bearing life in million revolutions
    """
    # Radial force from torque
    Fr = 2 * T / d    # N
    
    # Equivalent dynamic load (no axial load for deep-groove ball)
    P = Fr
    
    # Convert life to million revolutions
    L10 = (60 * n * L10h) / 1e6
    
    # Exponent for ball bearings
    p = 3.0
    
    # Required C
    C = P * (L10 ** (1/p))
    
    return C, P, L10

def static_load_requirements(Fr, Fa=0.0, X0=None, Y0=None, safety_factors=1.6):
    """
    Compute equivalent static load P0 and required C0 for a set of safety factors.
    
    Parameters:
        Fr (float): radial load (N)
        Fa (float): axial load (N), default 0
        X0 (float or None): static factor X0 from catalogue (if None and Fa==0, X0 assumed 1)
        Y0 (float or None): static factor Y0 from catalogue (if None and Fa==0, Y0 assumed 0)
        safety_factors (iterable): list/tuple of safety factors to compute required C0
    
    Returns:
        dict with keys:
            'P0' : equivalent static load (N)
            'C0_required' : {s: value} dict of required C0 for each safety factor
    """
    # if no axial load or no X0/Y0 provided, assume pure radial
    if Fa == 0.0:
        P0 = Fr
    else:
        if X0 is None or Y0 is None:
            raise ValueError("For combined loads provide X0 and Y0 from the bearing catalogue.")
        P0 = X0 * Fr + Y0 * Fa

    C0_req = P0 * safety_factors
    return P0, C0_req


if __name__ == "__main__":
    # Given data
    Ti = 0.7          # N·m (max torque)
    di = 0.043         # m (rotor OD)
    ni = 30000         # rpm (max speed)
    L10hi = 100     # desired life in hours

    Ci, Pi, L10i = required_C_deep_groove(Ti, di, ni, L10hi)
    P0i, C0i = static_load_requirements(Pi)
    n_flights = L10hi*60/40


    print(f"Estimated number of flights(40 min) = {round(n_flights)}")   
    print('**************************')    
    print(f"Dynamic load P = {Pi/1000:.2f} kN")
    print(f"Static load = {P0i/1000:.2f} kN")
    print('**************************')

    print(f"Basic dynamic load rating C = {Ci/1000:.2f} kN") 
    print(f"Basic static load rating C0 =  {C0i/1000:.2f} kN")
    
    print(f"Static Load frac = {P0i/C0i:.2f}") 
    
    L10h_list = [100,300,500,1000,2000,3000,4000,5000,6000,8000,10000]
    C_L10h_all = []
    for i,v in enumerate(L10h_list):
        C, P, L10 = required_C_deep_groove(Ti, di, ni, v)
        C_L10h_all.append(C/1000)
    
    plt.figure()
    plt.plot(L10h_list, C_L10h_all,'-o', color = '#0F3878', mfc='#009494ff', mec='#0F3878')
    plt.xlabel('L10h')
    plt.ylabel('Dynamic Static Load Rating (kN)')
        

        
    
    
    sf = [1,1.2,1.4,1.6,1.8,2,2.2,2.4,2.6,2.8,3,3.2]
    C0_sf_all = []
    for i,v in enumerate(sf):
        P0, C0 = static_load_requirements(Pi,safety_factors=v)
        C0_sf_all.append(C0/1000)
        
    plt.figure()
    plt.plot(sf, C0_sf_all,'-o', color = '#f74242ff', mfc='#0FAAF0', mec='#f74242ff')
    plt.xlabel('SF')
    plt.ylabel('Basic Static Load Rating (kN)')
    
    Torque = [0.3, 0.5, 0.7, 0.9 ,1, 1.1, 1.3, 1.5, 1.7, 1.9]
    C0_t_all=[]
    for i, v in enumerate(Torque):
        C, P, L10 = required_C_deep_groove(v, di, ni, L10hi)
        P0, C0 = static_load_requirements(P,safety_factors=1.5)
        C0_t_all.append(C0/1000)

    plt.figure()
    plt.plot(Torque, C0_t_all,'-o', color = '#009494ff', mfc='#009494ff', mec='#0F3878')
    plt.xlabel('Output Torque (N.m)')
    plt.ylabel('Basic Static Load Rating (kN)')
        