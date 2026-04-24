#!/usr/bin/env python3
"""
LTSpice_full_pipeline.py

Complete pipeline:
 - Parallel LTspice runs (concurrent.futures)
 - Thread/process-safe parsing (each worker uses unique filenames)
 - Automatic netlist generation supporting AC / TRAN / OP
 - CSV + optional NumPy (.npz) export
 - Ctrl+C safe (partial results saved)
 - Cleanup of all LTspice artifacts (op.raw, *.raw, *.log, *.cir, *.cir~)
 - Robust error reporting (captures LTspice stdout/stderr)

Requirements:
 - Python 3.8+
 - ltspice Python package (pip install ltspice)
 - pandas, numpy
 - LTspice installed and LTSPICE_EXE path set below
"""

import concurrent.futures
import subprocess
import ltspice
import pandas as pd
import numpy as np
import os
import time
import uuid
import signal
from typing import Tuple, List, Dict, Optional

# -------------------------
# USER CONFIGURATION
# -------------------------

# Path to LTspice executable on your machine
LTSPICE_EXE = r"C:/Program Files/ADI/LTspice/LTspice.exe"

# Template mode:
# "AC"  -> frequency response (.ac)
# "TRAN"-> transient (.tran)
# "OP"  -> operating point (.op)
ANALYSIS_TYPE = "AC"

# Number of parallel workers (set to cpu_count or less)
N_WORKERS = max(1, os.cpu_count() - 1)

# How many simulations to run (you can generate parameter combinations below)
N_SIMULATIONS = 100  # set to 1000 for full generation

# Output filenames
OUTPUT_CSV = "spice_dataset.csv"
OUTPUT_NUMPY = "spice_dataset.npz"   # optional; saved if SAVE_NUMPY True
SAVE_NUMPY = True

# Timeout for a single simulation raw file creation (seconds)
RAW_TIMEOUT_SEC = 10.0

# AC or TRAN simulation parameters (default content for netlist generation)
AC_DEC = 50
AC_START = 1
AC_STOP = 100000
TRAN_STEP = "1u"      # timestep string for transient (e.g. '1u')
TRAN_STOP = "10m"     # stop time string (e.g. '10m')

# LTspice command-line flags:
# -Run : run
# -b   : batch (no GUI)
LTSPICE_FLAGS = ["-Run", "-b"]

# -------------------------
# Parameter generation (customize ranges or sampling method)
# -------------------------
# Example: uniformly sample R in [100, 10k], C in [1e-7, 1e-4], VDC in [1, 12]
# We create N_SIMULATIONS random parameter sets. Replace with grid or .step as desired.

def generate_parameters(n_samples: int) -> List[Tuple[float, float, float]]:
    rng = np.random.default_rng(seed=42)
    R_vals = rng.uniform(100.0, 10000.0, size=n_samples)      # ohms
    C_vals = rng.uniform(1e-7, 1e-4, size=n_samples)          # Farads
    V_vals = rng.uniform(1.0, 12.0, size=n_samples)           # Volts
    return list(zip(R_vals, C_vals, V_vals))

# -------------------------
# HELPERS: cleanup and safe file utilities
# -------------------------
def cleanup_sim_files(prefix: str) -> None:
    """
    Remove LTspice artifacts for files that start with prefix (temp_sim unique id).
    Also attempt to remove common global artifacts like op.raw.
    """
    for filename in os.listdir("."):
        # Remove files that start with our prefix and have typical extensions
        if filename.startswith(prefix) and (filename.endswith(".raw") or filename.endswith(".log") or filename.endswith(".cir") or filename.endswith(".cir~")):
            try:
                os.remove(filename)
            except Exception:
                pass
    # Remove op.raw if present (annoying global file)
    if os.path.exists("op.raw"):
        try:
            os.remove("op.raw")
        except Exception:
            pass

def wait_for_file(path: str, timeout: float) -> bool:
    """Wait up to timeout seconds for path to appear. Return True if exists."""
    start = time.time()
    while (time.time() - start) < timeout:
        if os.path.exists(path):
            return True
        time.sleep(0.05)
    return False

