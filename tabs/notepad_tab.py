"""
Notepad Tab module.
Provides an auto-saving strategist notepad with interactive checkbox checklist features.
"""

import tkinter as tk
from typing import Any, Optional

from ui_components import CardFrame, ModernButton, ModernScrollbar


class NotepadTab(tk.Frame):
    """Encapsulates note taking, task lists with clickable checkboxes, and auto-persistence."""

    def __init__(self, parent: tk.Widget, app: Any):
        super().__init__(parent, bg=app.theme.bg)
        self.app = app
        self.db = app.db
        self.theme = app.theme

        self.notepad_save_timer: Optional[str] = None
        self._build_ui()

    def _build_ui(self) -> None:
        card = CardFrame(self, self.theme, title="Strategist Notes & Task List", header_color=self.theme.blue, padding=10)
        card.pack(fill="both", expand=True, padx=15, pady=15)

        # Toolbar
        toolbar = tk.Frame(card.body, bg=self.theme.surface)
        toolbar.pack(side="top", fill="x", pady=(0, 8))

        ModernButton(
            toolbar, self.theme, text="☑ Insert Checklist Item", variant="neutral",
            command=self.insert_checklist, padx=10, pady=3
        ).pack(side="left")

        self.lbl_notepad_status = tk.Label(toolbar, text="", font=self.theme.fonts["small_bold"], bg=self.theme.surface, fg=self.theme.green)
        self.lbl_notepad_status.pack(side="right", padx=10)

        # Text Area with Scrollbar
        editor_frame = tk.Frame(card.body, bg=self.theme.surface)
        editor_frame.pack(fill="both", expand=True)

        scrollbar = ModernScrollbar(editor_frame, self.theme)
        scrollbar.pack(side="right", fill="y")

        self.txt_notepad = tk.Text(
            editor_frame,
            bg=self.theme.bg,
            fg=self.theme.fg,
            font=self.theme.fonts["code"],
            insertbackground=self.theme.fg,
            relief="flat",
            highlightthickness=1,
            highlightbackground=self.theme.border,
            highlightcolor=self.theme.blue,
            padx=12,
            pady=12,
            yscrollcommand=scrollbar.set,
            undo=True,
            wrap="word"
        )
        self.txt_notepad.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.txt_notepad.yview)

        # Event Bindings
        self.txt_notepad.bind("<KeyRelease>", self.schedule_save)
        self.txt_notepad.bind("<FocusOut>", self.save_content)
        self.txt_notepad.bind("<Button-1>", self.on_text_click)

        # Load existing content
        saved_content = self.db.get_setting("notepad_content", "")
        if saved_content:
            self.txt_notepad.insert("1.0", saved_content)

    def insert_checklist(self) -> None:
        """Inserts an uncompleted checkbox item at cursor position."""
        self.txt_notepad.insert("insert", "☐ ")
        self.txt_notepad.focus_set()

    def on_text_click(self, event: tk.Event) -> Optional[str]:
        """Toggles checklist status between ☐ and ☑ when clicked."""
        index = self.txt_notepad.index(f"@{event.x},{event.y}")
        char = self.txt_notepad.get(index)

        if char == "☐":
            self.txt_notepad.delete(index)
            self.txt_notepad.insert(index, "☑")
            self.schedule_save()
            return "break"
        elif char == "☑":
            self.txt_notepad.delete(index)
            self.txt_notepad.insert(index, "☐")
            self.schedule_save()
            return "break"
        return None

    def schedule_save(self, _event: Optional[tk.Event] = None) -> None:
        """Debounces content persistence by 1 second."""
        if self.notepad_save_timer:
            self.after_cancel(self.notepad_save_timer)
        self.notepad_save_timer = self.after(1000, self.save_content)
        self.lbl_notepad_status.config(text="Saving...", fg=self.theme.yellow)

    def save_content(self, _event: Optional[tk.Event] = None) -> None:
        """Saves notepad content to the SQLite settings store."""
        content = self.txt_notepad.get("1.0", tk.END)
        self.db.set_setting("notepad_content", content)
        self.lbl_notepad_status.config(text="Saved ✓", fg=self.theme.green)
        if self.notepad_save_timer:
            self.after_cancel(self.notepad_save_timer)
            self.notepad_save_timer = None
