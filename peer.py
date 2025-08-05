from utils import setup_logging, encrypt_data, decrypt_data
import socket
import psutil
import time
import logging
import json
import sys
import os

class Peer:
    def __init__(self, peer_id, coordinator_host='localhost', coordinator_port=5001):  # Changed port to 5001
        if not os.path.exists('logs'):
            os.makedirs('logs')
        setup_logging(f'logs/peer_{peer_id}.log')
        self.peer_id = peer_id
        self.coordinator_host = coordinator_host
        self.coordinator_port = coordinator_port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Load the coordinator's key (in production, use proper key exchange)
        try:
            with open('coordinator.key', 'rb') as f:
                self.encryption_key = f.read()
            logging.info("Loaded coordinator key")
        except FileNotFoundError:
            logging.error("coordinator.key not found. Start the coordinator first.")
            sys.exit(1)
            
        try:
            self.socket.connect((self.coordinator_host, self.coordinator_port))
            logging.info(f"Peer {peer_id} connected to Coordinator at {coordinator_host}:{coordinator_port}")
        except ConnectionRefusedError:
            logging.error(f"Could not connect to coordinator at {coordinator_host}:{coordinator_port}")
            sys.exit(1)
            
        self.last_net_io_counters = psutil.net_io_counters()
        self.last_measure_time = time.time()

    def measure_attributes(self):
        current_time = time.time()
        current_net_io_counters = psutil.net_io_counters()
        time_elapsed = current_time - self.last_measure_time

        upload_bytes_diff = current_net_io_counters.bytes_sent - self.last_net_io_counters.bytes_sent
        download_bytes_diff = current_net_io_counters.bytes_recv - self.last_net_io_counters.bytes_recv

        self.last_net_io_counters = current_net_io_counters
        self.last_measure_time = current_time

        attributes = {
            'upload_bandwidth': (upload_bytes_diff / 1024) / time_elapsed,  # KB/s
            'download_bandwidth': (download_bytes_diff / 1024) / time_elapsed,  # KB/s
            'storage': psutil.disk_usage('/').free / (1024 ** 3),  # GB
            'cpu': psutil.cpu_percent(interval=1)  # %
        }
        
        logging.info(f"Measured attributes: {attributes}")
        return attributes

    def send_attributes(self):
        try:
            attributes = self.measure_attributes()
            packet = encrypt_data({
                'type': 'attribute_update',
                'peer_id': self.peer_id,
                'attributes': attributes
            }, self.encryption_key)
            
            self.socket.send(json.dumps(packet).encode())
            
            # Wait for acknowledgment
            response_data = self.socket.recv(1024)
            if response_data:
                response = decrypt_data(json.loads(response_data.decode()), self.encryption_key)
                if response.get('type') == 'ACK':
                    logging.info("Attributes sent and acknowledged")
                elif response.get('type') == 'honeypot':
                    logging.warning("Flagged as suspicious by coordinator")
                else:
                    logging.warning(f"Unexpected response type: {response.get('type')}")
            
        except Exception as e:
            logging.error(f"Error sending attributes: {e}")
            # Try to reconnect
            try:
                self.socket.close()
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.connect((self.coordinator_host, self.coordinator_port))
                logging.info("Reconnected to coordinator")
            except Exception as e:
                logging.error(f"Failed to reconnect: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python peer.py <peer_id>")
        sys.exit(1)
        
    peer_id = sys.argv[1]
    peer = Peer(peer_id)
    
    try:
        while True:
            peer.send_attributes()
            time.sleep(10)  # Update every 10 seconds
    except KeyboardInterrupt:
        logging.info("Peer shutting down...")
    finally:
        peer.socket.close()