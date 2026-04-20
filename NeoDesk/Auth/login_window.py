# Auth/login_window.py
import customtkinter as ctk
import tkinter.messagebox as mbox
import bcrypt

try:
    from base_ui import BaseWindow
except Exception:
    BaseWindow = ctk.CTk

from Chatpage_Gui.utils import init_ctk, apply_theme, center_window
from Chatpage_Gui.design import (
    BG, PANEL, SURFACE, BORDER, ACCENT, ACCENT_H,
    TEXT, SUBTLE, DANGER,
    font_h1, font_h2, font_body, font_small,
    PrimaryButton, StyledEntry
)
from settings import get_theme_mode
from .user_manager import load_users, save_users, check_login, ensure_admin
from Dashboard.dashboard_window import DashboardWindow


class PasswordRulesMixin:
    @staticmethod
    def validate_password(p: str):
        letters = sum(1 for c in p if c.isalpha())
        has_digit = any(c.isdigit() for c in p)
        if letters < 6 or not has_digit:
            return False, "Das Passwort muss mindestens 6 Buchstaben und eine Zahl enthalten."
        return True, ""


class LoginWindow(PasswordRulesMixin, BaseWindow):
    PANEL_W = 460
    PANEL_H = 500

    def __init__(self):
        super().__init__()
        init_ctk()
        apply_theme("Dark")

        self.title("Neo Login")
        self.geometry("1000x640")
        self.minsize(720, 480)
        self.configure(fg_color=BG)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ── Background canvas with subtle grid lines ──────────────────────────
        bg = ctk.CTkFrame(self, fg_color=BG)
        bg.grid(row=0, column=0, sticky="nsew")
        bg.grid_columnconfigure(0, weight=1)
        bg.grid_rowconfigure(0, weight=1)

        # ── Centered glass panel ──────────────────────────────────────────────
        self.panel = ctk.CTkFrame(
            bg,
            corner_radius=20,
            fg_color=PANEL,
            border_width=1,
            border_color=BORDER,
            width=self.PANEL_W,
            height=self.PANEL_H,
        )
        self.panel.place(relx=0.5, rely=0.5, anchor="center")
        self.panel.grid_propagate(False)
        self.panel.grid_columnconfigure(0, weight=1)
        self.panel.grid_rowconfigure(2, weight=1)

        self.bind("<Configure>",
                  lambda e: self.panel.place(relx=0.5, rely=0.5, anchor="center"))

        # ── Logo / brand area ─────────────────────────────────────────────────
        brand = ctk.CTkFrame(self.panel, fg_color="transparent")
        brand.grid(row=0, column=0, sticky="ew", padx=32, pady=(32, 4))
        brand.grid_columnconfigure(0, weight=1)

        # Accent dot + name
        dot = ctk.CTkFrame(brand, width=10, height=10,
                           corner_radius=5, fg_color=ACCENT)
        dot.grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(brand, text="  NEO", font=font_h1(),
                     text_color=TEXT).grid(row=0, column=0, sticky="w", padx=16)
        ctk.CTkLabel(brand, text="Sicherer Arbeitsbereich",
                     font=font_small(), text_color=SUBTLE).grid(
            row=1, column=0, sticky="w", pady=(2, 0))

        # ── Segmented tab ─────────────────────────────────────────────────────
        self._tabs = ctk.CTkSegmentedButton(
            self.panel,
            values=["Anmelden", "Registrieren"],
            command=self._switch_tab,
            fg_color=SURFACE,
            selected_color=ACCENT,
            selected_hover_color=ACCENT_H,
            unselected_color=SURFACE,
            unselected_hover_color=BORDER,
            text_color=TEXT,
            font=font_body(),
            corner_radius=8,
            height=36,
        )
        self._tabs.grid(row=1, column=0, sticky="ew", padx=32, pady=(20, 0))

        # ── Form frames ───────────────────────────────────────────────────────
        self._login_frame    = self._build_login(self.panel)
        self._register_frame = self._build_register(self.panel)

        self._tabs.set("Anmelden")
        self._login_frame.tkraise()
        ensure_admin()

    # ── builders ──────────────────────────────────────────────────────────────

    def _build_login(self, parent):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.grid(row=2, column=0, sticky="nsew", padx=32, pady=20)
        f.grid_columnconfigure(0, weight=1)

        self.user   = ctk.StringVar()
        self.passwd = ctk.StringVar()

        ctk.CTkLabel(f, text="Benutzername", font=font_small(),
                     text_color=SUBTLE).grid(row=0, column=0, sticky="w", pady=(0, 4))
        StyledEntry(f, textvariable=self.user,
                    placeholder_text="Ihr Benutzername").grid(
            row=1, column=0, sticky="ew", pady=(0, 14))

        ctk.CTkLabel(f, text="Passwort", font=font_small(),
                     text_color=SUBTLE).grid(row=2, column=0, sticky="w", pady=(0, 4))
        StyledEntry(f, textvariable=self.passwd,
                    placeholder_text="••••••••", show="•").grid(
            row=3, column=0, sticky="ew", pady=(0, 24))

        PrimaryButton(f, text="Anmelden →", command=self.login).grid(
            row=4, column=0, sticky="ew")

        return f

    def _build_register(self, parent):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.grid(row=2, column=0, sticky="nsew", padx=32, pady=20)
        f.grid_columnconfigure(0, weight=1)

        self.reg_user = ctk.StringVar()
        self.reg_pass = ctk.StringVar()

        ctk.CTkLabel(f, text="Benutzername wählen", font=font_small(),
                     text_color=SUBTLE).grid(row=0, column=0, sticky="w", pady=(0, 4))
        StyledEntry(f, textvariable=self.reg_user,
                    placeholder_text="Gewünschter Benutzername").grid(
            row=1, column=0, sticky="ew", pady=(0, 14))

        ctk.CTkLabel(f, text="Passwort", font=font_small(),
                     text_color=SUBTLE).grid(row=2, column=0, sticky="w", pady=(0, 4))
        StyledEntry(f, textvariable=self.reg_pass,
                    placeholder_text="mind. 6 Buchstaben + 1 Zahl", show="•").grid(
            row=3, column=0, sticky="ew", pady=(0, 6))

        ctk.CTkLabel(f, text="Mindestens 6 Buchstaben und eine Zahl.",
                     font=font_small(), text_color=SUBTLE).grid(
            row=4, column=0, sticky="w", pady=(0, 20))

        PrimaryButton(f, text="Account erstellen →", command=self.register).grid(
            row=5, column=0, sticky="ew")

        return f

    # ── tab switch ────────────────────────────────────────────────────────────

    def _switch_tab(self, value):
        (self._login_frame if value == "Anmelden" else self._register_frame).tkraise()

    # ── actions (logic unchanged) ─────────────────────────────────────────────

    def login(self):
        u = self.user.get().strip()
        p = self.passwd.get().strip()
        if not u or not p:
            mbox.showerror("Fehler", "Bitte Benutzername und Passwort eingeben.")
            return
        ok, role = check_login(u, p)
        if not ok:
            mbox.showerror("Fehler", "Falsche Anmeldedaten.")
            return
        self.withdraw()
        DashboardWindow(self, username=u, role=role).wait_window()
        self.deiconify()

    def register(self):
        u = self.reg_user.get().strip()
        p = self.reg_pass.get().strip()
        if not u or not p:
            mbox.showerror("Fehler", "Bitte Benutzername und Passwort eingeben.")
            return
        ok, msg = self.validate_password(p)
        if not ok:
            mbox.showerror("Fehler", msg)
            return
        users = load_users()
        if u in users:
            mbox.showerror("Fehler", "Dieser Benutzername ist bereits vergeben.")
            return
        hashed = bcrypt.hashpw(p.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        users[u] = {"password": hashed, "role": "User"}
        save_users(users)
        mbox.showinfo("Erfolg", "Account erstellt! Bitte jetzt anmelden.")
        self._tabs.set("Anmelden")
        self._login_frame.tkraise()
