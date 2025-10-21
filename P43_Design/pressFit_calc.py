import numpy as np
from matplotlib import pyplot as plt
import matplotlib.font_manager

def contact_pressure(T, mu, d, L):
    """
    Compute required contact pressure [Pa] to transmit torque by friction.
    """
    if mu <= 0 or d <= 0 or L <= 0:
        raise ValueError("Friction coefficient, diameter, and length must be positive.")
    p_req = (2 * T) / (mu * np.pi * d**2 * L)
    return p_req


def interference_from_pressure_lame(p,
                                    d, d_shaft_inner,
                                     d_hub_outer,
                                    E_shaft, nu_shaft,
                                    E_hub, nu_hub,
                                    diametral=False):
    """
    Compute required interference [m] for a given contact pressure [Pa]
    using Lame's equations (Classical Elastic Theory).
    """
    r_shaft_outer= d/2.0
    r_shaft_inner = d_shaft_inner/2.0
    r_hub_inner =r_shaft_outer
    r_hub_outer = d_hub_outer/2.0
    # Shaft deformation term
    term_shaft = (r_shaft_outer / E_shaft) * (
        (r_shaft_outer**2 + r_shaft_inner**2) / (r_shaft_outer**2 - r_shaft_inner**2) - nu_shaft
    )

    # Hub deformation term
    term_hub = (r_hub_inner / E_hub) * (
        (r_hub_outer**2 + r_hub_inner**2) / (r_hub_outer**2 - r_hub_inner**2) - nu_hub
    )

    # Total radial interference
    delta_radial = p * (term_shaft + term_hub)

    # Convert to diametral interference if requested
    return 2 * delta_radial if diametral else delta_radial


# ---------------- Example Usage ----------------
if __name__ == "__main__":
    
    font_name = 'Century Gothic'
    try:
        if font_name not in matplotlib.font_manager.findSystemFonts(fontext='ttf'):
            raise FileNotFoundError
        plt.rcParams['font.family'] = font_name
    except:
        # Use a common, readable font if the requested one is not found
        plt.rcParams['font.family'] = 'sans-serif'
        plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'DejaVu Sans']
    # Given torque requirements
    Sf = 1.5
    T = 0.85       # N·m
    T= Sf*T
    mu = 0.2   # friction coefficient
    # Materials
    E_st = 210e9
    nu_st = 0.3
    
    E_al = 70e9
    nu_al = 0.33
    
    region = 'shaft'
    do=43/1000      
    d = 8/1000
    di = 0        # shaft diameter [m]
    L = 3.9/1000        # contact length [m]
    E_shaft = E_st   # Pa
    nu_shaft = nu_st
    E_hub = E_al     # Pa
    nu_hub = nu_al

    p_req = contact_pressure(T, mu, d, L)

    delta_diam = interference_from_pressure_lame(
        p_req,
        d, di,
        do,
        E_shaft, nu_shaft, E_hub, nu_hub,
        diametral=True
    )
    print('************************************')
    print(f"P_{region}: {p_req/1e6:.2f} MPa")
    print(f"Interference_{region}: {delta_diam*1e6:.2f} µm, {delta_diam*1e3:.4f} mm")
    
    
    region = 'rotor'
    do=43/1000      
    d = 39.38/1000
    di = 8/1000        # shaft diameter [m]
    L = 2.8/1000        # contact length [m]
    E_shaft = E_al   # Pa
    nu_shaft = nu_al
    E_hub = E_st     # Pa
    nu_hub = nu_st

    p_req = contact_pressure(T, mu, d, L)

    delta_diam = interference_from_pressure_lame(
        p_req,
        d, di,
        do,
        E_shaft, nu_shaft, E_hub, nu_hub,
        diametral=True
    )
    print('************************************')
    print(f"P_{region}: {p_req/1e6:.2f} MPa")
    print(f"Interference_{region}: {delta_diam*1e6:.2f} µm, {delta_diam*1e3:.4f} mm")
    
    T = 0.85 
    Sf= 1.5      # N·m
    T= Sf*T
    mu = 0.2 
    d=39.38/1000
    ll = [3.5,4,4.5,5,]
    p_all=[]
    for l in ll:
        p_req = contact_pressure(T, mu, d, l/1000)
        p_all.append(p_req/1e6)
        
    plt.figure()
    plt.plot(ll,p_all, '-o')
    plt.xlabel('Contact Width (mm)', fontsize=14)
    plt.ylabel('Contact Pressure (MPa)', fontsize=14)
    plt.grid(True, linestyle='--', alpha=0.6)

    

        