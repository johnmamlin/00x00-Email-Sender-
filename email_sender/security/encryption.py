# Anti-spam techniques and header randomizationfrom cryptography.fernet import Fernet
import os
from cryptography.fernet import Fernet


class EncryptionHandler:
    def __init__(self):
        self.encryption_key = Fernet.generate_key()
        self.cipher_suite = Fernet(self.encryption_key)

    def encrypt_attachment(self, file_data):
        """Encrypt attachment data using Fernet encryption"""
        return self.cipher_suite.encrypt(file_data)
