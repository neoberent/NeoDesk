# Thin wrapper around CryptoManager for naming clarity in NoteManager
try:
    from crypto_manager import CryptoManager
except Exception:  # if not available, provide a noop fallback
    CryptoManager = None

class NoteEncryptor:
    def __init__(self):
        self._cm = CryptoManager() if CryptoManager else None

    def ensure_key(self):
        # no-op if CryptoManager handles keys internally
        return True

    def encrypt(self, plaintext: str) -> str:
        if self._cm:
            return self._cm.encrypt(plaintext)
        return plaintext  # fallback: no encryption

    def decrypt(self, ciphertext: str) -> str:
        if self._cm:
            return self._cm.decrypt(ciphertext)
        return ciphertext  # fallback: no encryption
