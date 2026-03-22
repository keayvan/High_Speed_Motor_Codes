# -*- coding: utf-8 -*-
"""
Created on Mon Dec 15 14:34:32 2025

@author: kkeramati
"""

#!/usr/bin/env python3
"""
Fixed-wing electric powertrain + mission simulator (simple, extensible).

"""


import math
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple


RHO0 = 1.225  # kg/m^3 at sea level
G = 9.80665


# -----------------------------
# Data structures
# -----------------------------
@dataclass
class Battery:
    cells_s: int
    capacity_ah: float
    internal_resistance_mohm: float
    v_cell_nom: float = 3.7

    @property
    def r_int_ohm(self) -> float:
        return self.internal_resistance_mohm / 1000.0

    @property
    def v_oc_nom(self) -> float:
        return self.cells_s * self.v_cell_nom

    @property
    def capacity_coulomb(self) -> float:
        return self.capacity_ah * 3600.0  # As


@dataclass
class Motor:
    kv_rpm_per_v: float
    rm_ohm: float
    i0_a: float
    max_current_a: float
    max_temp_c: Optional[float] = None


@dataclass
class ESC:
    max_current_a: float
    efficiency: float
    has_telemetry: bool = False


@dataclass
class PropModel:
    name: str
    diameter_in: float
    pitch_in: float

    # Option A: constants for Ct, Cq (rough)
    ct0: float = 0.10
    cq0: float = 0.04

    # Option B: polynomial coefficients for Ct(J) and Cq(J)
    # Ct(J) = a0 + a1*J + a2*J^2 + ...
    ct_poly: Optional[List[float]] = None
    cq_poly: Optional[List[float]] = None

    def diameter_m(self) -> float:
        return self.diameter_in * 0.0254

    def pitch_m(self) -> float:
        return self.pitch_in * 0.0254


@dataclass
class Aircraft:
    mass_kg: float
    wing_area_m2: Optional[float] = None
    cd0: float = 0.03
    k: float = 0.08


@dataclass
class Segment:
    name: str
    duration_s: float
    target_airspeed_mps: float
    required_thrust_n: Optional[float] = None  # if None, compute from aircraft model
    rho: float = RHO0


@dataclass
class Constraints:
    max_tip_mps: float = 220.0
    max_current_a: Optional[float] = None
    max_motor_temp_c: Optional[float] = None
    min_thrust_margin: float = 0.0  # N above required thrust (optional)


# -----------------------------
# Helper math
# -----------------------------
def poly_eval(coeffs: List[float], x: float) -> float:
    y = 0.0
    p = 1.0
    for a in coeffs:
        y += a * p
        p *= x
    return y


def compute_required_thrust_from_drag(aircraft: Aircraft, seg: Segment) -> float:
    if aircraft.wing_area_m2 is None:
        raise ValueError(
            f"Segment '{seg.name}' requires thrust but aircraft.wing_area_m2 is missing."
        )
    V = max(seg.target_airspeed_mps, 0.1)
    S = aircraft.wing_area_m2
    W = aircraft.mass_kg * G
    q = 0.5 * seg.rho * V * V
    Cl = W / (q * S)
    Cd = aircraft.cd0 + aircraft.k * (Cl * Cl)
    D = q * S * Cd
    return D


def prop_coefficients(prop: PropModel, V: float, n_rev_s: float) -> Tuple[float, float, float]:
    """
    Returns (Ct, Cq, J).
    """
    D = prop.diameter_m()
    n = max(n_rev_s, 1e-6)
    J = V / (n * D)

    if prop.ct_poly is not None and prop.cq_poly is not None:
        Ct = poly_eval(prop.ct_poly, J)
        Cq = poly_eval(prop.cq_poly, J)
    else:
        # Very rough default: constant coefficients (works only as a placeholder)
        Ct = prop.ct0
        Cq = prop.cq0
    return Ct, Cq, J


