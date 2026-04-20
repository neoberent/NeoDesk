from cryptography.fernet import Fernet  
import os  

# CryptoManager verwaltet die Verschlüsselung und Entschlüsselung von Daten
class CryptoManager:
    """
    Diese Klasse verwaltet die Verschlüsselung und Entschlüsselung von Daten
    mit Hilfe des Fernet-Algorithmus aus der cryptography-Bibliothek.
    """
    def __init__(self):
        """
        Initialisiert das CryptoManager-Objekt und lädt den Schlüssel aus der Datei.
        """
        # Öffne die Schlüsseldatei und lese den Schlüssel für die Verschlüsselung
        with open('schluessel.key', 'rb') as key_file:
            self.key = key_file.read()  
        self.fernet = Fernet(self.key)  

    @staticmethod
    def generate_key():
        """
        Erzeugt einen neuen Schlüssel für die Verschlüsselung und speichert ihn in einer Datei.
        """
        key = Fernet.generate_key()  
        with open('schluessel.key', 'wb') as key_file:
            key_file.write(key)  
        print("Schlüssel generiert und in 'schluessel.key' gespeichert.")  

    def encrypt(self, data):
        """
        Verschlüsselt die übergebenen Daten (Text) und gibt die verschlüsselten Bytes zurück.
        """
        return self.fernet.encrypt(data.encode())  
    def decrypt(self, token):
        """
        Entschlüsselt die übergebenen verschlüsselten Daten und gibt den entschlüsselten Text zurück.
        """
        return self.fernet.decrypt(token).decode()  