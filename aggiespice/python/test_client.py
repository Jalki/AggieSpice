import socket
import json
import time

def test_server(host='127.0.0.1', port=9090):
    """Test the simulation server"""
    try:
        # Create test circuit
        test_circuit = {
            "components": [
                {"type": "R", "value": 1000, "nodes": [1, 2]},
                {"type": "C", "value": 1e-6, "nodes": [2, 0]}
            ],
            "analysis": "transient",
            "duration": 0.01,
            "points": 1000
        }
        
        # Connect and send
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(5.0)
            s.connect((host, port))
            
            print(f"📡 Sending test circuit to {host}:{port}")
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
                print("✅ Simulation successful!")
                print(f"📊 Generated {len(result['time'])} data points")
                print(f"📈 Voltage range: {min(result['voltage']):.3f}V to {max(result['voltage']):.3f}V")
            else:
                print(f"❌ Simulation failed: {result['error']}")
                
    except ConnectionRefusedError:
        print(f"❌ Could not connect to {host}:{port}")
        print("Make sure the server is running!")
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_server()