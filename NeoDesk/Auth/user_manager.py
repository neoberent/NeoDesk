import bcrypt
from json_store import JsonStore
from log_setup import get_logger
logger = get_logger(__name__)

def ensure_admin():
    ds = JsonStore()
    users = ds.get_users()
    if 'admin' not in users:
        hashed = bcrypt.hashpw("admin".encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        ds.upsert_user("admin", hashed, "Admin")

def load_users() -> dict:
    ds = JsonStore()
    return ds.get_users()

def save_users(users: dict):
    ds = JsonStore()
    for username, data in users.items():
        ds.upsert_user(username, data["password"], data.get("role", "User"))

def check_login(username: str, password: str):
    ds = JsonStore()
    users = ds.get_users()
    u = users.get(username)
    if not u:
        return False, None
    try:
        ok = bcrypt.checkpw(password.encode("utf-8"), u["password"].encode("utf-8"))
    except Exception:
        logger.exception('Unhandled exception')
        ok = False
    return ok, u.get("role", "User")