# -----------------------------
# Core solver for a segment
# -----------------------------
def solve_operating_point(
    battery: Battery,
    motor: Motor,
    esc: ESC,
    prop: PropModel,
    V_airspeed: float,
    thrust_required_n: float,
    constraints: Constraints,
    rho: float = RHO0,
) -> Dict[str, float]:
    """
    Solve for RPM and current such that prop thrust ~= required thrust.
    Uses a simple 1D search over RPM.
    """

    D = prop.diameter_m()
    kv = motor.kv_rpm_per_v
    rm = motor.rm_ohm
    i0 = motor.i0_a

    # constraint current
    max_i = min(
        motor.max_current_a,
        esc.max_current_a,
        constraints.max_current_a if constraints.max_current_a is not None else float("inf"),
    )

    # Search RPM range
    rpm_lo, rpm_hi = 1000.0, 45000.0  # adjust if needed
    best = None

    for _ in range(55):
        rpm_mid = 0.5 * (rpm_lo + rpm_hi)
        n = rpm_mid / 60.0  # rev/s

        Ct, Cq, J = prop_coefficients(prop, V_airspeed, n)

        # Prop thrust / torque
        T = Ct * rho * (n ** 2) * (D ** 4)
        Q = Cq * rho * (n ** 2) * (D ** 5)
        omega = 2.0 * math.pi * n
        P_shaft = omega * Q

        # Motor back-emf (approx)
        # RPM = Kv * V_emf => V_emf = RPM/Kv
        V_emf = rpm_mid / kv

        # Required motor electrical power ignoring losses would be P_shaft/eta_motor,
        # but we instead compute current from V_m = I*Rm + V_emf with minimum i0.
        # We also approximate that current must be enough to supply shaft power:
        # P_elec_motor ~= V_m * I ; but V_m depends on I too.
        # We'll do a consistent estimate:
        # Choose I such that V_m = V_emf + I*Rm and P_elec >= P_shaft + copper loss + no-load.
        # Simple approach:
        # Start with I from torque power: I_guess = max(i0, P_shaft / max(V_emf, 1e-3))
        I_guess = max(i0, P_shaft / max(V_emf, 1e-3))
        # Compute motor terminal voltage from I_guess
        V_m = V_emf + I_guess * rm
        # Battery voltage sag with ESC efficiency
        # V_m = V_batt * esc_eff  -> V_batt = V_m / eff
        V_batt = V_m / max(esc.efficiency, 1e-6)
        # With sag: V_batt = V_oc - I_batt*Rint ; assume I_batt ~= I_guess/eff
        I_batt = I_guess / max(esc.efficiency, 1e-6)
        V_batt_sag = battery.v_oc_nom - I_batt * battery.r_int_ohm

        # If sagged battery can't supply required V_batt, operating point not feasible
        feasible = V_batt_sag >= V_batt and I_guess <= max_i

        # Thrust margin check drives our search: we want T >= required + margin
        T_target = thrust_required_n + constraints.min_thrust_margin

        if feasible and T >= T_target:
            best = {
                "rpm": rpm_mid,
                "n_rev_s": n,
                "J": J,
                "Ct": Ct,
                "Cq": Cq,
                "thrust_n": T,
                "torque_nm": Q,
                "omega_rad_s": omega,
                "p_shaft_w": P_shaft,
                "i_motor_a": I_guess,
                "v_motor_v": V_m,
                "i_batt_a": I_batt,
                "v_batt_v": V_batt_sag,
                "p_batt_w": V_batt_sag * I_batt,
                "feasible": 1.0,
            }
            rpm_hi = rpm_mid  # try lower RPM if possible
        else:
            rpm_lo = rpm_mid

    # If no feasible solution, return the "closest" (highest thrust) point for diagnostics
    if best is None:
        rpm = rpm_hi
        n = rpm / 60.0
        Ct, Cq, J = prop_coefficients(prop, V_airspeed, n)
        T = Ct * rho * (n ** 2) * (D ** 4)
        Q = Cq * rho * (n ** 2) * (D ** 5)
        omega = 2.0 * math.pi * n
        P_shaft = omega * Q
        V_emf = rpm / kv
        I_guess = max(i0, P_shaft / max(V_emf, 1e-3))
        V_m = V_emf + I_guess * rm
        I_batt = I_guess / max(esc.efficiency, 1e-6)
        V_batt_sag = battery.v_oc_nom - I_batt * battery.r_int_ohm

        best = {
            "rpm": rpm,
            "n_rev_s": n,
            "J": J,
            "Ct": Ct,
            "Cq": Cq,
            "thrust_n": T,
            "torque_nm": Q,
            "omega_rad_s": omega,
            "p_shaft_w": P_shaft,
            "i_motor_a": I_guess,
            "v_motor_v": V_m,
            "i_batt_a": I_batt,
            "v_batt_v": V_batt_sag,
            "p_batt_w": V_batt_sag * I_batt,
            "feasible": 0.0,
        }

    # Tip speed constraint
    tip_speed = math.pi * D * best["n_rev_s"]  # m/s (pi*D*n)
    best["tip_speed_mps"] = tip_speed
    best["tip_ok"] = 1.0 if tip_speed <= constraints.max_tip_mps else 0.0

    # Current constraints
    best["current_ok"] = 1.0 if best["i_motor_a"] <= max_i else 0.0

    return best


