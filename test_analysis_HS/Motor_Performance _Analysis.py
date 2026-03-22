# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

# -*- coding: utf-8 -*-
"""
Motor Performance Analysis and Polynomial Fitting

This script analyzes motor performance data (RPM, Torque, Electrical Power, Efficiency)
loaded from CSV files. It fits a polynomial model for electrical power and
visualizes the results.

Part 1: General Motor Model
Methodology:
1.  Load & Preprocess Data: Read CSVs, average by throttle, clean, preprocess.
2.  Polynomial Regression: Fit P_elec = f(RPM, Torque) using least squares.
3.  Calculate Efficiency: Derive efficiency from the power model.
4.  Error Analysis: Quantify model fit against measured data.
5.  Visualize Results: Plot power and efficiency maps with error overlays.

Part 2: Specific Propeller Model & Validation
Methodology:
1.  Load data for a specific propeller test.
2.  Fit propeller models: Thrust = C_t * omega^2, Torque = C_q * omega^2.
3.  Calculate modelled torque using the propeller model.
4.  Calculate modelled electrical power using the modelled torque and measured RPM
    as input to the general motor model from Part 1.
5.  Compare measured vs. modelled electrical power for this specific test.

"""

# =========================================
# ===          IMPORTS                  ===
# =========================================
import pandas as pd
import numpy as np
import glob
import os
import matplotlib.pyplot as plt

# =========================================
# ===        DATA PROCESSING            ===
# =========================================

