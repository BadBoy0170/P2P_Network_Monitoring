from utils import setup_logging
import socket
import threading
import logging
import json
import os

class Honeypot:
    def __init__(self, host='localhost', port=9999):
        if not os.path.exists('logs'):
            os.makedirs('logs')
        setup_logging('logs/honeypot.log')
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Allow port reuse
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.host, self.port))
        self.socket.listen(5)
        logging.info(f"Honeypot active on {self.host}:{self.port}")

    def handle_attacker(self, client_socket, addr):
        try:
            logging.warning(f"New connection from potential attacker: {addr}")
            while True:
                try:
                    data = client_socket.recv(1024).decode()
                    if not data:
                        break
                    logging.warning(f"Malicious activity from {addr}: {data}")
                    client_socket.send(json.dumps({'status': 'logged'}).encode())
                except Exception as e:
                    logging.error(f"Error receiving data from {addr}: {e}")
                    break
        except Exception as e:
            logging.error(f"Honeypot error handling {addr}: {e}")
        finally:
            logging.info(f"Attacker {addr} disconnected")
            client_socket.close()

    def start(self):
        logging.info("Honeypot running...")
        try:
            while True:
                client_socket, addr = self.socket.accept()
                threading.Thread(target=self.handle_attacker, args=(client_socket, addr)).start()
        except KeyboardInterrupt:
            logging.info("Honeypot shutting down...")
        except Exception as e:
            logging.error(f"Error in honeypot: {e}")
        finally:
            self.socket.close()

if __name__ == "__main__":
    Honeypot().start()