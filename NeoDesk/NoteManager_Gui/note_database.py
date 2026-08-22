import json, os
from datetime import datetime
from crypto_manager import CryptoManager
from log_setup import get_logger
logger = get_logger(__name__)


# Stores notes to disk, encrypting content via CryptoManager
class NotesStore:
    def __init__(self, filename: str = "notes.json"):
        self.filename = filename
        self.crypto = CryptoManager()
        # Only some CryptoManager versions have this
        if hasattr(self.crypto, "ensure_key"):
            try:
                self.crypto.ensure_key()
            except Exception:
                logger.exception('Unhandled exception')
                pass

        self.notes = []
        self._load()

    def _load(self):
        if os.path.exists(self.filename):
            with open(self.filename, "r", encoding="utf-8") as f:
                try:
                    self.notes = json.load(f)
                except Exception:
                    logger.exception('Unhandled exception')
                    self.notes = []
        else:
            self.notes = []
            self._save()

    def _save(self):
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(self.notes, f, indent=2, ensure_ascii=False)

    def _encrypt(self, text: str) -> str:
        enc = self.crypto.encrypt(text)
        return enc.decode() if isinstance(enc, (bytes, bytearray)) else enc

    def _decrypt(self, enc_text: str) -> str:
        try:
            return self.crypto.decrypt(enc_text)
        except Exception:
            logger.exception('Unhandled exception')
            return ""

    def enumerate_owner(self, owner: str):
        for idx, item in enumerate(self.notes):
            if item.get("owner") == owner:
                dec = self._decrypt(item.get("content", ""))
                yield idx, {"content": dec, "timestamp": item.get("timestamp", ""), "owner": owner}

    def list_decrypted(self, owner: str = None):
        if owner is None:
            out = []
            for item in self.notes:
                dec = self._decrypt(item.get("content", ""))
                out.append({
                    "content": dec,
                    "timestamp": item.get("timestamp", ""),
                    "owner": item.get("owner")
                })
            return out
        return [dec for _, dec in self.enumerate_owner(owner)]

    def add(self, content: str, owner: str):
        enc = self._encrypt(content)
        self.notes.append({
            "content": enc,
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "owner": owner
        })
        self._save()

    def update(self, global_index: int, content: str):
        if 0 <= global_index < len(self.notes):
            enc = self._encrypt(content)
            self.notes[global_index]["content"] = enc
            self.notes[global_index]["timestamp"] = datetime.now().isoformat(timespec="seconds")
            self._save()
            return True
        return False

    def delete(self, global_index: int):
        if 0 <= global_index < len(self.notes):
            del self.notes[global_index]
            self._save()
            return True
        return False
