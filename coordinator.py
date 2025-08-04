from utils import setup_logging, encrypt_data, decrypt_data
import socket
import threading
from sklearn.ensemble import IsolationForest
from Crypto.Random import get_random_bytes
import json
import logging

class Coordinator:
    def __init__(self, host='0.0.0.0', port=5000):  # Use '0.0.0.0' to allow remote connections
        setup_logging('coordinator.log')
        self.host = host
        self.port = port
        self.attributes = {}  # Stores peer data (e.g., bandwidth, CPU)
        self.anomaly_detector = IsolationForest(contamination=0.05)  # ML for attack detection
        self.encryption_key = get_random_bytes(16)  # AES-256 key
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        logging.info(f"Coordinator started on {host}:{port}")

    def handle_client(self, client_socket, addr):
        try:
            while True:
                data = client_socket.recv(1024)
                if not data: break
                packet = decrypt_data(json.loads(data.decode()), self.encryption_key)
                if self.is_anomalous(packet):
                    self.redirect_to_honeypot(client_socket, addr, packet)
                    continue
                if packet['type'] == 'attribute_update':
                    self.attributes[packet['peer_id']] = packet['attributes']
                    client_socket.send(encrypt_data({'type': 'ACK'}, self.encryption_key).encode())
                elif packet['type'] == 'query':
                    result = self.process_query(packet['constraints'], packet['num_peers'])
                    client_socket.send(encrypt_data({'type': 'query_response', 'peers': result}, self.encryption_key).encode())
        except Exception as e:
            logging.error(f"Error handling {addr}: {e}")
        finally:
            client_socket.close()

    def is_anomalous(self, packet):
        features = [packet.get('size', 0), packet.get('frequency', 1)]
        if len(self.anomaly_detector.predict([features])) > 0:
            return self.anomaly_detector.predict([features])[0] == -1  # -1 = anomaly
        return False

    def redirect_to_honeypot(self, client_socket, addr, packet):
        response = encrypt_data({'type': 'honeypot', 'message': 'Suspicious activity logged'}, self.encryption_key)
        client_socket.send(response.encode())
        logging.warning(f"Redirected {addr} to honeypot for: {packet}")

    def start(self):
        logging.info("Coordinator running...")
        while True:
            client_socket, addr = self.server_socket.accept()
            threading.Thread(target=self.handle_client, args=(client_socket, addr)).start()

if __name__ == "__main__":
    Coordinator().start()
