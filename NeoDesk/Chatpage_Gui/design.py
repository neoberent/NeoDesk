import customtkinter as ctk

# Core dark-theme palette; ACCENT/DANGER pairs are the base color and its hover shade.
BG        = "#0A0A0F"
PANEL     = "#12121A"
SURFACE   = "#1A1A26"
BORDER    = "#2A2A3D"
ACCENT    = "#6C63FF"
ACCENT_H  = "#5A52E0"
TEXT      = "#F0F0FF"
SUBTLE    = "#8888AA"
DANGER    = "#EF4444"
DANGER_H  = "#DC2626"

def font_h1() -> ctk.CTkFont:
    return ctk.CTkFont("Segoe UI Semibold", 22, "bold")

def font_h2() -> ctk.CTkFont:
    return ctk.CTkFont("Segoe UI Semibold", 16, "bold")

def font_body() -> ctk.CTkFont:
    return ctk.CTkFont("Segoe UI", 13)

def font_small() -> ctk.CTkFont:
    return ctk.CTkFont("Segoe UI", 11)



class Label(ctk.CTkLabel):
    def __init__(self, master, text="", size="body", **kw):
        fonts  = {"h1": font_h1(), "h2": font_h2(), "body": font_body(), "small": font_small()}
        colors = {"h1": TEXT, "h2": TEXT, "body": TEXT, "small": SUBTLE}
        super().__init__(master, text=text,
                         font=fonts.get(size, font_body()),
                         text_color=colors.get(size, TEXT), **kw)


class PrimaryButton(ctk.CTkButton):
    def __init__(self, master, **kw):
        kw.setdefault("height", 38)
        kw.setdefault("font", font_body())
        super().__init__(master,
                         fg_color=ACCENT, hover_color=ACCENT_H,
                         text_color=TEXT, corner_radius=8,
                         **kw)


class SecondaryButton(ctk.CTkButton):
    def __init__(self, master, **kw):
        kw.setdefault("height", 38)
        kw.setdefault("font", font_body())
        super().__init__(master,
                         fg_color=SURFACE, hover_color=BORDER,
                         text_color=TEXT, corner_radius=8,
                         border_width=1, border_color=BORDER,
                         **kw)


class DangerButton(ctk.CTkButton):
    def __init__(self, master, **kw):
        kw.setdefault("height", 38)
        kw.setdefault("font", font_body())
        super().__init__(master,
                         fg_color=DANGER, hover_color=DANGER_H,
                         text_color=TEXT, corner_radius=8,
                         **kw)


class StyledEntry(ctk.CTkEntry):
    def __init__(self, master, **kw):
        kw.setdefault("height", 38)
        kw.setdefault("font", font_body())
        super().__init__(master,
                         fg_color=SURFACE, border_color=BORDER,
                         text_color=TEXT, placeholder_text_color=SUBTLE,
                         corner_radius=8,
                         **kw)


class Card(ctk.CTkFrame):
    """Elevated card with optional title header."""
    def __init__(self, master, title: str = "", **kw):
        super().__init__(master,
                         corner_radius=14,
                         fg_color=PANEL,
                         border_width=1,
                         border_color=BORDER, **kw)
        self.grid_columnconfigure(0, weight=1)

        if title:
            header = ctk.CTkFrame(self, fg_color="transparent")
            header.grid(row=0, column=0, sticky="ew", padx=20, pady=(18, 10))
            header.grid_columnconfigure(0, weight=1)
            ctk.CTkLabel(header, text=title, font=font_h2(), text_color=TEXT).grid(row=0, column=0, sticky="w")

            sep = ctk.CTkFrame(self, height=1, fg_color=BORDER, corner_radius=0)
            sep.grid(row=1, column=0, sticky="ew")

            self.body = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
            self.body.grid(row=2, column=0, sticky="nsew", padx=20, pady=16)
            self.body.grid_columnconfigure(0, weight=1)
            self.grid_rowconfigure(2, weight=1)
        else:
            self.body = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
            self.body.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
            self.body.grid_columnconfigure(0, weight=1)
            self.grid_rowconfigure(0, weight=1)


class AppShell(ctk.CTkFrame):
    """12-column grid shell."""
    def __init__(self, master, **kw):
        super().__init__(master, fg_color=BG, **kw)
        for c in range(12):
            self.grid_columnconfigure(c, weight=1)
        self.grid_rowconfigure(99, weight=1)