def process_motor_data(file_path='.', file_pattern="*.csv"):
    """
    Finds, loads, averages (per throttle), cleans, and pre-processes motor data.

    Args:
        file_path (str): Directory containing CSV files.
        file_pattern (str): Glob pattern to match CSV files.

    Returns:
        tuple: (rpm, torque, efficiency, power) numpy arrays, or (None, None, None, None) on failure.

    Theory Note for Aero Engineers:
        This function handles the essential data preparation steps:
        1. Locating and loading raw test data.
        2. Averaging data points recorded at the same throttle setting within each file.
           This reduces noise and provides a more stable representation for each operating condition.
        3. Combining data from multiple files.
        4. Cleaning: Removing invalid entries (NaNs) and ensuring data types are correct.
        5. Pre-processing: Taking absolute values (check assumption based on motor behavior)
           and clipping efficiency to [0, 100%].
    """
    print("--- Starting Data Processing ---")
    # ----- Step 1: Find Files -----
    search_pattern = os.path.join(file_path, file_pattern)
    csv_files = glob.glob(search_pattern)
    csv_files.sort()

    if not csv_files:
        print(f"Error: No CSV files found matching '{search_pattern}'")
        print(f"Absolute path searched: '{os.path.abspath(file_path)}'")
        return None, None, None, None

    print(f"Found {len(csv_files)} files matching pattern '{file_pattern}'.")
    print("-" * 20)

    all_averaged_data = []
    # Define column names expected in the CSV files
    time_col = 'Time (s)'
    throttle_col = 'Powertrain 1 - ESC throttle (μs)'
    thrust_col = 'Powertrain 1 - force Fz (thrust) (kgf)'
    torque_col = 'Powertrain 1 - torque MZ (torque) (N⋅m)'
    voltage_col = 'Powertrain 1 - voltage (V)'
    current_col = 'Powertrain 1 - current (A)'
    rpm_col = 'Powertrain 1 - rotation speed (rpm)'
    power_col = 'Powertrain 1 - electrical power (W)'
    mech_power_col = 'Powertrain 1 - mechanical power (W)'
    efficiency_col = 'Powertrain 1 - motor & ESC efficiency (%)'
    prop_eff_col = 'Powertrain 1 - propeller efficiency (gf/W)'
    sys_eff_col = 'Powertrain 1 - powertrain efficiency (gf/W)'

    # Columns required for this specific analysis (Part 1)
    required_cols_part1 = [rpm_col, torque_col, efficiency_col, power_col]
    # All numeric columns potentially present that we want to average
    numeric_cols_to_average = [
        thrust_col, torque_col, voltage_col, current_col, rpm_col,
        power_col, mech_power_col, efficiency_col, prop_eff_col, sys_eff_col
    ]

    print("Loading and averaging data per file by throttle value...")
    for f in csv_files:
        try:
            df = pd.read_csv(f)
            file_basename = os.path.basename(f)

            if df.empty:
                print(f"  Skipping empty file: {file_basename}")
                continue

            # Check if required columns exist before proceeding
            # Check for PART 1 columns specifically for the main model build
            if not all(col in df.columns for col in required_cols_part1):
                 print(f"  Warning: Skipping {file_basename} for Part 1 Model. Missing one or more required columns: {required_cols_part1}.")
                 continue # Skip this file for building the general motor model

            # --- Averaging Step ---
            if throttle_col in df.columns:
                # Ensure columns to be averaged are numeric, coercing errors to NaN
                current_numeric_cols = [col for col in numeric_cols_to_average if col in df.columns]
                for col in current_numeric_cols:
                    if not pd.api.types.is_numeric_dtype(df[col]):
                        df[col] = pd.to_numeric(df[col], errors='coerce')

                # Drop rows where essential numeric columns (for Part 1) became NaN BEFORE averaging
                df.dropna(subset=[col for col in required_cols_part1 if col in df.columns], inplace=True)

                if df.empty:
                    print(f"  Skipping {file_basename} after dropping NaNs in required columns.")
                    continue

                # Handle throttle column conversion and NaN drop AFTER checking essential columns
                if df[throttle_col].isnull().all():
                    print(f"  Warning: Throttle column '{throttle_col}' is all NaN in {file_basename}. Cannot average by throttle.")
                    # Decide: skip file or process without averaging? Here we skip.
                    continue
                else:
                    df[throttle_col] = pd.to_numeric(df[throttle_col], errors='coerce')
                    df.dropna(subset=[throttle_col], inplace=True)

                if df.empty:
                    print(f"  Skipping {file_basename} after dropping NaNs in throttle column.")
                    continue

                # Group by throttle and average only numeric columns present
                cols_to_avg_present = [c for c in current_numeric_cols if pd.api.types.is_numeric_dtype(df[c])]
                try:
                    df_averaged = df.groupby(throttle_col, as_index=False)[cols_to_avg_present].mean()
                    df_averaged['source_file'] = file_basename
                    all_averaged_data.append(df_averaged)
                    # print(f"  Successfully averaged data for {file_basename} by throttle.") # Optional: Verbose
                except Exception as avg_err:
                     print(f"  Error during averaging for {file_basename}: {avg_err}")

            else:
                print(f"  Warning: Throttle column '{throttle_col}' not found in {file_basename}. Skipping averaging for this file.")

        except pd.errors.EmptyDataError:
             print(f"Warning: Skipping empty file {os.path.basename(f)}")
        except Exception as e:
            print(f"Error loading/processing file {os.path.basename(f)}: {e}")

    if not all_averaged_data:
        print("\nError: No data loaded/averaged successfully for Part 1 Model.")
        return None, None, None, None

    combined_df = pd.concat(all_averaged_data, ignore_index=True)
    print("-" * 20)
    print(f"Combined data (averaged by throttle) has {len(combined_df)} rows.")

    # ----- Step 3: Prepare Combined Data for Part 1 Model -----
    missing_cols = [col for col in required_cols_part1 if col not in combined_df.columns]
    if missing_cols:
         print(f"\nError: Required columns missing after combining data for Part 1: {missing_cols}")
         return None, None, None, None

    # --- Data Cleaning on Combined Data ---
    for col in required_cols_part1:
         if not pd.api.types.is_numeric_dtype(combined_df[col]):
              combined_df[col] = pd.to_numeric(combined_df[col], errors='coerce')

    original_rows = len(combined_df)
    combined_df_clean = combined_df.dropna(subset=required_cols_part1).copy()
    rows_after_na = len(combined_df_clean)
    if original_rows > rows_after_na:
        print(f"Removed {original_rows - rows_after_na} rows with NaNs in essential columns: {required_cols_part1}.")
    print(f"Data remaining for Part 1 analysis: {rows_after_na} rows.")

    if rows_after_na < 3: # Need at least 3 points for fitting
         print("Error: Not enough valid data points (< 3) remain after cleaning for Part 1.")
         return None, None, None, None

    # --- Pre-processing: Extract, Absolute Values, Clip ---
    rpm = combined_df_clean[rpm_col].values
    torque = combined_df_clean[torque_col].values
    efficiency = combined_df_clean[efficiency_col].values
    power = combined_df_clean[power_col].values

    # Apply absolute value (check theory note above)
    # Assuming Torque should always be positive for propeller load
    # Assuming Power (electrical input) should always be positive
    # Efficiency can be negative if braking, but clipping to 0-100 is common for performance maps
    torque = np.abs(torque)
    efficiency = np.abs(efficiency)
    power = np.abs(power)
    print(f"Applied np.abs() to '{torque_col}', '{efficiency_col}', and '{power_col}'.")

    # Clip efficiency
    efficiency = np.clip(efficiency, 0, 100)
    print(f"Clipped '{efficiency_col}' to range [0, 100].")

    # Final check for sufficient points after potential NaN introduction by abs/clip (unlikely here)
    valid_indices = ~np.isnan(rpm) & ~np.isnan(torque) & ~np.isnan(efficiency) & ~np.isnan(power)
    rpm = rpm[valid_indices]
    torque = torque[valid_indices]
    efficiency = efficiency[valid_indices]
    power = power[valid_indices]

    if len(rpm) < 3:
        print("Error: Not enough valid numeric points (< 3) after pre-processing for Part 1.")
        return None, None, None, None

    print(f"\nFinal data ranges used for Part 1 Model:")
    print(f"  RPM:        {rpm.min():.1f} to {rpm.max():.1f}")
    print(f"  Torque:     {torque.min():.3f} to {torque.max():.3f} N·m")
    print(f"  Efficiency: {efficiency.min():.1f}% to {efficiency.max():.1f}%")
    print(f"  Power:      {power.min():.1f} W to {power.max():.1f} W")
    print("--- Data Processing Finished ---")

    return rpm, torque, efficiency, power


