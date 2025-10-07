import numpy as np

# Ternary values: -1 (False), 0 (Unknown), +1 (True)
T, O, F = -1, 0, 1  # T = -1 (Ternary False), F = +1 (Ternary True)

def ternary_not(a):
    """Ternary NOT gate (inverts -1 ↔ +1, keeps 0)."""
    return -a

def ternary_and(a, b):
    """Ternary AND (MIN gate)."""
    return np.minimum(a, b)

def ternary_or(a, b):
    """Ternary OR (MAX gate)."""
    return np.maximum(a, b)

def print_truth_table(gate_func, gate_name):
    """Prints truth table for a ternary gate."""
    inputs = [T, O, F]
    print(f"\n{gate_name} Gate Truth Table:")
    print("A \\ B |  T  |  0  |  F  ")
    print("------|-----|-----|-----")
    for a in inputs:
        row = f"  {a}   |"
        for b in inputs:
            output = gate_func(a, b)
            row += f"  {output}  |"
        print(row)

# Test
if __name__ == "__main__":
    print_truth_table(ternary_and, "AND")
    print_truth_table(ternary_or, "OR")
    print("\nNOT Gate:")
    print(f"NOT(T) = {ternary_not(T)}")
    print(f"NOT(0) = {ternary_not(O)}")
    print(f"NOT(F) = {ternary_not(F)}")