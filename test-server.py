import socket
import ssl
import json
import sys
import hashlib
import argparse
from typing import Any, Dict

class ElectrumClient:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.use_ssl = port in [50002, 50004, 443] or (port >= 50002 and port % 2 == 0)
        self.socket = None

    def connect(self) -> None:
        try:
            raw_sock = socket.create_connection((self.host, self.port), 10)
            if self.use_ssl:
                context = ssl.create_default_context()
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                self.socket = context.wrap_socket(raw_sock)
            else:
                self.socket = raw_sock
            print(f"Connected to {self.host}:{self.port} (SSL={self.use_ssl})")
        except Exception as e:
            print(f"Connection failed: {e}")
            sys.exit(1)

    def close(self) -> None:
        if self.socket:
            self.socket.close()

    def request(self, method: str, params: list = None, msg_id: int = 0) -> Dict[str, Any]:
        if not self.socket:
            raise ConnectionError("Not connected")
        
        req = {"id": msg_id, "method": method, "params": params or []}
        payload = (json.dumps(req) + "\n").encode()
        self.socket.sendall(payload)
        
        # Receive response
        data = b""
        while b"\n" not in data:
            chunk = self.socket.recv(4096)
            if not chunk:
                break
            data += chunk
        
        line = data.split(b"\n", 1)[0].decode()
        return json.loads(line) if line else {}

def parse_address(address: str) -> tuple[str, int]:
    if ':' not in address:
        raise ValueError("Format: IP:port")
    host, port_str = address.rsplit(':', 1)
    try:
        port = int(port_str)
        if not (1 <= port <= 65535):
            raise ValueError("Port must be 1-65535")
    except ValueError:
        raise ValueError("Invalid port number")
    return host, port

def print_result(title: str, data: Dict[str, Any]) -> None:
    print(f"\n{title}:")
    print("=" * 50)
    print(json.dumps(data, indent=2))

def get_block_hash(hex_header: str) -> str:
    header_bytes = bytes.fromhex(hex_header)
    return hashlib.sha256(hashlib.sha256(header_bytes).digest()).digest()[::-1].hex()

def main() -> None:
    parser = argparse.ArgumentParser(description='ElectrumX test client')
    parser.add_argument('address', help='Server address (IP:port)')
    args = parser.parse_args()
    
    try:
        host, port = parse_address(args.address)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    
    client = ElectrumClient(host, port)
    
    try:
        client.connect()
        
        # Version handshake
        ver = client.request("server.version", ["test-client", "1.4"], 0)
        print_result("Server Version", ver)
        
        # Server features
        features = client.request("server.features", [], 1)
        print_result("Server Features", features)
        
        # Latest block header
        headers = client.request("blockchain.headers.subscribe", [], 2)
        if headers.get('result', {}).get('hex'):
            hex_header = headers['result']['hex']
            height = headers['result']['height']
            block_hash = get_block_hash(hex_header)
            print_result("Latest Block", {"height": height, "hash": block_hash})
        else:
            print_result("Headers Subscribe", headers)
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    main()