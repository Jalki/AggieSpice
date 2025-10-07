from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import numpy as np

class SimulationHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            circuit_data = json.loads(post_data.decode('utf-8'))
            
            # Run simulation
            result = self.simulate_circuit(circuit_data)
            
            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')  # CORS for Godot
            self.end_headers()
            self.wfile.write(json.dumps(result).encode('utf-8'))
            
        except Exception as e:
            self.send_error(500, f"Server error: {str(e)}")
    
    def simulate_circuit(self, netlist):
        """Same simulation logic as before"""
        duration = netlist.get('duration', 1.0)
        points = netlist.get('points', 1000)
        
        t = np.linspace(0, duration, points)
        voltage = np.sin(2 * np.pi * 5 * t)  # 5Hz sine wave
        
        return {
            'time': t.tolist(),
            'voltage': voltage.tolist(),
            'success': True
        }
    
    def do_OPTIONS(self):
        # Handle CORS preflight
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

def run_http_server(port=9090):
    server_address = ('', port)
    httpd = HTTPServer(server_address, SimulationHandler)
    print(f"🌐 HTTP Simulation server running on port {port}")
    print("Use Ctrl+C to stop")
    httpd.serve_forever()

if __name__ == "__main__":
    run_http_server()