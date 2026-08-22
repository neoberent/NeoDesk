from cryptography.fernet import Fernet
import os

# Handles Fernet symmetric encryption/decryption
class CryptoManager:
    def __init__(self):
        with open('schluessel.key', 'rb') as key_file:
            self.key = key_file.read()
        self.fernet = Fernet(self.key)

    @staticmethod
    def generate_key():
        key = Fernet.generate_key()
        with open('schluessel.key', 'wb') as key_file:
            key_file.write(key)
        print("Schlüssel generiert und in 'schluessel.key' gespeichert.")

    def encrypt(self, data):
        return self.fernet.encrypt(data.encode())

    def decrypt(self, token):
        return self.fernet.decrypt(token).decode()