# =========================================
# ===      POLYNOMIAL FIT HELPERS       ===
# =========================================

def build_design_matrix(rpm, torque):
    """
    Constructs the design matrix 'A' for a 3rd order polynomial fit.
    Model: P_elec ≈ A @ coeffs

    Args:
        rpm (np.ndarray): Array of RPM values.
        torque (np.ndarray): Array of Torque values.

    Returns:
        np.ndarray: The design matrix A.

    Theory Note:
        This matrix holds the basis functions (1, rpm, T, rpm^2, ...) evaluated
        at each data point. Solving P_elec = A @ coeffs via least squares finds
        the coefficients that best fit the data surface.
    """
    rpm_flat = rpm.ravel()
    torque_flat = torque.ravel()
    return np.column_stack([
        np.ones_like(rpm_flat),      # c0 (intercept)
        rpm_flat,                    # c1 * rpm
        torque_flat,                 # c2 * torque
        rpm_flat**2,                 # c3 * rpm^2
        rpm_flat * torque_flat,      # c4 * rpm * torque
        torque_flat**2,              # c5 * torque^2
        rpm_flat**3,                 # c6 * rpm^3
        rpm_flat**2 * torque_flat,   # c7 * rpm^2 * torque
        rpm_flat * torque_flat**2,   # c8 * rpm * torque^2
        torque_flat**3               # c9 * torque^3
    ])

# =========================================
# ===         PLOTTING FUNCTION         ===
# =========================================

