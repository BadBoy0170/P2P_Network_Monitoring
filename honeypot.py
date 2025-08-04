from utils import setup_logging
import socket
import threading
import logging
import json

class Honeypot:
    def __init__(self, host='localhost', port=9999):
        setup_logging('honeypot.log')
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        self.socket.listen(5)
        logging.info(f"Honeypot active on {self.host}:{self.port}")

    def handle_attacker(self, client_socket, addr):
        try:
            # In a real honeypot, you'd log and analyze the data more thoroughly
            data = client_socket.recv(1024).decode()
            logging.warning(f"Malicious activity from {addr}: {data}")
            client_socket.send(json.dumps({'status': 'logged'}).encode())
        except Exception as e:
            logging.error(f"Honeypot error handling {addr}: {e}")
        finally:
            client_socket.close()

    def start(self):
        logging.info("Honeypot running...")
        while True:
            client_socket, addr = self.socket.accept()
            threading.Thread(target=self.handle_attacker, args=(client_socket, addr)).start()

if __name__ == "__main__":
    Honeypot().start()
