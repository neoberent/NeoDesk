import customtkinter as ctk
import tkinter.messagebox as mbox

from Chatpage_Gui.design import (
    BG, PANEL, SURFACE, BORDER, ACCENT, ACCENT_H,
    TEXT, SUBTLE,
    font_h1, font_h2, font_body, font_small,
    PrimaryButton, SecondaryButton, Card,
)

try:
    from Chatpage_Gui.chat_window import ChatWindow
except Exception:
    ChatWindow = None

try:
    from NoteManager_Gui.note_manager import NotesWindow
except Exception:
    NotesWindow = None

try:
    from Dashboard.admin_window import AdminWindow
except Exception:
    AdminWindow = None


_MODULES = [
    {
        "key": "chat",
        "title": "KI-Chat",
        "subtitle": "Konversation mit dem integrierten KI-Assistenten",
        "icon": "💬",
        "action_label": "Chat öffnen",
    },
    {
        "key": "notes",
        "title": "Notizen",
        "subtitle": "Persönliche Notizen sicher speichern und verwalten",
        "icon": "📝",
        "action_label": "Notizen öffnen",
    },
    {
        "key": "admin",
        "title": "Administration",
        "subtitle": "Benutzerverwaltung und Systemeinstellungen",
        "icon": "⚙",
        "action_label": "Admin öffnen",
    },
]


class _ModuleCard(ctk.CTkFrame):
    """Single dashboard module card."""

    def __init__(self, master, data: dict, command, **kw):
        super().__init__(
            master,
            corner_radius=16,
            fg_color=PANEL,
            border_width=1,
            border_color=BORDER,
            **kw,
        )
        self.grid_columnconfigure(0, weight=1)

        icon_bg = ctk.CTkFrame(self, width=52, height=52,
                               corner_radius=14, fg_color=SURFACE)
        icon_bg.grid(row=0, column=0, sticky="w", padx=22, pady=(22, 10))
        icon_bg.grid_propagate(False)
        ctk.CTkLabel(icon_bg, text=data["icon"],
                     font=ctk.CTkFont(size=24)).place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(self, text=data["title"],
                     font=font_h2(), text_color=TEXT,
                     anchor="w").grid(row=1, column=0, sticky="ew", padx=22, pady=(0, 4))

        ctk.CTkLabel(self, text=data["subtitle"],
                     font=font_small(), text_color=SUBTLE,
                     anchor="w", wraplength=220).grid(
            row=2, column=0, sticky="ew", padx=22, pady=(0, 18))

        ctk.CTkFrame(self, height=1, fg_color=BORDER, corner_radius=0).grid(
            row=3, column=0, sticky="ew")

        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.grid(row=4, column=0, sticky="ew", padx=22, pady=14)
        PrimaryButton(btn_row, text=data["action_label"], command=command,
                      height=34).pack(side="left")

        self.bind("<Enter>", lambda e: self.configure(border_color=ACCENT))
        self.bind("<Leave>", lambda e: self.configure(border_color=BORDER))


class DashboardWindow(ctk.CTkToplevel):
    def __init__(self, master=None, username=None, role="User"):
        super().__init__(master)
        self.username = username or "Benutzer"
        self.role = role or "User"
        is_admin = self.role == "Admin"

        self.title("Dashboard – Neo")
        self.geometry("1100x700")
        self.minsize(860, 560)
        self.configure(fg_color=BG)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        navbar = ctk.CTkFrame(self, fg_color=PANEL,
                              border_width=0, corner_radius=0, height=60)
        navbar.grid(row=0, column=0, sticky="ew")
        navbar.grid_propagate(False)
        navbar.grid_columnconfigure(1, weight=1)

        brand = ctk.CTkFrame(navbar, fg_color="transparent")
        brand.grid(row=0, column=0, sticky="w", padx=28, pady=0)
        brand.grid_rowconfigure(0, weight=1)

        dot = ctk.CTkFrame(brand, width=8, height=8,
                           corner_radius=4, fg_color=ACCENT)
        dot.grid(row=0, column=0)
        ctk.CTkLabel(brand, text="  NEO", font=font_h2(),
                     text_color=TEXT).grid(row=0, column=1)

        ctk.CTkLabel(navbar, text=f"Willkommen, {self.username}",
                     font=font_body(), text_color=SUBTLE).grid(
            row=0, column=1, sticky="e", padx=28)

        body = ctk.CTkFrame(self, fg_color=BG)
        body.grid(row=1, column=0, sticky="nsew")
        body.grid_columnconfigure((0, 1, 2), weight=1)
        body.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(body, text="Module", font=font_h1(),
                     text_color=TEXT, anchor="w").grid(
            row=0, column=0, columnspan=3, sticky="w", padx=32, pady=(28, 16))

        visible_modules = _MODULES if is_admin else [m for m in _MODULES if m["key"] != "admin"]
        actions_map = {"chat": self.open_chat, "notes": self.open_notes, "admin": self.open_admin}
        for i, mod in enumerate(visible_modules):
            card = _ModuleCard(body, mod, actions_map[mod["key"]])
            card.grid(row=1, column=i, sticky="nsew", padx=16, pady=(0, 28))

        statusbar = ctk.CTkFrame(self, fg_color=PANEL,
                                 border_width=0, corner_radius=0, height=30)
        statusbar.grid(row=2, column=0, sticky="ew")
        statusbar.grid_propagate(False)
        ctk.CTkLabel(statusbar, text="Neo Workspace  ·  Alle Systeme bereit",
                     font=font_small(), text_color=SUBTLE).place(x=28, rely=0.5, anchor="w")


    def open_chat(self):
        if ChatWindow is None:
            mbox.showinfo("Hinweis", "ChatWindow nicht verfügbar.")
            return
        try:
            ChatWindow(self)
        except TypeError:
            try:
                ChatWindow(self, self.username)
            except Exception as e:
                mbox.showerror("Fehler", f"Chat konnte nicht geöffnet werden:\n{e}")

    def open_notes(self):
        if NotesWindow is None:
            mbox.showinfo("Hinweis", "NotesWindow nicht verfügbar.")
            return
        NotesWindow(self, self.username)

    def open_admin(self):
        if self.role != "Admin":
            mbox.showerror("Zugriff verweigert", "Nur Administratoren können diesen Bereich öffnen.")
            return
        if AdminWindow is None:
            mbox.showinfo("Hinweis", "AdminWindow nicht verfügbar.")
            return
        AdminWindow(self)
