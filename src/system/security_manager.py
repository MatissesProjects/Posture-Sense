import os
from cryptography.fernet import Fernet
import logging

logger = logging.getLogger(__name__)

KEY_FILE = ".posture_key"

class SecurityManager:
    def __init__(self):
        self.key = self._load_or_generate_key()
        self.fernet = Fernet(self.key)

    def _load_or_generate_key(self):
        """ Loads existing key or creates a new one. """
        if os.path.exists(KEY_FILE):
            with open(KEY_FILE, "rb") as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(KEY_FILE, "wb") as f:
                # Set permissions to user-only on Unix systems (optional for Windows)
                os.chmod(KEY_FILE, 0o600)
                f.write(key)
            logger.info("New encryption key generated.")
            return key

    def encrypt(self, data: str) -> str:
        """ Encrypts a string and returns a base64 encoded string. """
        if not data: return ""
        return self.fernet.encrypt(data.encode()).decode()

    def decrypt(self, encrypted_data: str) -> str:
        """ Decrypts a base64 encoded string. """
        if not encrypted_data: return ""
        try:
            return self.fernet.decrypt(encrypted_data.encode()).decode()
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            return ""

if __name__ == "__main__":
    sm = SecurityManager()
    secret = "Top Secret Posture Data"
    encrypted = sm.encrypt(secret)
    print(f"Encrypted: {encrypted}")
    print(f"Decrypted: {sm.decrypt(encrypted)}")