def plot_motor_performance(rpm_grid, tor_grid, value_grid, value_label, levels, cmap,
                           rpm_pts, tor_pts, error_pts, error_label, error_cmap,
                           title):
    """
    Generates a contour plot of predicted values with scatter points colored by error.
    (Hull plotting removed from this version).

    Args:
        rpm_grid, tor_grid: Meshgrid arrays for RPM and Torque.
        value_grid: 2D array of predicted values (e.g., Power, Efficiency).
        value_label: Label for the contour colorbar.
        levels: Number of contour levels or specific level values.
        cmap: Colormap for the contour plot.
        rpm_pts, tor_pts: 1D arrays of measured RPM and Torque points.
        error_pts: 1D array of errors at the measured points.
        error_label: Label for the scatter point colorbar.
        error_cmap: Colormap for the scatter points.
        title: Title for the plot.

    Theory Note for Aero Engineers:
        Visualizes:
        - Contour Plot: Predicted performance map from the model.
        - Scatter Plot: Original measured data points, colored by model error
          (prediction vs. measurement). Helps assess fit quality visually.
    """
    plt.figure(figsize=(10, 8))

    # --- Contour Plot (Predicted Surface) ---
    cp = plt.contourf(rpm_grid, tor_grid, value_grid, levels=levels, cmap=cmap, extend='both')
    plt.colorbar(cp, label=value_label)

    # --- Scatter Plot (Measured Points colored by Error) ---
    if rpm_pts is not None and tor_pts is not None and error_pts is not None and len(rpm_pts) > 0:
        # Determine symmetric color limits for error map centered at 0
        valid_errors = error_pts[~np.isnan(error_pts)]
        if len(valid_errors) > 0:
            error_max_abs = np.nanmax(np.abs(valid_errors))
            if error_max_abs < 1e-9: error_max_abs = 1.0 # Avoid zero range
            vmin, vmax = -error_max_abs, error_max_abs
        else:
            vmin, vmax = -1, 1 # Default if no valid error points

        sc = plt.scatter(rpm_pts, tor_pts, c=error_pts, cmap=error_cmap,
                         vmin=vmin, vmax=vmax,
                         edgecolor='k', marker='o', s=50, label=f'Measured Points (N={len(rpm_pts)})')
        plt.colorbar(sc, label=error_label)
        plt.legend() # Show legend for scatter points

    # --- Hull Plotting Removed ---

    # --- Labels and Formatting ---
    plt.xlabel('RPM')
    plt.ylabel('Torque (N·m)')
    plt.title(title)
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.tight_layout()
    # --- Save the figure as PDF ---
    plt.savefig(f"{title.replace(' ', '_')}.pdf", format='pdf')
    # --- Show the plot ---
    plt.show()