# -----------------------------
# Mission simulator
# -----------------------------
def simulate_mission(
    battery: Battery,
    motor: Motor,
    esc: ESC,
    prop: PropModel,
    aircraft: Aircraft,
    mission: List[Segment],
    constraints: Constraints,
) -> Dict[str, Any]:
    q_remaining = battery.capacity_coulomb
    results: List[Dict[str, Any]] = []

    total_wh = 0.0
    feasible_all = True
    tip_all = True
    current_all = True

    for seg in mission:
        if seg.required_thrust_n is None:
            thrust_req = compute_required_thrust_from_drag(aircraft, seg)
        else:
            thrust_req = seg.required_thrust_n

        op = solve_operating_point(
            battery=battery,
            motor=motor,
            esc=esc,
            prop=prop,
            V_airspeed=seg.target_airspeed_mps,
            thrust_required_n=thrust_req,
            constraints=constraints,
            rho=seg.rho,
        )

        dt = seg.duration_s
        i_batt = max(op["i_batt_a"], 0.0)
        v_batt = max(op["v_batt_v"], 0.0)
        p_batt = max(op["p_batt_w"], 0.0)

        dq = i_batt * dt  # coulombs
        q_remaining = max(0.0, q_remaining - dq)

        dwh = (p_batt * dt) / 3600.0
        total_wh += dwh

        seg_res = {
            "segment": seg.name,
            "duration_s": dt,
            "V_mps": seg.target_airspeed_mps,
            "thrust_required_n": thrust_req,
            **op,
            "wh_used": dwh,
            "soc_est": q_remaining / battery.capacity_coulomb,
        }
        results.append(seg_res)

        feasible_all = feasible_all and (op["feasible"] > 0.5)
        tip_all = tip_all and (op["tip_ok"] > 0.5)
        current_all = current_all and (op["current_ok"] > 0.5)

        if q_remaining <= 1e-6:
            break

    return {
        "prop": prop.name,
        "total_wh": total_wh,
        "soc_end": q_remaining / battery.capacity_coulomb,
        "all_feasible": feasible_all,
        "all_tip_ok": tip_all,
        "all_current_ok": current_all,
        "segments": results,
    }



def print_summary(res: Dict[str, Any]) -> None:
    print(f"\n=== PROP: {res['prop']} ===")
    print(f"Total energy used: {res['total_wh']:.1f} Wh")
    print(f"End SOC (est):     {res['soc_end']*100:.1f}%")
    print(f"Feasible all segs: {res['all_feasible']}")
    print(f"Tip speed OK all:  {res['all_tip_ok']}")
    print(f"Current OK all:    {res['all_current_ok']}")
    print("\nSegments:")
    for s in res["segments"]:
        print(
            f"- {s['segment']}: V={s['V_mps']:.1f} m/s, "
            f"Treq={s['thrust_required_n']:.1f} N, "
            f"T={s['thrust_n']:.1f} N, "
            f"RPM={s['rpm']:.0f}, "
            f"Ibatt={s['i_batt_a']:.1f} A, "
            f"Vbatt={s['v_batt_v']:.1f} V, "
            f"Wh={s['wh_used']:.2f}, "
            f"tip={s['tip_speed_mps']:.0f} m/s, "
            f"{'OK' if s['feasible']>0.5 else 'NOT FEASIBLE'}"
        )



def main():

    # =========================
    # 1) BATTERY
    # =========================
    battery = Battery(
        cells_s=1000,
        capacity_ah=5.0,
        internal_resistance_mohm=30,
        v_cell_nom=3.7
    )

    # =========================
    # 2) MOTOR
    # =========================
    motor = Motor(
        kv_rpm_per_v=1400,
        rm_ohm=0.000000008,
        i0_a=1.2,
        max_current_a=150,
        max_temp_c=130
    )

    # =========================
    # 3) ESC
    # =========================
    esc = ESC(
        max_current_a=150,
        efficiency=0.6,
        has_telemetry=True
    )

    # =========================
    # 4) PROPS TO COMPARE
    # =========================
    props = [
        PropModel(name="10x6", diameter_in=10, pitch_in=6, ct0=0.10, cq0=0.040),
        PropModel(name="11x5.5", diameter_in=11, pitch_in=5.5, ct0=0.105, cq0=0.042),
    ]

    # =========================
    # 5) AIRCRAFT
    # =========================
    aircraft = Aircraft(
        mass_kg=8,
        wing_area_m2=0.42,
        cd0=0.035,
        k=0.075
    )

    # =========================
    # 6) MISSION PROFILE
    # =========================
    mission = [
        Segment("takeoff", duration_s=15,  target_airspeed_mps=12, required_thrust_n=18),
        Segment("climb",   duration_s=120, target_airspeed_mps=18, required_thrust_n=10),
        Segment("cruise",  duration_s=900, target_airspeed_mps=22),
        Segment("loiter",  duration_s=600, target_airspeed_mps=16),
    ]

    # =========================
    # 7) CONSTRAINTS
    # =========================
    constraints = Constraints(
        max_tip_mps=220,
        max_current_a=35,
        max_motor_temp_c=130,
        min_thrust_margin=0.0
    )

    # =========================
    # RUN SIMULATION
    # =========================
    results = []
    for prop in props:
        r = simulate_mission(
            battery=battery,
            motor=motor,
            esc=esc,
            prop=prop,
            aircraft=aircraft,
            mission=mission,
            constraints=constraints
        )
        print_summary(r)
        results.append(r)

    # =========================
    # PICK BEST PROP
    # =========================
    feasible = [
        r for r in results
        if r["all_feasible"] and r["all_tip_ok"] and r["all_current_ok"]
    ]

    if feasible:
        best = min(feasible, key=lambda x: x["total_wh"])
        print(f"\n>>> BEST PROP: {best['prop']} ({best['total_wh']:.1f} Wh)")
    else:
        print("\n>>> No fully feasible solution under constraints")


if __name__ == "__main__":
    main()
