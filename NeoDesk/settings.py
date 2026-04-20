from json_store import JsonStore


import logging
_root = logging.getLogger()
if not _root.handlers:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
log = logging.getLogger(__name__)
def load_settings() -> dict:
    ds = JsonStore()
    return ds.get_settings()

def save_settings(cfg: dict):
    ds = JsonStore()
    for k, v in cfg.items():
        ds.set_setting(k, v)

def get_theme_mode(default: str = "System") -> str:
    cfg = load_settings()
    return cfg.get("theme_mode", default)

def set_theme_mode(mode: str):
    cfg = load_settings()
    cfg["theme_mode"] = mode
    save_settings(cfg)