# -------------------------
# WORKER: generates netlist, runs LTspice, parses results, cleans up
# -------------------------
def worker_run_sim(sim_id: str, R: float, C: float, VDC: float, analysis_type: str) -> List[Dict]:
    """
    Run a single LTspice simulation in a worker process.
    Returns a list of rows (dictionaries) to append to the dataset.
    If simulation fails, return empty list.
    """
    # Use a unique prefix per simulation to avoid clashes
    prefix = f"sim_{sim_id}"
    sim_file = f"{prefix}.cir"
    raw_file = f"{prefix}.raw"
    log_file = f"{prefix}.log"

    # Ensure no leftover files from earlier runs with same prefix
    cleanup_sim_files(prefix)

    # Build netlist content (automatic netlist generation)
    # Node naming: V1 in 0 DC {VDC}; R1 in out {R}; C1 out 0 {C} -> probe V(out)
    netlist_lines = [
        f"* Auto-generated netlist - sim {sim_id}",
        ".options nopage",
        f"V1 in 0 DC {VDC}",
        f"R1 in out {R}",
        f"C1 out 0 {C}"
    ]

    # Add analysis block
    if analysis_type.upper() == "AC":
        netlist_lines.append(f".ac dec {AC_DEC} {AC_START} {AC_STOP}")
        # Tell LTspice to save V(out)
        netlist_lines.append(".save V(out)")
    elif analysis_type.upper() == "TRAN":
        netlist_lines.append(f".tran {TRAN_STEP} {TRAN_STOP}")
        netlist_lines.append(".save V(out)")
    else:  # OP
        netlist_lines.append(".op")
        netlist_lines.append(".save V(out)")

    netlist_lines.append(".end")

    # Write netlist file
    with open(sim_file, "w") as nf:
        nf.write("\n".join(netlist_lines))

    # Build LTspice command; ensure we pass sim_file directly
    cmd = [LTSPICE_EXE] + LTSPICE_FLAGS + [sim_file]

    # Run LTspice (capture output; don't raise CalledProcessError so we can handle gracefully)
    try:
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
    except FileNotFoundError as e:
        # LTspice executable not found
        print(f"[{sim_id}] LTspice executable not found at: {LTSPICE_EXE}")
        cleanup_sim_files(prefix)
        return []

    # If LTspice returned non-zero, capture log / stderr for debugging and return empty result
    if proc.returncode != 0:
        print(f"[{sim_id}] LTspice exited with code {proc.returncode}")
        if proc.stderr:
            print(f"[{sim_id}] STDERR:\n{proc.stderr.strip()}")
        # print log file if exists
        if os.path.exists(log_file):
            try:
                with open(log_file, "r") as lf:
                    print(f"[{sim_id}] LTspice LOG:\n{lf.read()}")
            except Exception:
                pass
        cleanup_sim_files(prefix)
        return []

    # Wait for the raw file to appear (with timeout)
    if not wait_for_file(raw_file, RAW_TIMEOUT_SEC):
        print(f"[{sim_id}] RAW file '{raw_file}' did not appear within timeout ({RAW_TIMEOUT_SEC}s).")
        cleanup_sim_files(prefix)
        return []

    # Parse raw file using ltspice package
    try:
        lt = ltspice.Ltspice(raw_file)
        lt.parse()  # parse the raw file
    except Exception as e:
        print(f"[{sim_id}] Failed to parse RAW file: {e}")
        cleanup_sim_files(prefix)
        return []

    rows = []
    try:
        # For AC: use get_frequency(); for TRAN: get_time(); for OP: parse DC value into one row
        if analysis_type.upper() == "AC":
            try:
                x_axis = lt.get_frequency()
            except Exception:
                print(f"[{sim_id}] No frequency axis in RAW (not an AC simulation).")
                x_axis = np.array([])

        # FIX: array-safe check
        if x_axis is not None and len(x_axis) > 0:
            y_data = lt.get_data("V(out)")
        else:
            y_data = np.array([])

        if len(x_axis) != len(y_data):
            print(f"[{sim_id}] Length mismatch: freq={len(x_axis)}, vout={len(y_data)}")
            return []

            for x, y in zip(x_axis, y_data):
                rows.append({
                    "SimID": sim_id,
                    "R": R,
                    "C": C,
                    "VDC": VDC,
                    "x": float(x),
                    "Vout": float(abs(y))
                })


        elif analysis_type.upper() == "TRAN":
            # get_time() and V(out) arrays
            try:
                x_axis = lt.get_time()
            except Exception:
                print(f"[{sim_id}] No time axis in RAW (not a TRAN simulation).")
                x_axis = []
            y_data = lt.get_data("V(out)") if x_axis else []
            for x, y in zip(x_axis, y_data):
                rows.append({
                    "SimID": sim_id,
                    "R": R,
                    "C": C,
                    "VDC": VDC,
                    "x": float(x),       # time (s)
                    "Vout": float(y)
                })

        else:  # OP
            # For operating point, attempt to get the DC node value
            # ltspice raw for OP may not provide get_data in same way; try reading node directly
            try:
                y = lt.get_data("V(out)")
                # If get_data returns array-like, use first element
                val = float(y[0]) if hasattr(y, "__len__") else float(y)
            except Exception:
                # fallback: attempt to parse .log
                val = None
                if os.path.exists(log_file):
                    with open(log_file, "r") as lf:
                        lines = lf.readlines()
                    # simple heuristic to find "v(out)" or similar
                    for line in lines:
                        if "v(out)" in line.lower() or "v(out)" in line:
                            try:
                                val = float(line.split()[-1])
                                break
                            except Exception:
                                pass
            rows.append({
                "SimID": sim_id,
                "R": R,
                "C": C,
                "VDC": VDC,
                "x": 0.0,
                "Vout": float(val) if val is not None else np.nan
            })

    except Exception as e:
        print(f"[{sim_id}] Error while extracting data from RAW: {e}")
        rows = []

    finally:
        # Always cleanup temporary files created by this simulation
        cleanup_sim_files(prefix)

    return rows

