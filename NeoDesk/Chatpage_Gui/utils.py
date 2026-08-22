import customtkinter as ctk
from log_setup import get_logger
logger = get_logger(__name__)

def init_ctk():
    # Safe to call more than once
    try:
        ctk.set_default_color_theme("blue")
    except Exception:
        logger.exception('Unhandled exception')
        pass

def apply_theme(mode: str | None = None):
    if not mode:
        mode = "System"
    try:
        ctk.set_appearance_mode(mode)
    except Exception:
        logger.exception('Unhandled exception')
        ctk.set_appearance_mode("System")

def center_window(win, w=980, h=640):
    try:
        win.update_idletasks()
        sw = win.winfo_screenwidth()
        sh = win.winfo_screenheight()
        x = int((sw - w) / 2)
        y = int((sh - h) / 2)
        win.geometry(f"{w}x{h}+{x}+{y}")
    except Exception:
        logger.exception('Unhandled exception')
        win.geometry(f"{w}x{h}")

class Grid:
    @staticmethod
    def fill(widget, row=0, col=0, padx=0, pady=0):
        widget.grid(row=row, column=col, sticky="nsew", padx=padx, pady=pady)

    @staticmethod
    def make_flexible(widget, rows=(0,), cols=(0,)):
        for r in rows:
            widget.grid_rowconfigure(r, weight=1)
        for c in cols:
            widget.grid_columnconfigure(c, weight=1)