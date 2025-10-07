# Run this first to check if basic networking works
import socket

def test_basic_socket():
    print("🔧 Testing basic socket functionality...")
    
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('127.0.0.1', 9090))
        print("✅ Socket binding works")
        s.close()
        return True
    except Exception as e:
        print(f"❌ Socket issue: {e}")
        return False

if __name__ == "__main__":
    test_basic_socket()