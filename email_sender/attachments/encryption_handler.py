def encrypt_attachment(self, file_data):
        """Encrypt attachment data using Fernet encryption"""
        return self.cipher_suite.encrypt(file_data)


from cryptography.fernet import Fernet