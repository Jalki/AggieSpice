import socket
import json
import threading
import numpy as np
from contextlib import closing
import Dataset as dset # Custom dataset module for circuit data generation

#This function checks for an available port and returns it
def find_available_port(start_port=9090, max_attempts=10):
    """Find an available port starting from start_port"""
    for port in range(start_port, start_port + max_attempts):
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
            try:
                sock.bind(('localhost', port))
                return port
            except OSError:
                continue
    raise Exception(f"No available ports found in range {start_port}-{start_port + max_attempts}")

#Our main server class that hooks everything together, handles connections, and runs simulations calculations
class SimulationServer:
    def __init__(self, host='127.0.0.1', port=None, debug=False):
        self.host = host
        self.port = port or find_available_port()
        self.is_running = False
        self.debug = debug
        
    def log(self, message):
        """Log messages if debug mode is enabled"""
        if self.debug:
            print(f"🔧 [DEBUG] {message}")

    #Simulate a simple RC circuit as a placeholder for real simulation logic; in a real implementation, this would parse the netlist and perform actual circuit analysis
    #Another option is to integrate with a library like PySpice or similar for real SPICE simulations
    #But for now, we just return a dummy sine wave or exponential decay based on analysis type
    #Godot can then plot this data and use it for animations or other purposes    
    def simulate_circuit(self, netlist):
        """Simple RC circuit simulation for testing"""
        try:
            if self.debug:
                print(f"🔧 [DEBUG] Starting simulation with: {netlist}")
                
            duration = netlist.get('duration', 1.0)
            points = netlist.get('points', 1000)
            
            t = np.linspace(0, duration, points)
            
            # More realistic circuit simulation based on components
            if 'components' in netlist and self.debug:
                print(f"🔧 [DEBUG] Processing {len(netlist['components'])} components")
                
            # Simple demo - sine wave for AC, exponential for RC
            analysis_type = netlist.get('analysis', 'transient')
            if analysis_type == 'ac':
                voltage = np.sin(2 * np.pi * 5 * t)  # 5Hz sine wave
            else:
                # RC circuit response
                voltage = 5 * np.exp(-t / 0.001)  # Exponential decay
            
            result = {
                'time': t.tolist(),
                'voltage': voltage.tolist(),
                'success': True,
                'message': f'Simulated {len(t)} points for {analysis_type} analysis'
            }
            
            if self.debug:
                print(f"🔧 [DEBUG] Simulation completed: {result['message']}")
                
            return result
            
        except Exception as e:
            error_msg = f'Simulation error: {str(e)}'
            if self.debug:
                print(f"🔧 [DEBUG] {error_msg}")
            return {'success': False, 'error': error_msg}
    
    #Function to handle each client connection in a separate thread
    #This allows multiple clients to connect and be served simultaneously
    def handle_client(self, conn, addr):
        """Handle a single client connection"""
        try:
            self.log(f"New connection from {addr}")
            
             # Send handshake ack so Godot sees a "live" connection
            conn.send(json.dumps({"status": "connected"}).encode("utf-8"))
            # Read data
            data = b""
            conn.settimeout(5.0)
            while True:
                chunk = conn.recv(1024)
                if not chunk:
                    break
                data += chunk
                if len(chunk) < 1024:
                    break
            
            if data:
                circuit_data = json.loads(data.decode('utf-8'))
                self.log(f"Received circuit data: {circuit_data.get('analysis', 'unknown')} analysis")
                
                result = self.simulate_circuit(circuit_data)
                response = json.dumps(result).encode('utf-8')
                conn.send(response)
                self.log(f"Sent response: {len(response)} bytes")
                
        except json.JSONDecodeError as e:
            error_msg = f'Invalid JSON: {str(e)}'
            self.log(f"JSON error: {error_msg}")
            error_result = {'success': False, 'error': error_msg}
            conn.send(json.dumps(error_result).encode('utf-8'))
        except socket.timeout:
            error_msg = 'Receive timeout'
            self.log(error_msg)
            error_result = {'success': False, 'error': error_msg}
            conn.send(json.dumps(error_result).encode('utf-8'))
        except Exception as e:
            error_msg = f'Server error: {str(e)}'
            self.log(f"Unexpected error: {error_msg}")
            error_result = {'success': False, 'error': error_msg}
            conn.send(json.dumps(error_result).encode('utf-8'))
        finally:
            conn.close()
            self.log(f"Connection to {addr} closed")
    
    # Start the server and listen for connections
    def start(self):
        """Start the server with better error handling"""
        try:
            self.is_running = True
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                # Allow port reuse
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                
                s.bind((self.host, self.port))
                s.listen()
                s.settimeout(1.0)  # Allow periodic checking of is_running
                
                print(f"🎯 Simulation server listening on {self.host}:{self.port}")
                if self.debug:
                    print("🔧 Debug mode: ENABLED")
                print("Press Ctrl+C to stop the server")
                
                while self.is_running:
                    try:
                        conn, addr = s.accept()
                        client_thread = threading.Thread(
                            target=self.handle_client, args=(conn, addr),
                            daemon=True
                        )
                        client_thread.start()
                    except socket.timeout:
                        continue
                        
        except OSError as e:
            print(f"❌ Could not start server: {e}")
            print("Try changing the port number or checking if another server is running")
        except KeyboardInterrupt:
            print("\n🛑 Server stopped by user")
        finally:
            self.is_running = False

