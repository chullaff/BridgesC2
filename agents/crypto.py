import base64
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import json

# Для простоты — ключ фиксированный, 16 байт (AES-128)
KEY = b'Sixteen byte key'

def pad(s):
    # PKCS7 padding
    pad_len = 16 - len(s) % 16
    return s + bytes([pad_len]) * pad_len

def unpad(s):
    pad_len = s[-1]
    return s[:-pad_len]

def encrypt(data: dict) -> str:
    raw = json.dumps(data).encode()
    raw = pad(raw)
    iv = get_random_bytes(16)
    cipher = AES.new(KEY, AES.MODE_CBC, iv)
    encrypted = cipher.encrypt(raw)
    return base64.b64encode(iv + encrypted).decode()

def decrypt(data_str: str) -> dict:
    raw = base64.b64decode(data_str)
    iv = raw[:16]
    encrypted = raw[16:]
    cipher = AES.new(KEY, AES.MODE_CBC, iv)
    decrypted = cipher.decrypt(encrypted)
    decrypted = unpad(decrypted)
    return json.loads(decrypted)
