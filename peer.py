from utils import setup_logging, encrypt_data, decrypt_data
import socket
import psutil
import time
import logging
import json
import sys
from Crypto.Random import get_random_bytes

class Peer:
    def __init__(self, peer_id, coordinator_host='localhost', coordinator_port=5000):
        setup_logging('peer.log')
        self.peer_id = peer_id
        self.coordinator_host = coordinator_host
        self.coordinator_port = coordinator_port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # For simplicity, using a hardcoded key. In production, use a secure key exchange.
        self.encryption_key = get_random_bytes(32)  # AES-256 key (32 bytes)
        self.socket.connect((self.coordinator_host, self.coordinator_port))
        logging.info(f"Peer {peer_id} connected to Coordinator")
        self.last_net_io_counters = psutil.net_io_counters()

    def measure_attributes(self):
        current_net_io_counters = psutil.net_io_counters()
        time_elapsed = 10 # Assuming 10 seconds update interval

        upload_bytes_diff = current_net_io_counters.bytes_sent - self.last_net_io_counters.bytes_sent
        download_bytes_diff = current_net_io_counters.bytes_recv - self.last_net_io_counters.bytes_recv

        self.last_net_io_counters = current_net_io_counters

        return {
            'upload_bandwidth': (upload_bytes_diff / 1024) / time_elapsed,
            'download_bandwidth': (download_bytes_diff / 1024) / time_elapsed,
            'storage': psutil.disk_usage('/').free / (1024 ** 3),
            'cpu': psutil.cpu_percent()
        }

    def send_attributes(self):
        attributes = self.measure_attributes()
        packet = encrypt_data({
            'type': 'attribute_update',
            'peer_id': self.peer_id,
            'attributes': attributes
        }, self.encryption_key)
        self.socket.send(json.dumps(packet).encode())

if __name__ == "__main__":
    peer_id = sys.argv[1] if len(sys.argv) > 1 else "default_peer"
    peer = Peer(peer_id)
    while True:
        peer.send_attributes()
        time.sleep(10)  # Update every 10 seconds
