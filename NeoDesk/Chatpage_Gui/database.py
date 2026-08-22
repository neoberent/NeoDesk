
import os
import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from config import CHAT_DB, DB_FILES
from log_setup import get_logger
logger = get_logger(__name__)

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    role TEXT CHECK(role IN ('user','assistant')) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_messages_user ON messages(username);
"""

class Database:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or CHAT_DB
        Path(os.path.dirname(self.db_path)).mkdir(parents=True, exist_ok=True)
        self._init_db()
        # one-time migration from JSON if empty
        try:
            self._maybe_migrate_from_json()
        except Exception:
            logger.exception('Unhandled exception')
            pass

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._connect() as con:
            con.executescript(SCHEMA_SQL)

    def _messages_count(self) -> int:
        with self._connect() as con:
            cur = con.execute("SELECT COUNT(*) FROM messages")
            return int(cur.fetchone()[0])

    def _maybe_migrate_from_json(self):
        if self._messages_count() > 0:
            return
        json_path = Path(DB_FILES.get("USER", ""))
        if not json_path.exists():
            return
        try:
            data = json.loads(json_path.read_text(encoding="utf-8"))
        except Exception:
            logger.exception('Unhandled exception')
            return
        items = []
        if isinstance(data, list):
            items = data
        elif isinstance(data, dict):
            if "messages" in data and isinstance(data["messages"], list):
                items = data["messages"]
            else:
                for _, v in data.items():
                    if isinstance(v, list):
                        items.extend(v)

        rows = []
        for m in items:
            if not isinstance(m, dict):
                continue
            role = m.get("role") or ("assistant" if m.get("author") == "ai" else "user")
            content = m.get("content") or m.get("text") or m.get("message") or ""
            username = m.get("user") or m.get("username") or m.get("owner") or None
            if not content:
                continue
            rows.append((username, role if role in ("user","assistant") else "user", content))

        if not rows:
            return

        with self._connect() as con:
            con.executemany(
                "INSERT INTO messages(username, role, content) VALUES(?,?,?)", rows
            )

    def save_message(self, username: str, message: Dict[str, Any]) -> None:
        role = message.get("role", "user")
        content = message.get("content", "")
        if not content:
            return
        with self._connect() as con:
            con.execute(
                "INSERT INTO messages(username, role, content) VALUES(?,?,?)",
                (username, "assistant" if role == "assistant" else "user", content),
            )

    def get_messages(self, username: Optional[str] = None) -> List[Dict[str, Any]]:
        with self._connect() as con:
            if username:
                cur = con.execute(
                    "SELECT username, role, content, created_at FROM messages "
                    "WHERE (username = ? AND role = 'user') OR role = 'assistant' "
                    "ORDER BY id ASC",
                    (username,),
                )
            else:
                cur = con.execute(
                    "SELECT username, role, content, created_at FROM messages ORDER BY id ASC"
                )
            out = []
            for uname, role, content, ts in cur.fetchall():
                out.append({"user": uname, "role": role, "content": content, "created_at": ts})
            return out