def model_prop(FILE_PATH,PROPELLER_TEST_FILE,motor_coeffs):
    prop_file_path = os.path.join(FILE_PATH, PROPELLER_TEST_FILE)

    # Define required columns for Part 2 analysis
    rpm_col = 'Powertrain 1 - rotation speed (rpm)'
    torque_col = 'Powertrain 1 - torque MZ (torque) (N⋅m)'
    thrust_col = 'Powertrain 1 - force Fz (thrust) (N)'
    power_col = 'Powertrain 1 - electrical power (W)'
    throttle_col = 'Powertrain 1 - ESC throttle (μs)' # Needed for averaging this specific test

    required_cols_part2 = [rpm_col, torque_col, thrust_col, power_col, throttle_col]


    # # Check if motor model from Part 1 exists
    # if motor_coeffs is None:
    #     print("\nError: Motor coefficients from Part 1 not available. Cannot proceed with Part 2.")
    #     exit()

    # ----- Step 1: Load and Process Specific Propeller Data -----
    print(f"\n--- 1. Loading and Processing Propeller Data ({PROPELLER_TEST_FILE}) ---")
    if not os.path.exists(prop_file_path):
        print(f"Error: Propeller test file not found at '{prop_file_path}'")
        print(f"Absolute path checked: '{os.path.abspath(prop_file_path)}'")
        # exit()

    try:
        df_prop = pd.read_csv(prop_file_path)


        if df_prop.empty:
              print(f"Error: Propeller test file '{PROPELLER_TEST_FILE}' is empty.")
              exit()

        # Check required columns
        if not all(col in df_prop.columns for col in required_cols_part2):
            missing = [col for col in required_cols_part2 if col not in df_prop.columns]
            print(f"Error: Propeller test file '{PROPELLER_TEST_FILE}' is missing required columns: {missing}")
            # exit()

        # Ensure numeric types and handle potential errors
        for col in required_cols_part2:
            if not pd.api.types.is_numeric_dtype(df_prop[col]):
                  df_prop[col] = pd.to_numeric(df_prop[col], errors='coerce')

        # Drop rows with NaNs in essential columns for propeller modeling
        df_prop.dropna(subset=required_cols_part2, inplace=True)

        if len(df_prop) < 2:
              print(f"Error: Not enough valid data points (< 2) in '{PROPELLER_TEST_FILE}' after cleaning.")
              exit()

        # Average the propeller data by throttle setting for cleaner analysis
        numeric_cols_prop = [rpm_col, torque_col, thrust_col, power_col] # Columns to average
        df_prop_avg = df_prop.groupby(throttle_col, as_index=False)[numeric_cols_prop].mean()

        if len(df_prop_avg) < 2:
              print(f"Error: Not enough distinct throttle points (< 2) found in '{PROPELLER_TEST_FILE}' for averaging.")
              exit()

        print(f"Loaded and averaged {len(df_prop_avg)} data points for '{PROPELLER_TEST_FILE}'.")

        # Extract data for modeling
        rpm_prop_meas = df_prop_avg[rpm_col].values
        torque_prop_meas = np.abs(df_prop_avg[torque_col].values) # Use absolute torque
        thrust_prop_meas_kgf = df_prop_avg[thrust_col].values
        power_prop_meas = np.abs(df_prop_avg[power_col].values) # Use absolute power

        # Convert RPM to rad/s (omega)
        omega_prop_meas = rpm_prop_meas * (2 * np.pi / 60)
        # Convert Thrust from kgf to Newtons (approx g = 9.80665)
        thrust_prop_meas_N = thrust_prop_meas_kgf * 9.80665

        # Remove zero/low omega points to avoid issues with fitting C*omega^2 model
        valid_prop_indices = omega_prop_meas > 10 # Threshold rad/s (adjust if needed)
        if not np.any(valid_prop_indices):
              print("Error: No valid data points with omega > 10 rad/s found for propeller fitting.")
              exit()
        omega_prop_meas = omega_prop_meas[valid_prop_indices]
        rpm_prop_meas = rpm_prop_meas[valid_prop_indices]
        torque_prop_meas = torque_prop_meas[valid_prop_indices]
        thrust_prop_meas_N = thrust_prop_meas_N[valid_prop_indices]
        power_prop_meas = power_prop_meas[valid_prop_indices]

        if len("omega_prop_meas:", omega_prop_meas) < 2:
              print("Error: Not enough valid data points (< 2) remain after filtering low omega values.")
              exit()

        print(f"Using {len(omega_prop_meas)} points for propeller coefficient fitting.")

    except Exception as e:
        print(f"Error processing propeller file '{PROPELLER_TEST_FILE}': {e}")
        # exit()

    # ----- Step 2: Fit Propeller Models (Thrust = Ct*omega^2, Torque = Cq*omega^2) -----
    print("\n--- 2. Fitting Propeller Coefficients (Ct, Cq) ---")

    # Design matrix for C*omega^2 model is just omega^2
    A_prop_fit = (omega_prop_meas**2).reshape(-1, 1) # Needs to be a column vector

    # Fit C_thrust (Ct)
    try:
        Ct_coeffs, _, _, _ = np.linalg.lstsq(A_prop_fit, thrust_prop_meas_N, rcond=None)
        C_thrust = Ct_coeffs[0]
        print(f"  Fitted Thrust Coefficient (Ct): {C_thrust:.6e} N/(rad/s)^2")
    except np.linalg.LinAlgError as e:
        print(f"  Error fitting Thrust Coefficient: {e}")
        C_thrust = np.nan

    # Fit C_torque (Cq)
    try:
        Cq_coeffs, _, _, _ = np.linalg.lstsq(A_prop_fit, torque_prop_meas, rcond=None)
        C_torque = Cq_coeffs[0]
        print(f"  Fitted Torque Coefficient (Cq): {C_torque:.6e} N·m/(rad/s)^2")
    except np.linalg.LinAlgError as e:
        print(f"  Error fitting Torque Coefficient: {e}")
        C_torque = np.nan

    if np.isnan(C_torque):
        print("\nError: Failed to fit C_torque. Cannot proceed with power modeling.")
        exit()

    # ----- Step 3: Calculate Modelled Torque for the Test -----
    print("\n--- 3. Calculating Modelled Torque using Propeller Model ---")
    torque_prop_modelled = C_torque * (omega_prop_meas**2)

    # ----- Step 4: Calculate Modelled Electrical Power using Motor Model -----
    print("\n--- 4. Calculating Modelled Electrical Power using Motor Model ---")
    # Use the measured RPM and the *modelled* torque as input to the motor power model
    A_prop_power_model = build_design_matrix(rpm_prop_meas, torque_prop_modelled)
    power_prop_modelled = A_prop_power_model.dot(motor_coeffs)

    # ----- Step 5: Compare Measured vs Modelled Power -----
    print("\n--- 5. Comparing Measured vs Modelled Electrical Power ---")

    # Calculate error
    power_prop_error = power_prop_modelled - power_prop_meas
    mae_prop_power = np.mean(np.abs(power_prop_error))
    rmse_prop_power = np.sqrt(np.mean(power_prop_error**2))
    print(f"  Comparison on '{PROPELLER_TEST_FILE}' data:")
    print(f"    Mean Absolute Error: {mae_prop_power:.2f} W")
    print(f"    RMSE: {rmse_prop_power:.2f} W")

    # Create plot
    plt.figure(figsize=(10, 6))
    # Sort values by RPM for cleaner line plotting
    sort_indices = np.argsort(rpm_prop_meas)
    rpm_sorted = rpm_prop_meas[sort_indices]
    power_meas_sorted = power_prop_meas[sort_indices]
    power_modelled_sorted = power_prop_modelled[sort_indices]

    plt.plot(rpm_sorted, power_meas_sorted, 'bo-', label='Measured Electrical Power', markersize=5)
    plt.plot(rpm_sorted, power_modelled_sorted, 'rx--', label='Modelled Electrical Power (Motor Model + Prop Model Torque)', markersize=5)

    plt.xlabel("RPM")
    plt.ylabel("Electrical Power (W)")
    plt.title(f"Measured vs Modelled Electrical Power for {PROPELLER_TEST_FILE}\n(Motor Model + Propeller Cq={C_torque:.3e})")
    plt.legend()
    plt.grid(True, linestyle=':', alpha=0.7)
    plt.tight_layout()
    # Save to PDF
    plt.savefig(f"power_comparison_{PROPELLER_TEST_FILE.replace(' ', '_')}.pdf", format='pdf')
    plt.show()


    print("\n--- Analysis Complete (Parts 1 & 2) ---")
    print("="*40)

