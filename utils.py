import json
import base64
try:
    from Crypto.Cipher import AES
    from Crypto.Random import get_random_bytes
except ImportError:
    from crypto.Cipher import AES
    from crypto.Random import get_random_bytes
import logging

def setup_logging(filename):
    logging.basicConfig(filename=filename, level=logging.INFO,
                       format='%(asctime)s: %(message)s')

def encrypt_data(data, key):
    cipher = AES.new(key, AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest(json.dumps(data).encode())
    return {'nonce': base64.b64encode(cipher.nonce).decode(),
            'ciphertext': base64.b64encode(ciphertext).decode(),
            'tag': base64.b64encode(tag).decode()}

def decrypt_data(encrypted_data, key):
    nonce = base64.b64decode(encrypted_data['nonce'])
    ciphertext = base64.b64decode(encrypted_data['ciphertext'])
    tag = base64.b64decode(encrypted_data['tag'])
    cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
    return json.loads(cipher.decrypt_and_verify(ciphertext, tag).decode())