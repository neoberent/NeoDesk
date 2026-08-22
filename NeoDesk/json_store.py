# Unified user store: app_data.json in the form {"users": {...}}
import json, os, threading
from typing import Optional, Dict, List, Tuple
from pathlib import Path
from log_setup import get_logger
logger = get_logger(__name__)

DATA_DIR = Path(__file__).resolve().parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

NOTES_JSON    = DATA_DIR / "notes.json"
SETTINGS_JSON = DATA_DIR / "settings.json"

APP_DATA_JSON_CANDIDATES = [
    Path(__file__).resolve().parent / "app_data.json",
    Path(__file__).resolve().parent.parent / "app_data.json",
    Path(__file__).resolve().parents[2] / "app_data.json",
    DATA_DIR / "app_data.json",
]

_LOCK = threading.Lock()

def _atomic_write_text(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


def _find_app_data_json() -> Path:
    for p in APP_DATA_JSON_CANDIDATES:
        if p.exists():
            return p
    # default to project/data/app_data.json if none exists
    return APP_DATA_JSON_CANDIDATES[-1]

def _load_users_json() -> Tuple[dict, Path]:
    """
    Ensures structure: {"users": { "<name>": {"password": "...", "role": "..."} }}
    Returns (data, path).
    """
    p = _find_app_data_json()
    if not p.exists():
        data = {"users": {}}
        _atomic_write_text(p, json.dumps(data, ensure_ascii=False, indent=2))
        return data, p
    try:
        raw = json.loads(p.read_text(encoding="utf-8")) or {}
    except Exception:
        logger.exception('Unhandled exception')
        raw = {}
    if not isinstance(raw, dict):
        raw = {}
    if "users" not in raw or not isinstance(raw["users"], dict):
        raw["users"] = {}
    return raw, p

def _save_users_json(data: dict, path: Path):
    if "users" not in data or not isinstance(data["users"], dict):
        data["users"] = {}
    _atomic_write_text(path, json.dumps(data, ensure_ascii=False, indent=2))


def _ensure_settings():
    if not SETTINGS_JSON.exists():
        _atomic_write_text(SETTINGS_JSON, json.dumps({"theme": "system"}, ensure_ascii=False, indent=2))

def _read_settings() -> dict:
    _ensure_settings()
    try:
        return json.loads(SETTINGS_JSON.read_text(encoding="utf-8"))
    except Exception:
        logger.exception('Unhandled exception')
        return {"theme": "system"}

def _write_settings(d: dict):
    if not isinstance(d, dict):
        d = {}
    _atomic_write_text(SETTINGS_JSON, json.dumps(d, ensure_ascii=False, indent=2))


def _ensure_notes():
    if not NOTES_JSON.exists():
        _atomic_write_text(NOTES_JSON, json.dumps({"_seq": {"notes": 0}, "notes": []}, ensure_ascii=False, indent=2))

def _read_notes() -> dict:
    _ensure_notes()
    try:
        return json.loads(NOTES_JSON.read_text(encoding="utf-8"))
    except Exception:
        logger.exception('Unhandled exception')
        return {"_seq": {"notes": 0}, "notes": []}

def _write_notes(d: dict):
    _atomic_write_text(NOTES_JSON, json.dumps(d, ensure_ascii=False, indent=2))


class JsonStore:
    def get_users(self) -> Dict[str, dict]:
        data, _ = _load_users_json()
        return data["users"]

    def upsert_user(self, username: str, password_hash: str, role: str = "User") -> None:
        with _LOCK:
            data, p = _load_users_json()
            data["users"][username] = {
                "password": password_hash,
                "role": role or "User",
            }
            _save_users_json(data, p)

    def delete_user(self, username: str) -> bool:
        with _LOCK:
            data, p = _load_users_json()
            if username in data["users"]:
                data["users"].pop(username, None)
                _save_users_json(data, p)
                return True
            return False

    def get_settings(self) -> dict:
        return _read_settings()

    def set_settings(self, data: dict) -> None:
        _write_settings(data)

    def list_all(self, owner: Optional[str] = None) -> List[dict]:
        d = _read_notes()
        notes = d.get("notes", [])
        return [n for n in notes if n.get("owner") == owner] if owner else notes

    # Backwards-compat alias
    def list_notes(self, owner: Optional[str] = None) -> List[dict]:
        return self.list_all(owner=owner)

    def get(self, note_id: int | str) -> Optional[dict]:
        d = _read_notes()
        for n in d.get("notes", []):
            if str(n.get("id")) == str(note_id):
                return n
        return None

    def add_note(self, owner: str, combined: str) -> int:
        with _LOCK:
            d = _read_notes()
            seq = int(d.get("_seq", {}).get("notes", 0)) + 1
            d.setdefault("_seq", {})["notes"] = seq
            d.setdefault("notes", []).append({"id": seq, "owner": owner, "combined": combined})
            _write_notes(d)
            return seq

    def update_note(self, note_id: int, combined: str) -> bool:
        with _LOCK:
            d = _read_notes()
            for n in d.get("notes", []):
                if int(n.get("id")) == int(note_id):
                    n["combined"] = combined
                    _write_notes(d)
                    return True
            return False

    def delete_note(self, note_id: int) -> bool:
        with _LOCK:
            d = _read_notes()
            before = len(d.get("notes", []))
            d["notes"] = [n for n in d.get("notes", []) if int(n.get("id")) != int(note_id)]
            if len(d["notes"]) != before:
                _write_notes(d)
                return True
            return False