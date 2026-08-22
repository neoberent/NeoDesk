import customtkinter as ctk
import tkinter as tk
import tkinter.messagebox as mbox
import bcrypt
import logging

from base_ui import BaseToplevel
from json_store import JsonStore
from config import WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_MINSIZE
from log_setup import get_logger
from Chatpage_Gui.design import (
    BG, PANEL, SURFACE, BORDER, ACCENT, ACCENT_H,
    TEXT, SUBTLE, DANGER, DANGER_H,
    font_h1, font_h2, font_body, font_small,
    PrimaryButton, SecondaryButton, DangerButton, StyledEntry,
)

logger = get_logger(__name__)


class AdminWindow(BaseToplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Administration – Benutzerverwaltung")
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        try:
            self.minsize(*WINDOW_MINSIZE)
        except Exception:
            pass

        self.configure(fg_color=BG)
        self.columns = 3
        self.store = JsonStore()
        self._users_cache = {}
        self._filter_text = tk.StringVar(value="")
        self._selected_username = None

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        topbar = ctk.CTkFrame(self, fg_color=PANEL,
                              border_width=0, corner_radius=0, height=60)
        topbar.grid(row=0, column=0, sticky="ew")
        topbar.grid_propagate(False)
        topbar.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(topbar, text="Benutzerverwaltung",
                     font=font_h2(), text_color=TEXT).grid(
            row=0, column=0, sticky="w", padx=24, pady=0)

        right_bar = ctk.CTkFrame(topbar, fg_color="transparent")
        right_bar.grid(row=0, column=1, sticky="e", padx=20)
        right_bar.grid_columnconfigure(0, weight=1)

        self.filter_entry = StyledEntry(right_bar,
                                        textvariable=self._filter_text,
                                        placeholder_text="🔍  Suche nach Name oder Rolle …",
                                        width=260, height=34)
        self.filter_entry.grid(row=0, column=0, padx=(0, 12))
        self.filter_entry.bind("<KeyRelease>", lambda e: self._refresh_grid())

        PrimaryButton(right_bar, text="+ Benutzer hinzufügen",
                      command=self._add_user_dialog, height=34).grid(row=0, column=1)

        self.scroll = ctk.CTkScrollableFrame(self, fg_color=BG)
        self.scroll.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)

        self.grid_frame = ctk.CTkFrame(self.scroll, fg_color="transparent")
        self.grid_frame.grid(row=0, column=0, sticky="nsew", padx=16, pady=16)

        self._menu = tk.Menu(self, tearoff=0,
                             bg="#1A1A26", fg=TEXT,
                             activebackground=ACCENT, activeforeground=TEXT)
        self._menu.add_command(label="Rolle ändern", command=self._change_role_selected)
        self._menu.add_command(label="Entfernen",    command=self._remove_selected)

        self.grid_frame.bind("<Button-3>", self._open_context_menu)
        self.bind("<Configure>", self._on_resize)

        self._load()
        self._on_resize(None)


    def _load(self):
        try:
            self._users_cache = self.store.get_users() or {}
        except Exception as e:
            logger.exception(e)
            mbox.showerror("Fehler", f"Benutzer konnten nicht geladen werden:\n{e}")
            self._users_cache = {}
        self._refresh_grid()

    def _upsert_user(self, username: str, password_hash: str, role: str):
        try:
            self.store.upsert_user(username, password_hash, role)
            self._users_cache[username] = {
                "username": username, "password": password_hash, "role": role or "User"
            }
        except Exception as e:
            logger.exception(e)
            mbox.showerror("Fehler", f"Speichern fehlgeschlagen:\n{e}")

    def _delete_user(self, username: str) -> bool:
        try:
            ok = self.store.delete_user(username)
            if ok and username in self._users_cache:
                del self._users_cache[username]
            return ok
        except Exception as e:
            logger.exception(e)
            mbox.showerror("Fehler", f"Löschen fehlgeschlagen:\n{e}")
            return False


    def _configure_grid_columns(self, cols: int):
        for i in range(max(1, cols)):
            self.grid_frame.grid_columnconfigure(i, weight=1, uniform="cards")
        self.columns = cols

    def _refresh_grid(self):
        for w in self.grid_frame.winfo_children():
            w.destroy()

        q = (self._filter_text.get() or "").strip().lower()
        items = [
            (uname, data.get("role", "User"))
            for uname, data in (self._users_cache or {}).items()
            if not q or q in uname.lower() or q in str(data.get("role", "")).lower()
        ]
        items.sort(key=lambda t: (t[1].lower(), t[0].lower()))

        if not items:
            ctk.CTkLabel(self.grid_frame, text="Keine Benutzer gefunden.",
                         font=font_body(), text_color=SUBTLE).grid(
                row=0, column=0, padx=24, pady=32)
            return

        for idx, (uname, role) in enumerate(items):
            r, c = divmod(idx, self.columns)
            card = self._make_user_card(uname, role)
            card.grid(row=r, column=c, padx=10, pady=10, sticky="nsew")

    def _make_user_card(self, uname: str, role: str) -> ctk.CTkFrame:
        card = ctk.CTkFrame(self.grid_frame, corner_radius=14,
                            fg_color=PANEL, border_width=1, border_color=BORDER)
        card.grid_columnconfigure(0, weight=1)

        avatar = ctk.CTkFrame(card, width=44, height=44,
                              corner_radius=22, fg_color=SURFACE)
        avatar.grid(row=0, column=0, sticky="w", padx=16, pady=(16, 8))
        avatar.grid_propagate(False)
        initials = uname[:2].upper()
        ctk.CTkLabel(avatar, text=initials,
                     font=ctk.CTkFont("Segoe UI Semibold", 14, "bold"),
                     text_color=ACCENT).place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(card, text=uname,
                     font=font_h2(), text_color=TEXT,
                     anchor="w").grid(row=1, column=0, sticky="ew", padx=16, pady=(0, 2))

        badge_color = ACCENT if role == "Admin" else SURFACE
        badge = ctk.CTkFrame(card, corner_radius=6,
                             fg_color=badge_color, height=22)
        badge.grid(row=2, column=0, sticky="w", padx=16, pady=(0, 14))
        ctk.CTkLabel(badge, text=f"  {role}  ",
                     font=font_small(), text_color=TEXT).pack()

        ctk.CTkFrame(card, height=1, fg_color=BORDER, corner_radius=0).grid(
            row=3, column=0, sticky="ew")

        btn_row = ctk.CTkFrame(card, fg_color="transparent")
        btn_row.grid(row=4, column=0, sticky="ew", padx=12, pady=12)
        btn_row.grid_columnconfigure((0, 1), weight=1)

        SecondaryButton(btn_row, text="Rolle ändern", height=32,
                        command=lambda u=uname: self._change_role(u)).grid(
            row=0, column=0, padx=(0, 6), sticky="ew")
        DangerButton(btn_row, text="Entfernen", height=32,
                     command=lambda u=uname: self._remove(u)).grid(
            row=0, column=1, padx=(6, 0), sticky="ew")

        for w in [card, avatar]:
            w.bind("<Button-3>", lambda e, u=uname: self._set_selected(u))

        card.bind("<Enter>", lambda e: card.configure(border_color=ACCENT))
        card.bind("<Leave>", lambda e: card.configure(border_color=BORDER))

        return card

    def _set_selected(self, username: str):
        self._selected_username = username

    def _open_context_menu(self, event):
        try:
            self._menu.tk_popup(event.x_root, event.y_root)
        finally:
            self._menu.grab_release()


    def _add_user_dialog(self):
        win = ctk.CTkToplevel(self)
        win.title("Benutzer hinzufügen")
        win.geometry("400x260")
        win.resizable(False, False)
        win.configure(fg_color=BG)
        win.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(win, text="Neuen Benutzer anlegen",
                     font=font_h2(), text_color=TEXT).grid(
            row=0, column=0, sticky="w", padx=28, pady=(24, 16))

        name_var = tk.StringVar()
        StyledEntry(win, textvariable=name_var,
                    placeholder_text="Benutzername").grid(
            row=1, column=0, sticky="ew", padx=28, pady=(0, 10))

        role_var = tk.StringVar(value="User")
        ctk.CTkComboBox(win, values=["User", "Admin"], variable=role_var,
                        state="readonly",
                        fg_color=SURFACE, border_color=BORDER,
                        text_color=TEXT, button_color=ACCENT,
                        dropdown_fg_color=PANEL, dropdown_text_color=TEXT,
                        font=font_body(), height=38).grid(
            row=2, column=0, sticky="ew", padx=28, pady=(0, 20))

        def on_ok():
            uname = (name_var.get() or "").strip()
            role  = (role_var.get() or "User").strip() or "User"
            if not uname:
                mbox.showerror("Fehler", "Benutzername darf nicht leer sein.")
                return
            if uname in self._users_cache:
                mbox.showerror("Fehler", "Benutzer existiert bereits.")
                return
            hashed = bcrypt.hashpw("admin".encode(), bcrypt.gensalt()).decode()
            self._upsert_user(uname, hashed, role)
            self._refresh_grid()
            win.destroy()

        btn_row = ctk.CTkFrame(win, fg_color="transparent")
        btn_row.grid(row=3, column=0, pady=0, padx=28, sticky="ew")
        btn_row.grid_columnconfigure((0, 1), weight=1)

        SecondaryButton(btn_row, text="Abbrechen",
                        command=win.destroy).grid(row=0, column=0, padx=(0, 6), sticky="ew")
        PrimaryButton(btn_row, text="Erstellen",
                      command=on_ok).grid(row=0, column=1, padx=(6, 0), sticky="ew")

    def _change_role_selected(self):
        if self._selected_username:
            self._change_role(self._selected_username)

    def _change_role(self, username: str):
        if username not in self._users_cache:
            return
        current  = self._users_cache[username].get("role", "User")
        new_role = "Admin" if current != "Admin" else "User"
        pwd_hash = self._users_cache[username].get("password") or ""
        self._upsert_user(username, pwd_hash, new_role)
        self._refresh_grid()

    def _remove_selected(self):
        if self._selected_username:
            self._remove(self._selected_username)

    def _remove(self, username: str):
        if username not in self._users_cache:
            return
        if not mbox.askyesno("Bestätigen", f'Benutzer „{username}" wirklich entfernen?'):
            return
        if self._delete_user(username):
            self._refresh_grid()
        else:
            mbox.showwarning("Hinweis", f'Benutzer „{username}" nicht gefunden.')


    def _on_resize(self, _event):
        width = self.winfo_width()
        cols = 1 if width <= 540 else (2 if width <= 860 else 3)
        if cols != self.columns:
            self._configure_grid_columns(cols)
            self._refresh_grid()
