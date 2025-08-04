import json
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import logging

def setup_logging(filename):
    logging.basicConfig(filename=filename, level=logging.INFO,
                       format='%(asctime)s: %(message)s')

def encrypt_data(data, key):
    cipher = AES.new(key, AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest(json.dumps(data).encode())
    return {'nonce': cipher.nonce, 'ciphertext': ciphertext, 'tag': tag}

def decrypt_data(encrypted_data, key):
    cipher = AES.new(key, AES.MODE_EAX, nonce=encrypted_data['nonce'])
    return json.loads(cipher.decrypt_and_verify(encrypted_data['ciphertext'], encrypted_data['tag']).decode())