# =========================================
# ===          MAIN EXECUTION           ===
# =========================================

if __name__ == '__main__':

    print("Starting Motor Performance Analysis Script")
    print("="*40)

    # *****************************************
    # ********** PART 1: MOTOR MODEL ********
    # *****************************************
    print("\n======= PART 1: General Motor Polynomial Model =======")

    # ----- Step 0: Configuration -----
    FILE_PATH = './Results_TYTO/'
    FILE_PATTERN = 'throttle_Speed_th1200.csv' # Pattern to find *all* motor test files for the general model

    GRID_RESOLUTION = 100    # Resolution of the prediction grid
    BUFFER_PCT = 0.02        # Extend prediction grid slightly beyond data range

    print("\n--- Configuration (Part 1) ---")
    print(f"Data Directory (FILE_PATH): {os.path.abspath(FILE_PATH)}")
    print(f"File Pattern (FILE_PATTERN): {FILE_PATTERN}")
    print(f"Grid Resolution: {GRID_RESOLUTION}")
    print(f"Grid Buffer: {BUFFER_PCT*100:.1f}%")

    # ----- Step 1: Load and Process Data -----
    print("\n--- 1. Loading and Processing Data (Part 1) ---")
    rpm, torque, efficiency_meas_pct, power_meas = process_motor_data(
        file_path=FILE_PATH,
        file_pattern=FILE_PATTERN
    )

    # Global variable to store coefficients for Part 2
    motor_coeffs = None

    # Exit if data loading failed
    if rpm is None:
        print("\nError: Data loading failed for Part 1. Exiting.")
        exit()
    elif len(rpm) < 10: # Increased minimum points for a 10-coefficient polynomial
        print(f"\nError: Only {len(rpm)} valid data points found for Part 1. Need at least 10 for a reliable 3rd order fit. Exiting.")
        # exit()
    else:
        print(f"\nSuccessfully loaded and processed {len(rpm)} data points for Part 1 Model.")
        # Convert measured efficiency from % to fraction for calculations
        efficiency_meas_frac = efficiency_meas_pct / 100.0

        # ----- Step 2: Polynomial Regression Fit -----
        print("\n--- 2. Performing Polynomial Fit (Part 1) ---")
        # Model: power_meas ≈ A @ coeffs
        A = build_design_matrix(rpm, torque)

        # Solve using Linear Least Squares
        coeffs, residuals, rank, s = np.linalg.lstsq(A, power_meas, rcond=None)
        motor_coeffs = coeffs # Store coefficients for Part 2

        print(f"Fit completed. Rank of design matrix: {rank}")
        if rank < A.shape[1]:
              print(f"Warning: Design matrix is rank deficient (Rank {rank} < {A.shape[1]} columns). Fit might be unreliable.")
        # Optional: print coefficients if needed
        # print("Coefficients (c0 to c9):\n", motor_coeffs)

        # ----- Step 3: Point-wise Predictions and Error Analysis -----
        print("\n--- 3. Calculating Point-wise Predictions and Errors (Part 1) ---")
        mech_power_pts = torque * rpm * (2 * np.pi / 60)  # Mechanical power (W)
        power_pred_pts = A.dot(motor_coeffs)                   # Predicted electrical power (W)

        # Calculate predicted efficiency, avoiding division by zero
        power_pred_pts_safe = np.where(np.abs(power_pred_pts) > 1e-6, power_pred_pts, np.nan)
        eff_pred_pts_frac = np.divide(mech_power_pts, power_pred_pts_safe,
                                      out=np.full_like(mech_power_pts, np.nan),
                                      where=~np.isnan(power_pred_pts_safe)) # Predicted efficiency (fraction)

        # Calculate errors
        power_err_abs = power_pred_pts - power_meas             # Watts
        eff_err_pct = (eff_pred_pts_frac - efficiency_meas_frac) * 100 # Percentage Points (pp)

        # --- Error Statistics ---
        valid_power_err_mask = ~np.isnan(power_err_abs)
        valid_eff_err_mask = ~np.isnan(eff_err_pct)

        print("\nError Statistics (Predicted vs. Measured on ALL Part 1 data):")
        if np.any(valid_power_err_mask):
            mean_power_err = np.mean(np.abs(power_err_abs[valid_power_err_mask]))
            max_power_err = np.max(np.abs(power_err_abs[valid_power_err_mask]))
            rmse_power_err = np.sqrt(np.mean(power_err_abs[valid_power_err_mask]**2))
            print(f"  Power Fit Error      — Mean Abs: {mean_power_err:.2f} W, Max Abs: {max_power_err:.2f} W, RMSE: {rmse_power_err:.2f} W")
        else:
            print("  Power Fit Error      — Could not calculate (all NaNs?).")

        if np.any(valid_eff_err_mask):
            # Clip predicted efficiency before error calculation for meaningful stats if desired
            eff_pred_pts_frac_clipped = np.clip(eff_pred_pts_frac, 0, 1)
            eff_err_pct_clipped = (eff_pred_pts_frac_clipped - efficiency_meas_frac) * 100
            valid_eff_err_mask_clipped = ~np.isnan(eff_err_pct_clipped)

            if np.any(valid_eff_err_mask_clipped):
                  mean_eff_err = np.mean(np.abs(eff_err_pct_clipped[valid_eff_err_mask_clipped]))
                  max_eff_err = np.max(np.abs(eff_err_pct_clipped[valid_eff_err_mask_clipped]))
                  rmse_eff_err = np.sqrt(np.mean(eff_err_pct_clipped[valid_eff_err_mask_clipped]**2))
                  print(f"  Efficiency Fit Error — Mean Abs: {mean_eff_err:.2f} pp, Max Abs: {max_eff_err:.2f} pp, RMSE: {rmse_eff_err:.2f} pp")
            else:
                  print("  Efficiency Fit Error — Could not calculate (all NaNs?).")
        else:
            print("  Efficiency Fit Error — Could not calculate (all NaNs?).")


        # ----- Step 4: Create Prediction Grid -----
        print("\n--- 4. Creating Prediction Grid for Visualization (Part 1) ---")
        rpm_min, rpm_max = rpm.min(), rpm.max()
        torque_min, torque_max = torque.min(), torque.max()
        # Avoid zero range if data is flat
        rpm_range = rpm_max - rpm_min if rpm_max > rpm_min else 1.0
        torque_range = torque_max - torque_min if torque_max > torque_min else 0.1

        # Define grid limits with buffer
        rpm_lin = np.linspace(rpm_min - rpm_range * BUFFER_PCT,
                              rpm_max + rpm_range * BUFFER_PCT,
                              GRID_RESOLUTION)
        torque_lin = np.linspace(max(0, torque_min - torque_range * BUFFER_PCT), # Ensure torque grid >= 0
                                  torque_max + torque_range * BUFFER_PCT,
                                  GRID_RESOLUTION)
        RPM_grid, TOR_grid = np.meshgrid(rpm_lin, torque_lin)

        # Calculate predictions on the grid
        A_grid = build_design_matrix(RPM_grid, TOR_grid)
        power_pred_grid = A_grid.dot(motor_coeffs).reshape(RPM_grid.shape)

        mech_power_grid = TOR_grid * RPM_grid * (2 * np.pi / 60)
        # Use absolute value for predicted power denominator for safety, clip efficiency later
        power_pred_grid_safe = np.where(np.abs(power_pred_grid) > 1e-6, power_pred_grid, np.nan)
        eff_pred_grid_frac = np.divide(mech_power_grid, power_pred_grid_safe,
                                        out=np.full_like(mech_power_grid, np.nan),
                                        where=~np.isnan(power_pred_grid_safe))

        # Clip efficiency grid to physically meaningful range 0-100%
        eff_pred_grid_pct = np.clip(eff_pred_grid_frac * 100, 0, 100)

        print("Prediction grid generated.")

        # ----- Step 5: Visualization -----
        print("\n--- 5. Generating Plots (Part 1) ---")

        # --- Create Power Plot ---
        plot_motor_performance(
            rpm_grid=RPM_grid, tor_grid=TOR_grid,
            value_grid=power_pred_grid, value_label='Predicted Electrical Power (W)',
            levels=20, cmap='viridis',  # Adjust levels/cmap as needed
            rpm_pts=rpm, tor_pts=torque,
            error_pts=power_err_abs, error_label='Power Error (Pred - Meas) (W)', error_cmap='coolwarm',
            title='Motor Electrical Power Map (Polynomial Fit) - All Data'
        )

        # --- Create Efficiency Plot ---
        eff_levels = np.arange(50, 90, 2.5) # Contours every 2.5% from 50 to 100

        plot_motor_performance(
            rpm_grid=RPM_grid, tor_grid=TOR_grid,
            value_grid=eff_pred_grid_pct, value_label='Predicted Efficiency (%)',
            levels=eff_levels, cmap='viridis', # Use viridis for efficiency
            rpm_pts=rpm, tor_pts=torque,
            error_pts=eff_err_pct, error_label='Efficiency Error (Pred - Meas) (pp)', error_cmap='coolwarm',
            title='Motor Efficiency Map (Derived from Power Fit) - All Data'
        )
        
        # *******************************************************
    # ********** PART 2: PROPELLER MODEL & VALIDATION *******
    # *******************************************************
    print("\n\n======= PART 2: Specific Propeller Model & Validation =======")
    
    
    
    
    
    # ----- Configuration for Part 2 -----
    FILE_PATH = './Results_TYTO/'
    FILE_PATTERN = 'throttle_Speed_th1200.csv'
    model_prop(FILE_PATH,FILE_PATTERN,motor_coeffs)
    # model_prop('22inch-Xoar 28-04.csv')