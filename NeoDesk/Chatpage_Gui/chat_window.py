import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import logging

from base_ui import BaseToplevel
from Chatpage_Gui.database import Database
from Chatpage_Gui.utils import center_window, init_ctk, apply_theme
from Chatpage_Gui.ai_client import AIClient
from Chatpage_Gui.design import (
    BG, PANEL, SURFACE, BORDER, ACCENT, ACCENT_H,
    TEXT, SUBTLE,
    font_h2, font_body, font_small,
    PrimaryButton, StyledEntry,
)
from settings import get_theme_mode
from config import WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_MINSIZE
from log_setup import get_logger

logger = get_logger(__name__)

_root_log = logging.getLogger()
if not _root_log.handlers:
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")


class ChatWindow(BaseToplevel):
    def __init__(self, master=None, username: str = "User",
                 db: Database | None = None, **kwargs):
        super().__init__(master, **kwargs)

        init_ctk()
        apply_theme(get_theme_mode())
        self.title("KI-Chat – Neo")
        self.minsize(*WINDOW_MINSIZE)
        center_window(self, WINDOW_WIDTH, WINDOW_HEIGHT)
        self.configure(fg_color=BG)

        self.username = username
        self.db = db if db is not None else Database()
        self.ai = AIClient()

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        root = ctk.CTkFrame(self, fg_color=BG)
        root.grid(row=0, column=0, sticky="nsew")
        root.grid_columnconfigure(1, weight=1)
        root.grid_rowconfigure(0, weight=1)

        sidebar = ctk.CTkFrame(root, fg_color=PANEL,
                               border_width=0, corner_radius=0, width=220)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)
        sidebar.grid_rowconfigure(3, weight=1)
        sidebar.grid_columnconfigure(0, weight=1)

        brand = ctk.CTkFrame(sidebar, fg_color="transparent")
        brand.grid(row=0, column=0, sticky="ew", padx=20, pady=(24, 0))
        dot = ctk.CTkFrame(brand, width=8, height=8,
                           corner_radius=4, fg_color=ACCENT)
        dot.grid(row=0, column=0)
        ctk.CTkLabel(brand, text="  NEO Chat",
                     font=font_h2(), text_color=TEXT).grid(row=0, column=1)

        ctk.CTkFrame(sidebar, height=1, fg_color=BORDER, corner_radius=0).grid(
            row=1, column=0, sticky="ew", pady=16)

        user_frame = ctk.CTkFrame(sidebar, fg_color=SURFACE, corner_radius=10)
        user_frame.grid(row=2, column=0, sticky="ew", padx=16, pady=(0, 16))
        user_frame.grid_columnconfigure(1, weight=1)

        avatar = ctk.CTkFrame(user_frame, width=36, height=36,
                              corner_radius=18, fg_color=ACCENT)
        avatar.grid(row=0, column=0, padx=(12, 8), pady=10)
        avatar.grid_propagate(False)
        ctk.CTkLabel(avatar, text=self.username[:1].upper(),
                     font=ctk.CTkFont("Segoe UI Semibold", 14, "bold"),
                     text_color=TEXT).place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(user_frame, text=self.username,
                     font=font_body(), text_color=TEXT,
                     anchor="w").grid(row=0, column=1, sticky="w")
        ctk.CTkLabel(user_frame, text="Online",
                     font=font_small(), text_color=ACCENT).grid(
            row=1, column=1, sticky="w")

        ctk.CTkLabel(sidebar, text="KI-gestützte Konversation",
                     font=font_small(), text_color=SUBTLE,
                     wraplength=180).grid(
            row=3, column=0, padx=20, pady=0, sticky="n")

        main = ctk.CTkFrame(root, fg_color=BG)
        main.grid(row=0, column=1, sticky="nsew")
        main.grid_rowconfigure(1, weight=1)
        main.grid_columnconfigure(0, weight=1)

        header = ctk.CTkFrame(main, fg_color=PANEL,
                              corner_radius=0, border_width=0, height=52)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_propagate(False)
        ctk.CTkLabel(header, text="Neues Gespräch",
                     font=font_h2(), text_color=TEXT).place(x=24, rely=0.5, anchor="w")

        self.chat_box = ctk.CTkTextbox(
            main, wrap="word",
            fg_color=BG, text_color=TEXT,
            font=font_body(),
            border_width=0,
            scrollbar_button_color=SURFACE,
            scrollbar_button_hover_color=BORDER,
        )
        self.chat_box.grid(row=1, column=0, sticky="nsew", padx=24, pady=16)
        self.chat_box.configure(state="disabled")

        input_bar = ctk.CTkFrame(main, fg_color=PANEL,
                                 corner_radius=0, border_width=0, height=68)
        input_bar.grid(row=2, column=0, sticky="ew")
        input_bar.grid_propagate(False)
        input_bar.grid_columnconfigure(0, weight=1)

        inner = ctk.CTkFrame(input_bar, fg_color="transparent")
        inner.place(relx=0.5, rely=0.5, anchor="center",
                    relwidth=0.98, height=44)
        inner.grid_columnconfigure(0, weight=1)

        self.entry = StyledEntry(inner, placeholder_text="Nachricht eingeben …",
                                 height=44)
        self.entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.entry.bind("<Return>", lambda e: self.send())

        PrimaryButton(inner, text="Senden ↵", command=self.send,
                      width=100, height=44).grid(row=0, column=1)

        self._append_message("KI", "Hallo! Wie kann ich helfen?")
        self._load_history()
        self.protocol("WM_DELETE_WINDOW", self.destroy)


    def _append_message(self, author: str, text: str):
        self.chat_box.configure(state="normal")
        try:
            prefix = f"{'Du' if author == self.username else '🤖 KI'}"
            self.chat_box.insert("end", f"\n{prefix}\n", "author")
            self.chat_box.insert("end", f"{text}\n\n", "message")
            self.chat_box.see("end")
        finally:
            self.chat_box.configure(state="disabled")


    def send(self):
        try:
            text = (self.entry.get() or "").strip()
            if not text:
                return
            self._append_message(self.username, text)
            self.entry.delete(0, "end")

            try:
                self.db.save_message(self.username, {"role": "user", "content": text})
            except Exception:
                logger.exception("Konnte Nutzernachricht nicht speichern")

            try:
                response = self.ai.ask(text)
            except Exception as e:
                logger.exception("AIClient.ask fehlgeschlagen")
                messagebox.showerror("Fehler", f"KI-Fehler: {e}")
                return

            if not response:
                messagebox.showerror("Fehler", "KI konnte nicht antworten.")
                return

            try:
                self.db.save_message(self.username, {"role": "assistant", "content": response})
            except Exception:
                logger.exception("Konnte KI-Antwort nicht speichern")

            self._append_message("KI", response)
        except Exception:
            logger.exception("Unhandled exception in ChatWindow.send")

    def destroy(self):
        try:
            self.db = None
        except Exception:
            pass
        super().destroy()

    def _load_history(self):
        try:
            for m in self.db.get_messages(self.username):
                author  = "KI" if m.get("role") == "assistant" else (m.get("user") or self.username)
                content = m.get("content", "")
                if content:
                    self._append_message(author, content)
        except Exception as e:
            logger.exception("Verlauf konnte nicht geladen werden: %s", e)
