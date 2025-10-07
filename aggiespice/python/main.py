from ternary import *
from circuit import solve_dc_circuit
from simulation_server import SimulationServer

def menu():
    while True:
        print("\n===== AggieSPICE =====")
        print("1. Ternary Logic Simulator")
        print("2. DC Circuit Solver")
        print("3. Digital Logic Simulator")
        print("4. AC Circuit Solver (Coming Soon)")
        print("5. Exit")
        choice = input("Choose an option: ")

        if choice == "1":
            print_truth_table(ternary_and, "AND")
            print_truth_table(ternary_or, "OR")
        elif choice == "2":
            SimulationServer().start()
        elif choice == "3":
            print("Digital Logic Simulator is under development.")
        elif choice == "4":
            print("AC Circuit Solver is under development.")
        elif choice == "5":
            print("Exiting AggieSPICE.")
            break

if __name__ == "__main__":
    menu()