# Self-test function to verify server functionality
def run_self_test(server_port):
    """Run a self-test to verify the server is working"""
    print("\n🧪 Running self-test...")
    
    try:
        # Create test circuit
        test_circuit = {
            "components": [
                {"type": "R", "value": 1000, "nodes": [1, 2], "id": "R1"},
                {"type": "C", "value": 1e-6, "nodes": [2, 0], "id": "C1"},
                {"type": "V", "value": 5, "nodes": [1, 0], "id": "V1"}
            ],
            "analysis": "transient",
            "duration": 0.01,
            "points": 500
        }
        
        # Connect and send
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(5.0)
            s.connect(('127.0.0.1', server_port))
            
            print(f"📡 Sending test circuit to 127.0.0.1:{server_port}")
            json_data = json.dumps(test_circuit)
            s.send(json_data.encode('utf-8'))
            s.shutdown(socket.SHUT_WR)  # Signal that we're done sending
            
            # Receive response
            response = b""
            while True:
                chunk = s.recv(4096)
                if not chunk:
                    break
                response += chunk
            
            result = json.loads(response.decode('utf-8'))
            
            if result['success']:
                print("✅ Self-test successful!")
                print(f"📊 {result['message']}")
                print(f"📈 Voltage range: {min(result['voltage']):.3f}V to {max(result['voltage']):.3f}V")
                return True
            else:
                print(f"❌ Self-test failed: {result['error']}")
                return False
                
    except ConnectionRefusedError:
        print(f"❌ Could not connect to server on port {server_port}")
        print("Make sure the server is running!")
        return False
    except Exception as e:
        print(f"❌ Self-test error: {e}")
        return False

# Function to generate sample datasets using the Dataset module
def generate_sample_datasets():
    """Generate sample datasets using the Dataset module"""
    print("Generating sample datasets...")
    dset.process_data("RC")
    dset.process_data("RL")
    dset.process_data("RLC")
    dset.process_data("VoltageDivider")
    print("Sample datasets generated.")

# Main function with user interaction, allowing configuration and starting the server
# It also offers to run a self-test to verify everything is working before going live
# Godot will connect to this server for simulations, replacing this main function in production
def main():
    """Main function with user interaction"""
    print("=" * 50)
    print("       SPICE Simulation Server")
    print("=" * 50)
    
    # Ask for debug mode
    debug_input = input("Enable debug mode? (y/n): ").lower().strip()
    debug_mode = debug_input in ['y', 'yes', '1']
    
    # Ask for port
    port_input = input("Enter server port [9090]: ").strip()
    try:
        port = int(port_input) if port_input else 9090
    except ValueError:
        print("Invalid port, using default 9090")
        port = 9090
    
    # Create and start server
    server = SimulationServer(port=port, debug=debug_mode)

    #This will generate sample datasets for AggieC.I.R.C.A to use if needed
    gen_data = input("Generate sample datasets? (y/n): ").lower().strip()
    if gen_data in ['y', 'yes', '1']:
        generate_sample_datasets()
    else:
        print("Skipping dataset generation.")
    
    # Ask if user wants to run a self-test
    test_input = input("\nRun self-test before starting server? (y/n): ").lower().strip()
    if test_input in ['y', 'yes', '1']:
        # We need to start the server in a thread to test it
        print("Starting server for testing...")
        
        def start_server_thread():
            server.start()
        
        server_thread = threading.Thread(target=start_server_thread, daemon=True)
        server_thread.start()
        
        # Wait for server to start
        import time
        time.sleep(2)
        
        # Run the test
        if run_self_test(port):
            print("\n✅ Server is ready for Godot connections!")
        else:
            print("\n❌ Server test failed, but continuing anyway...")
        
        # Let the server continue running
        print("\n🚀 Server is running and ready for connections...")
        try:
            while server.is_running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Server stopped by user")
    else:
        # Just start the server normally
        server.start()

if __name__ == "__main__":
    main()