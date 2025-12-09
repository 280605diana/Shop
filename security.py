# security.py
import hashlib

def hash_password(password: str) -> bytes:
    # Возвращаем bytes, чтобы класть в VARBINARY
    return hashlib.sha256(password.encode('utf-8')).digest()


def verify_password(password: str, hashed: bytes) -> bool:
    return hash_password(password) == hashed
