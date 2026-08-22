
"""Zentrale Konfiguration für UI, Pfade und Dateien."""
import os
from log_setup import get_logger
logger = get_logger(__name__)

WINDOW_WIDTH = 980
WINDOW_HEIGHT = 640
WINDOW_MINSIZE = (100, 120)

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
try:
    os.makedirs(DATA_DIR, exist_ok=True)
except Exception:
    logger.exception('Unhandled exception')
    # Falls kein Schreibrecht vorhanden ist, falle auf das aktuelle Verzeichnis zurück
    DATA_DIR = os.path.dirname(__file__)

DB_FILES = {
    "NOTES": os.path.join(DATA_DIR, "notes.json"),
    "USER": os.path.join(DATA_DIR, "data.json"),
}

KEY_FILE = os.path.join(DATA_DIR, "schluessel.key")



# SQLite database for chat history
CHAT_DB = os.path.join(DATA_DIR, 'chat_history.db')