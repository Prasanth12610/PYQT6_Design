import hashlib


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password, stored_hash):
    return hash_password(password) == stored_hash
