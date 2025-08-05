from utils import setup_logging, encrypt_data, decrypt_data
import socket
import threading
from sklearn.ensemble import IsolationForest
from Crypto.Random import get_random_bytes
import json
import logging
import os

class Coordinator:
    def __init__(self, host='0.0.0.0', port=5001):  # Changed port to 5001
        if not os.path.exists('logs'):
            os.makedirs('logs')
        setup_logging('logs/coordinator.log')
        self.host = host
        self.port = port
        self.attributes = {}  # Stores peer data (e.g., bandwidth, CPU)
        self.anomaly_detector = IsolationForest(contamination=0.05)
        self.anomaly_detector.fit([[0, 0]])  # Initial fit with dummy data
        self.encryption_key = get_random_bytes(32)  # AES-256 key
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Allow port reuse
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        logging.info(f"Coordinator started on {self.host}:{self.port}")
        # Save the key to a file for peers to use (in production, use proper key exchange)
        with open('coordinator.key', 'wb') as f:
            f.write(self.encryption_key)
        logging.info("Encryption key saved to coordinator.key")

    def handle_client(self, client_socket, addr):
        try:
            logging.info(f"New connection from {addr}")
            while True:
                data = client_socket.recv(1024)
                if not data:
                    logging.info(f"Client {addr} disconnected")
                    break
                try:
                    packet = decrypt_data(json.loads(data.decode()), self.encryption_key)
                    logging.info(f"Received packet from {addr}: {packet['type']}")
                    
                    if self.is_anomalous(packet):
                        self.redirect_to_honeypot(client_socket, addr, packet)
                        continue
                    
                    if packet['type'] == 'attribute_update':
                        self.attributes[packet['peer_id']] = packet['attributes']
                        response = encrypt_data({'type': 'ACK'}, self.encryption_key)
                        client_socket.send(json.dumps(response).encode())
                        logging.info(f"Updated attributes for peer {packet['peer_id']}")
                    
                    elif packet['type'] == 'query':
                        result = self.process_query(packet.get('constraints', {}), packet.get('num_peers', 1))
                        response = encrypt_data({
                            'type': 'query_response',
                            'peers': result
                        }, self.encryption_key)
                        client_socket.send(json.dumps(response).encode())
                        logging.info(f"Processed query for {addr}")
                except json.JSONDecodeError:
                    logging.error(f"Invalid JSON from {addr}")
                except Exception as e:
                    logging.error(f"Error processing packet from {addr}: {e}")
        except Exception as e:
            logging.error(f"Error handling {addr}: {e}")
        finally:
            client_socket.close()

    def is_anomalous(self, packet):
        features = [packet.get('size', 0), packet.get('frequency', 1)]
        prediction = self.anomaly_detector.predict([features])
        return prediction[0] == -1 if len(prediction) > 0 else False

    def redirect_to_honeypot(self, client_socket, addr, packet):
        response = encrypt_data({
            'type': 'honeypot',
            'message': 'Suspicious activity logged'
        }, self.encryption_key)
        client_socket.send(json.dumps(response).encode())
        logging.warning(f"Redirected {addr} to honeypot for: {packet}")

    def process_query(self, constraints, num_peers):
        # Simple query processing - can be enhanced based on requirements
        matching_peers = []
        for peer_id, attrs in self.attributes.items():
            matches = True
            for key, value in constraints.items():
                if key not in attrs or attrs[key] < value:
                    matches = False
                    break
            if matches:
                matching_peers.append(peer_id)
            if len(matching_peers) >= num_peers:
                break
        return matching_peers

    def start(self):
        logging.info("Coordinator running...")
        try:
            while True:
                client_socket, addr = self.server_socket.accept()
                threading.Thread(target=self.handle_client, args=(client_socket, addr)).start()
        except KeyboardInterrupt:
            logging.info("Coordinator shutting down...")
        except Exception as e:
            logging.error(f"Error in coordinator: {e}")
        finally:
            self.server_socket.close()

if __name__ == "__main__":
    Coordinator().start()