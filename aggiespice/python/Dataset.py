import numpy as np
import json

def generate_rc_dataset(n=1000):
    data = []
    for _ in range(n):
        R = np.random.uniform(100, 10000)
        C = np.random.uniform(1e-6, 1e-3)
        V = np.random.uniform(1, 12)
        duration = 0.01
        t = np.linspace(0, duration, 100)
        voltage = V * np.exp(-t / (R*C))
        data.append({
            "netlist": {"R": R, "C": C, "V": V},
            "time": t.tolist(),
            "voltage": voltage.tolist()
        })
    return data

def generate_rl_dataset(n=1000):
    data = []
    for _ in range(n):
        R = np.random.uniform(10, 1000)
        L = np.random.uniform(1e-3, 1)
        V = np.random.uniform(1, 12)
        duration = 0.01
        t = np.linspace(0, duration, 100)
        current = (V/R) * (1 - np.exp(-R*t/L))
        data.append({
            "netlist": {"R": R, "L": L, "V": V},
            "time": t.tolist(),
            "current": current.tolist()
        })
    return data

def generate_rlc_dataset(n=1000):
    data = []
    for _ in range(n):
        R = np.random.uniform(10, 1000)
        L = np.random.uniform(1e-3, 1)
        C = np.random.uniform(1e-6, 1e-3)
        V = np.random.uniform(1, 12)
        duration = 0.01
        t = np.linspace(0, duration, 100)
        alpha = R / (2*L)
        omega_0 = 1 / np.sqrt(L*C)
        omega_d = np.sqrt(omega_0**2 - alpha**2)
        voltage = V * np.exp(-alpha*t) * (np.cos(omega_d*t) + (alpha/omega_d)*np.sin(omega_d*t))
        data.append({
            "netlist": {"R": R, "L": L, "C": C, "V": V},
            "time": t.tolist(),
            "voltage": voltage.tolist()
        })
    return data

def generate_voltage_divider_dataset(n=1000):
    data = []
    for _ in range(n):
        R1 = np.random.uniform(100, 10000)
        R2 = np.random.uniform(100, 10000)
        Vin = np.random.uniform(1, 12)
        Vout = Vin * (R2 / (R1 + R2))
        data.append({
            "netlist": {"R1": R1, "R2": R2, "Vin": Vin},
            "Vout": Vout
        })
    return data

#Main function to generate and save datasets; This can be called with different types to generate different datasets by AggieC.I.R.C.A.
def process_data(type):
    if type == "RC":
        dataset = generate_rc_dataset()
        with open("aggiespice/data/AI_Data/rc_dataset.json", "w") as f:
            json.dump(dataset, f)
    elif type == "RL":
        dataset = generate_rl_dataset()
        with open("aggiespice/data/AI_Data/rl_dataset.json", "w") as f:
            json.dump(dataset, f)
    elif type == "RLC":
        dataset = generate_rlc_dataset()
        with open("aggiespice/data/AI_Data/rlc_dataset.json", "w") as f:
            json.dump(dataset, f)
    elif type == "VoltageDivider":
        dataset = generate_voltage_divider_dataset()
        with open("aggiespice/data/AI_Data/voltage_divider_dataset.json", "w") as f:
            json.dump(dataset, f)
    else:
        print("Unknown dataset type.")

