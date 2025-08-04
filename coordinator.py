from utils import setup_logging, encrypt_data, decrypt_data
import socket
import threading
from sklearn.ensemble import IsolationForest
from Crypto.Random import get_random_bytes
import json
import logging

class Coordinator:
    def __init__(self, host='0.0.0.0', port=5000):
        setup_logging('coordinator.log')
        self.host = host
        self.port = port
        self.attributes = {}  # Stores peer data (e.g., bandwidth, CPU)
        self.anomaly_detector = IsolationForest(contamination=0.05)  # ML for attack detection
        # Initialize the anomaly detector with some dummy data or a warm-up phase
        # For now, we'll fit it with a single dummy point. In a real system, you'd collect data.
        self.anomaly_detector.fit([[0, 0]]) # Fit with a dummy data point to avoid NotFittedError
        self.encryption_key = get_random_bytes(32)  # AES-256 key (32 bytes)
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        logging.info(f"Coordinator started on {self.host}:{self.port}")

    def handle_client(self, client_socket, addr):
        try:
            while True:
                data = client_socket.recv(1024)
                if not data: break
                # Decode the received data and then decrypt
                packet = decrypt_data(json.loads(data.decode()), self.encryption_key)
                
                if self.is_anomalous(packet):
                    self.redirect_to_honeypot(client_socket, addr, packet)
                    continue
                if packet['type'] == 'attribute_update':
                    self.attributes[packet['peer_id']] = packet['attributes']
                    client_socket.send(json.dumps(encrypt_data({'type': 'ACK'}, self.encryption_key)).encode())
                elif packet['type'] == 'query':
                    result = self.process_query(packet['constraints'], packet['num_peers'])
                    client_socket.send(json.dumps(encrypt_data({'type': 'query_response', 'peers': result}, self.encryption_key)).encode())
        except Exception as e:
            logging.error(f"Error handling {addr}: {e}")
        finally:
            client_socket.close()

    def is_anomalous(self, packet):
        features = [packet.get('size', 0), packet.get('frequency', 1)]
        prediction = self.anomaly_detector.predict([features])
        if len(prediction) > 0:
            return prediction[0] == -1  # -1 = anomaly
        return False

    def redirect_to_honeypot(self, client_socket, addr, packet):
        response = encrypt_data({'type': 'honeypot', 'message': 'Suspicious activity logged'}, self.encryption_key)
        client_socket.send(json.dumps(response).encode())
        logging.warning(f"Redirected {addr} to honeypot for: {packet}")

    def start(self):
        logging.info("Coordinator running...")
        while True:
            client_socket, addr = self.server_socket.accept()
            threading.Thread(target=self.handle_client, args=(client_socket, addr)).start()

if __name__ == "__main__":
    Coordinator().start()
