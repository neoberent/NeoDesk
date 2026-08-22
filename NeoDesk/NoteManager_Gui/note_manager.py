import customtkinter as ctk
from base_ui import BaseToplevel
import tkinter as tk
from tkinter import messagebox
import logging
from json_store import JsonStore
from log_setup import get_logger
from Chatpage_Gui.design import (
    BG, PANEL, SURFACE, BORDER, ACCENT, ACCENT_H,
    TEXT, SUBTLE, DANGER, DANGER_H,
    font_h1, font_h2, font_body, font_small,
    PrimaryButton, SecondaryButton, DangerButton, StyledEntry,
)

logger = get_logger(__name__)

_root_log = logging.getLogger()
if not _root_log.handlers:
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

DEBOUNCE_MS = 220
PREVIEW_MAX = 56


class NotesWindow(BaseToplevel):
    def __init__(self, master, username: str):
        super().__init__(master)
        self.username = username
        self.title("Notizen – Neo")
        self.minsize(980, 640)
        self.resizable(True, True)
        self.configure(fg_color=BG)

        self.store = JsonStore()
        self.selected_note_id = None
        self._id_map = []
        self._dirty = False
        self._debounce_after_id = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        navbar = ctk.CTkFrame(self, fg_color=PANEL,
                              border_width=0, corner_radius=0, height=56)
        navbar.grid(row=0, column=0, sticky="ew")
        navbar.grid_propagate(False)
        navbar.grid_columnconfigure(1, weight=1)

        brand = ctk.CTkFrame(navbar, fg_color="transparent")
        brand.grid(row=0, column=0, sticky="w", padx=24)
        dot = ctk.CTkFrame(brand, width=8, height=8,
                           corner_radius=4, fg_color=ACCENT)
        dot.grid(row=0, column=0)
        ctk.CTkLabel(brand, text=f"  Notizen – {self.username}",
                     font=font_h2(), text_color=TEXT).grid(row=0, column=1)

        body = ctk.CTkFrame(self, fg_color=BG)
        body.grid(row=1, column=0, sticky="nsew")
        body.grid_columnconfigure(0, weight=0, minsize=280)
        body.grid_columnconfigure(1, weight=1)
        body.grid_rowconfigure(0, weight=1)

        sidebar = ctk.CTkFrame(body, fg_color=PANEL,
                               border_width=0, corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_rowconfigure(2, weight=1)
        sidebar.grid_columnconfigure(0, weight=1)

        search_wrap = ctk.CTkFrame(sidebar, fg_color="transparent")
        search_wrap.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 8))
        search_wrap.grid_columnconfigure(0, weight=1)

        self.search_var = tk.StringVar()
        StyledEntry(search_wrap, textvariable=self.search_var,
                    placeholder_text="🔍  Suche …", height=36).grid(
            row=0, column=0, sticky="ew")
        self.search_var.trace_add("write", self._on_search_change)

        self.lbl_count = ctk.CTkLabel(sidebar, text="0 Notizen",
                                       font=font_small(), text_color=SUBTLE,
                                       anchor="w")
        self.lbl_count.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 8))

        self._list_frame = ctk.CTkScrollableFrame(
            sidebar, fg_color="transparent",
            scrollbar_button_color=SURFACE,
            scrollbar_button_hover_color=BORDER,
        )
        self._list_frame.grid(row=2, column=0, sticky="nsew", padx=8, pady=(0, 8))
        self._list_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkFrame(sidebar, height=1, fg_color=BORDER, corner_radius=0).grid(
            row=3, column=0, sticky="ew")
        PrimaryButton(sidebar, text="+ Neue Notiz",
                      command=self._new, height=38).grid(
            row=4, column=0, sticky="ew", padx=16, pady=12)

        self._menu = tk.Menu(self, tearoff=0,
                             bg=PANEL, fg=TEXT,
                             activebackground=ACCENT, activeforeground=TEXT)
        self._menu.add_command(label="Öffnen",      command=self._open_selected)
        self._menu.add_separator()
        self._menu.add_command(label="Duplizieren", command=self._duplicate_selected)
        self._menu.add_command(label="Löschen",     command=self._delete)

        right = ctk.CTkFrame(body, fg_color=BG)
        right.grid(row=0, column=1, sticky="nsew")
        right.grid_columnconfigure(0, weight=1)
        right.grid_rowconfigure(2, weight=1)

        toolbar = ctk.CTkFrame(right, fg_color=SURFACE,
                               border_width=0, corner_radius=0, height=52)
        toolbar.grid(row=0, column=0, sticky="ew")
        toolbar.grid_propagate(False)

        btn_wrap = ctk.CTkFrame(toolbar, fg_color="transparent")
        btn_wrap.place(relx=0, rely=0.5, anchor="w", x=20)

        self.btn_save = SecondaryButton(btn_wrap, text="💾  Speichern (Ctrl+S)",
                                        command=self._save, height=34)
        self.btn_save.grid(row=0, column=0, padx=(0, 8))

        DangerButton(btn_wrap, text="🗑  Löschen",
                     command=self._delete, height=34).grid(row=0, column=1)

        self.title_var = tk.StringVar()
        self.title_var.trace_add("write", self._on_edit_changed)
        ctk.CTkEntry(right,
                     textvariable=self.title_var,
                     placeholder_text="Titel der Notiz …",
                     fg_color=BG, border_color=BORDER,
                     text_color=TEXT, placeholder_text_color=SUBTLE,
                     corner_radius=0, height=44,
                     font=ctk.CTkFont("Segoe UI Semibold", 15, "bold")).grid(
            row=1, column=0, sticky="ew", padx=0, pady=0)

        self.content_box = ctk.CTkTextbox(
            right, wrap="word",
            fg_color=BG, text_color=TEXT,
            font=font_body(),
            border_width=0,
            scrollbar_button_color=SURFACE,
            scrollbar_button_hover_color=BORDER,
        )
        self.content_box.grid(row=2, column=0, sticky="nsew",
                               padx=24, pady=(12, 0))
        self.content_box.bind("<<Modified>>", self._on_text_modified)

        statusbar = ctk.CTkFrame(right, fg_color=PANEL,
                                  corner_radius=0, height=28)
        statusbar.grid(row=3, column=0, sticky="ew")
        statusbar.grid_propagate(False)
        statusbar.grid_columnconfigure(0, weight=1)
        self.lbl_status = ctk.CTkLabel(statusbar, text="Bereit",
                                        font=font_small(), text_color=SUBTLE)
        self.lbl_status.place(x=24, rely=0.5, anchor="w")
        self.lbl_wc = ctk.CTkLabel(statusbar, text="0 Wörter",
                                    font=font_small(), text_color=SUBTLE)
        self.lbl_wc.place(relx=1, x=-24, rely=0.5, anchor="e")

        self.bind("<Control-n>", lambda e: self._new())
        self.bind("<Control-s>", lambda e: self._save())
        self.bind("<Control-f>", lambda e: self._focus_search())
        self.bind("<Delete>",    lambda e: self._delete())

        self._refresh_list()


    def _refresh_list(self):
        for w in self._list_frame.winfo_children():
            w.destroy()
        self._id_map.clear()

        notes = self._list_notes()
        self._set_count(len(notes))

        for i, n in enumerate(notes):
            preview = n["combined"].split("\n", 1)[0][:PREVIEW_MAX] or f"Notiz {n['id']}"
            self._make_note_row(i, n["id"], preview)

    def _make_note_row(self, idx: int, note_id: int, preview: str):
        selected = (note_id == self.selected_note_id)
        row = ctk.CTkFrame(
            self._list_frame,
            corner_radius=8,
            fg_color=SURFACE if selected else "transparent",
            height=44,
        )
        row.grid(row=idx, column=0, sticky="ew", pady=2, padx=4)
        row.grid_columnconfigure(0, weight=1)
        row.grid_propagate(False)

        lbl = ctk.CTkLabel(row, text=preview, font=font_body(),
                           text_color=TEXT if selected else SUBTLE,
                           anchor="w", wraplength=220)
        lbl.place(x=12, rely=0.5, anchor="w", relwidth=0.85)

        self._id_map.append(note_id)

        def select(e, nid=note_id):
            self._load_note(nid)
            self._refresh_list()

        def on_rmb(e, nid=note_id):
            self._set_selected_note(nid)
            self._open_context_menu(e)

        for widget in (row, lbl):
            widget.bind("<Button-1>", select)
            widget.bind("<Button-3>", on_rmb)

        def on_enter(e, r=row, nid=note_id):
            if nid != self.selected_note_id:
                r.configure(fg_color=BORDER)
        def on_leave(e, r=row, nid=note_id):
            if nid != self.selected_note_id:
                r.configure(fg_color="transparent")

        for widget in (row, lbl):
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)

    def _set_selected_note(self, note_id):
        self.selected_note_id = note_id

    def _open_context_menu(self, event):
        try:
            self._menu.tk_popup(event.x_root, event.y_root)
        finally:
            self._menu.grab_release()


    def _on_search_change(self, *_):
        self._debounce(self._refresh_list)

    def _list_notes(self):
        q = (self.search_var.get() or "").strip().lower()
        try:
            all_notes = self.store.list_notes(owner=self.username) or []
        except Exception:
            logger.exception("list_notes failed")
            return []
        clean = []
        for n in all_notes:
            nid      = n.get("id")
            combined = n.get("combined", "")
            if q and q not in combined.lower():
                continue
            if nid is not None:
                clean.append({"id": nid, "combined": combined})
        return clean


    def _open_selected(self):
        if self.selected_note_id is not None:
            self._load_note(self.selected_note_id)

    def _load_note(self, note_id: int):
        self.selected_note_id = note_id
        note = next(
            (n for n in self.store.list_notes(owner=self.username)
             if n.get("id") == note_id), None)
        if not note:
            self._set_status("Notiz nicht gefunden")
            return
        title, body = self._split_title_body(note.get("combined", ""))
        self.title_var.set(title)
        self._set_text(self.content_box, body)
        self._dirty = False
        self._update_title_marker()
        self._update_wordcount()
        self._set_status(f"Geladen")


    def _on_text_modified(self, _evt=None):
        try:
            self.content_box.edit_modified(False)
        except Exception:
            pass
        self._on_edit_changed()

    def _on_edit_changed(self, *_):
        self._dirty = True
        self._update_title_marker()
        self._debounce(self._update_wordcount)

    def _update_title_marker(self):
        self._set_status("Ungespeicherte Änderungen" if self._dirty else "Bereit", transient=True)

    def _update_wordcount(self):
        body  = self.content_box.get("1.0", "end").strip()
        words = len([w for w in body.split() if w.strip()])
        self.lbl_wc.configure(text=f"{words} Wörter")


    def _save(self):
        title    = self.title_var.get().strip()
        body     = self.content_box.get("1.0", "end").strip()
        combined = f"{title}\n\n{body}".strip()
        try:
            if self.selected_note_id is None:
                self.store.add_note(owner=self.username, combined=combined)
            else:
                self.store.update_note(self.selected_note_id, combined)
        except Exception:
            logger.exception("persist_note failed")
            messagebox.showerror("Fehler", "Konnte nicht speichern.")
            return
        self._dirty = False
        self._update_title_marker()
        self._refresh_list()
        self._set_status("Gespeichert.")

    def _delete(self):
        if self.selected_note_id is None:
            return
        if not messagebox.askyesno("Löschen", "Diese Notiz wirklich löschen?"):
            return
        try:
            self.store.delete_note(self.selected_note_id)
        except Exception:
            logger.exception("delete_note failed")
            messagebox.showerror("Fehler", "Löschen fehlgeschlagen.")
            return
        self.selected_note_id = None
        self._new()
        self._refresh_list()
        self._set_status("Gelöscht.")

    def _new(self):
        self.selected_note_id = None
        self.title_var.set("")
        self._set_text(self.content_box, "")
        self._dirty = False
        self._update_title_marker()
        self._set_status("Neue Notiz")
        self._refresh_list()

    def _duplicate_selected(self):
        if self.selected_note_id is None:
            return
        note = next(
            (n for n in self.store.list_notes(owner=self.username)
             if n.get("id") == self.selected_note_id), None)
        if not note:
            return
        try:
            self.store.add_note(owner=self.username,
                                combined=note.get("combined", "") + " (Kopie)")
        except Exception:
            logger.exception("duplicate_note failed")
        self._refresh_list()


    def _split_title_body(self, combined: str):
        parts = combined.split("\n", 1)
        return (parts[0], parts[1].lstrip()) if len(parts) == 2 else (parts[0], "")

    def _set_text(self, widget: ctk.CTkTextbox, text: str):
        widget.delete("1.0", "end")
        if text:
            widget.insert("1.0", text)

    def _set_status(self, text: str, transient: bool = False):
        self.lbl_status.configure(text=text)
        if transient:
            if hasattr(self, "_status_after"):
                try:
                    self.after_cancel(self._status_after)
                except Exception:
                    pass
            self._status_after = self.after(
                2500, lambda: self.lbl_status.configure(text="Bereit"))

    def _set_count(self, n: int):
        self.lbl_count.configure(text=f"{n} Notizen")

    def _focus_search(self):
        for child in self._list_frame.master.winfo_children():
            if isinstance(child, ctk.CTkFrame):
                break

    def _debounce(self, fn):
        if self._debounce_after_id:
            try:
                self.after_cancel(self._debounce_after_id)
            except Exception:
                pass
        self._debounce_after_id = self.after(DEBOUNCE_MS, fn)
