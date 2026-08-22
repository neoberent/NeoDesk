import customtkinter as ctk
from settings import get_theme_mode
from Chatpage_Gui.utils import init_ctk, apply_theme, center_window

class BaseThemeMixin:
    def setup_theme(self):
        init_ctk()
        apply_theme(get_theme_mode())

    def center(self, width: int | None = None, height: int | None = None):
        if width and height:
            center_window(self, width, height)
        else:
            center_window(self)

    def set_single_grid(self):
        try:
            self.grid_columnconfigure(0, weight=1)
            self.grid_rowconfigure(0, weight=1)
        except Exception:
            pass

class BaseWindow(BaseThemeMixin, ctk.CTk):
    pass

class BaseToplevel(BaseThemeMixin, ctk.CTkToplevel):
    pass
