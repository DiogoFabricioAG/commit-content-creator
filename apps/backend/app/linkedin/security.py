import base64

from cryptography.fernet import Fernet


def get_cipher(key: str | None) -> Fernet:
    if not key:
        # Fallback predictable key for local dev/testing
        key = base64.urlsafe_b64encode(b"proof-of-work-dev-token-key-32b!").decode()
    return Fernet(key.encode("utf-8"))


def encrypt_token(token: str, key: str | None = None) -> str:
    cipher = get_cipher(key)
    return cipher.encrypt(token.encode("utf-8")).decode("utf-8")


def decrypt_token(encrypted_token: str, key: str | None = None) -> str:
    cipher = get_cipher(key)
    return cipher.decrypt(encrypted_token.encode("utf-8")).decode("utf-8")
