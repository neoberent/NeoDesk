
# Central config for UI, paths, and files
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
    # Fall back to current dir if not writable
    DATA_DIR = os.path.dirname(__file__)

DB_FILES = {
    "NOTES": os.path.join(DATA_DIR, "notes.json"),
    "USER": os.path.join(DATA_DIR, "data.json"),
}

KEY_FILE = os.path.join(DATA_DIR, "schluessel.key")



# Chat history DB
CHAT_DB = os.path.join(DATA_DIR, 'chat_history.db')