# -------------------------
# MAIN: runs parameter generation, parallel execution, aggregation, saving
# -------------------------
def main():
    print("LTSpice full pipeline starting...")
    print(f"LTSpice exe: {LTSPICE_EXE}")
    print(f"Analysis type: {ANALYSIS_TYPE}")
    print(f"Parallel workers: {N_WORKERS}")
    print(f"Simulations to schedule: {N_SIMULATIONS}")
    print("Press CTRL+C to cancel and save partial results.\n")

    # Generate parameter list
    param_triplets = generate_parameters(N_SIMULATIONS)

    # Convert to a list of (sim_id, R, C, VDC)
    tasks = []
    for i, (R, C, V) in enumerate(param_triplets):
        # Use a short unique id (UUID4 truncated) so filenames are unique across workers
        uid = uuid.uuid4().hex[:8]
        sim_id = f"{i}_{uid}"
        tasks.append((sim_id, float(R), float(C), float(V)))

    dataset_rows = []

    # Use ProcessPoolExecutor to run workers in parallel
    # We will submit all tasks, then iterate as they complete. On KeyboardInterrupt we attempt to cancel remaining futures.
    with concurrent.futures.ProcessPoolExecutor(max_workers=N_WORKERS) as executor:
        future_to_task = {
            executor.submit(worker_run_sim, sim_id, R, C, V, ANALYSIS_TYPE): (sim_id, R, C, V)
            for (sim_id, R, C, V) in tasks
        }
        try:
            for future in concurrent.futures.as_completed(future_to_task):
                sim_info = future_to_task[future]
                try:
                    rows = future.result()
                    if rows:
                        dataset_rows.extend(rows)
                        print(f"[{sim_info[0]}] Completed, rows: {len(rows)}, total dataset rows: {len(dataset_rows)}")
                    else:
                        print(f"[{sim_info[0]}] Completed with no rows (failed or no data).")
                except Exception as e:
                    print(f"[{sim_info[0]}] Worker raised exception: {e}")

        except KeyboardInterrupt:
            # User hit CTRL+C: try to cancel outstanding tasks
            print("\nKeyboardInterrupt received — cancelling remaining simulations...")
            for fut in future_to_task:
                fut.cancel()
            # allow currently running tasks some time to finish cleanup
            time.sleep(1)

    # After all done (or cancelled), save dataset
    if dataset_rows:
        df = pd.DataFrame(dataset_rows)
        df.to_csv(OUTPUT_CSV, index=False)
        print(f"\nSaved CSV -> {OUTPUT_CSV}")

        if SAVE_NUMPY:
            # Convert to arrays and save compact NumPy .npz (x and Vout arrays may vary lengths per sim;
            # here we save structured arrays by converting dataframe columns)
            try:
                np.savez_compressed(OUTPUT_NUMPY,
                                    SimID=df["SimID"].values,
                                    R=df["R"].values,
                                    C=df["C"].values,
                                    VDC=df["VDC"].values,
                                    x=df["x"].values,
                                    Vout=df["Vout"].values)
                print(f"Saved NumPy -> {OUTPUT_NUMPY}")
            except Exception as e:
                print(f"Failed to save NumPy file: {e}")
    else:
        # still write an empty CSV with headers so you won't get lost
        pd.DataFrame(columns=["SimID", "R", "C", "VDC", "x", "Vout"]).to_csv(OUTPUT_CSV, index=False)
        print(f"No valid data collected — wrote empty CSV header to {OUTPUT_CSV}")

    print("All done. Exiting.")

if __name__ == "__main__":
    main()
