from utils import setup_logging, encrypt_data, decrypt_data
import socket
import psutil
import time

class Peer:
    def __init__(self, peer_id, coordinator_host='localhost', coordinator_port=5000):
        setup_logging('peer.log')
        self.peer_id = peer_id
        self.coordinator_host = coordinator_host
        self.coordinator_port = coordinator_port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.coordinator_host, self.coordinator_port))
        logging.info(f"Peer {peer_id} connected to Coordinator")

    def measure_attributes(self):
        return {
            'upload_bandwidth': psutil.net_io_counters().bytes_sent / 1024,
            'download_bandwidth': psutil.net_io_counters().bytes_recv / 1024,
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
        self.socket.send(packet.encode())

if __name__ == "__main__":
    peer = Peer("peer_1")
    while True:
        peer.send_attributes()
        time.sleep(10)  # Update every 10 seconds
