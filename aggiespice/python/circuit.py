import numpy as np

def solve_dc_circuit():
    """Solves a simple DC circuit (2 resistors + voltage source)."""
    print("\n=== DC Circuit Solver ===")
    V = float(input("Enter voltage (V): "))
    R1 = float(input("Enter R1 (Ω): "))
    R2 = float(input("Enter R2 (Ω): "))

    # Kirchhoff's laws: I = V / (R1 + R2)
    I = V / (R1 + R2)
    V1 = I * R1
    V2 = I * R2

    print(f"\nCurrent: {I:.2f} A")
    print(f"Voltage across R1: {V1:.2f} V")
    print(f"Voltage across R2: {V2:.2f} V")

if __name__ == "__main__":
    solve_dc_circuit()