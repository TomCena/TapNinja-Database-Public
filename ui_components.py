"""
Modern Windows 11 Dark Mica UI Components.
Provides CardFrame, ModernButton, ModernEntry with dynamic focus borders,
ConflictDialog, and Treeview striping setup.
"""

import tkinter as tk
from tkinter import ttk
from typing import Any, Optional, Dict

from theme import ThemeManager, apply_windows_dark_titlebar


class CardFrame(tk.Frame):
    """
    Sleek Windows 11 Dark Mica card container.
    Features a subtle 1px border (#3a3a3a) and elevated surface fill (#2b2b2b).
    """

    def __init__(
        self,
        parent: tk.Widget,
        theme: ThemeManager,
        title: Optional[str] = None,
        header_color: Optional[str] = None,
        padding: int = 12,
        **kwargs: Any
    ):
        # 1px border wrapper (#3a3a3a)
        super().__init__(
            parent,
            bg=theme.border,
            padx=1,
            pady=1,
            **kwargs
        )
        self.theme = theme

        # Elevated surface body (#2b2b2b)
        self.body = tk.Frame(self, bg=theme.surface, padx=padding, pady=padding)
        self.body.pack(fill="both", expand=True)

        if title:
            header_frame = tk.Frame(self.body, bg=theme.surface)
            header_frame.pack(side="top", fill="x", pady=(0, 8))

            color = header_color or theme.fg
            lbl_title = tk.Label(
                header_frame,
                text=title,
                font=theme.fonts["card_title"],
                bg=theme.surface,
                fg=color
            )
            lbl_title.pack(side="left", anchor="w")

            # Subtle accent separator line under header
            sep = tk.Frame(header_frame, height=1, bg=theme.border)
            sep.pack(side="bottom", fill="x", pady=(4, 0))


class ModernButton(tk.Button):
    """
    Custom Windows 11 styled button with smooth hover state feedback and semantic color variants.
    """

    def __init__(
        self,
        parent: tk.Widget,
        theme: ThemeManager,
        text: str,
        variant: str = "neutral",  # 'primary', 'success', 'warning', 'danger', 'neutral'
        command: Optional[Any] = None,
        padx: int = 12,
        pady: int = 4,
        **kwargs: Any
    ):
        self.theme = theme
        self.variant = variant
        self.normal_bg, self.hover_bg, self.active_bg, self.text_color, self.border_col = self._resolve_colors()

        super().__init__(
            parent,
            text=text,
            command=command,
            font=theme.fonts["body_bold"],
            bg=self.normal_bg,
            fg=self.text_color,
            activebackground=self.active_bg,
            activeforeground=self.text_color,
            relief="flat",
            borderwidth=1,
            highlightthickness=1,
            highlightbackground=self.border_col,
            cursor="hand2",
            padx=padx,
            pady=pady,
            **kwargs
        )

        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def _resolve_colors(self) -> tuple[str, str, str, str, str]:
        """Maps button variants to Windows 11 Dark Mica action colors."""
        if self.variant == "primary":
            return (self.theme.blue_dark, "#1084d9", "#006cc1", "#ffffff", self.theme.blue)
        elif self.variant == "success":
            return ("#203d22", "#284f2b", "#1a331c", self.theme.green, "#2f5e33")
        elif self.variant == "warning":
            return ("#42340b", "#54420e", "#332808", self.theme.yellow, "#614d11")
        elif self.variant == "danger":
            return ("#451e22", "#57262b", "#36171a", self.theme.red, "#6e2e34")
        else:  # neutral
            return (self.theme.btn_bg, "#3a3a3a", "#292929", self.theme.fg, self.theme.border)

    def _on_enter(self, _event: tk.Event) -> None:
        self.configure(bg=self.hover_bg)

    def _on_leave(self, _event: tk.Event) -> None:
        self.configure(bg=self.normal_bg)


class ModernEntry(tk.Entry):
    """
    Windows 11 styled text input field with dark backdrop (#1f1f1f)
    and dynamic accent focus border (#60cdff).
    """

    def __init__(self, parent: tk.Widget, theme: ThemeManager, **kwargs: Any):
        self.theme = theme
        super().__init__(
            parent,
            bg=theme.input_bg,
            fg=theme.fg,
            insertbackground=theme.fg,
            font=theme.fonts["body"],
            relief="flat",
            highlightthickness=1,
            highlightbackground=theme.border,
            highlightcolor=theme.border_focus,
            **kwargs
        )
        self.bind("<FocusIn>", self._on_focus_in)
        self.bind("<FocusOut>", self._on_focus_out)

    def _on_focus_in(self, _event: tk.Event) -> None:
        self.configure(highlightbackground=self.theme.border_focus)

    def _on_focus_out(self, _event: tk.Event) -> None:
        self.configure(highlightbackground=self.theme.border)


class ConflictDialog(tk.Toplevel):
    """
    Windows 11 styled modal dialog for resolving CSV import duplicate date conflicts.
    """

    def __init__(self, parent: tk.Widget, theme: ThemeManager, date_str: str, old_val: str, new_val: str):
        super().__init__(parent)
        self.theme = theme
        self.result: Optional[str] = None

        self.title("Duplicate Date Conflict")
        self.geometry("460x220")
        self.resizable(False, False)
        self.configure(bg=theme.bg)

        # Apply native Windows 11 Dark title bar
        apply_windows_dark_titlebar(self)

        self.transient(parent)
        self.grab_set()

        card = CardFrame(self, theme, title="⚠️ Date Conflict Detected", header_color=theme.yellow, padding=16)
        card.pack(fill="both", expand=True, padx=12, pady=12)

        msg = f"The date {date_str} already exists.\n\nExisting: {old_val}\nImporting: {new_val}\n\nWhat would you like to do?"
        tk.Label(
            card.body,
            text=msg,
            font=theme.fonts["body"],
            bg=theme.surface,
            fg=theme.fg,
            justify="left"
        ).pack(anchor="w", pady=(0, 14))

        btn_row = tk.Frame(card.body, bg=theme.surface)
        btn_row.pack(fill="x")

        ModernButton(btn_row, theme, text="Overwrite", variant="danger", command=lambda: self._set_result("overwrite")).pack(side="left", padx=3)
        ModernButton(btn_row, theme, text="Overwrite All", variant="danger", command=lambda: self._set_result("overwrite_all")).pack(side="left", padx=3)
        ModernButton(btn_row, theme, text="Skip", variant="neutral", command=lambda: self._set_result("skip")).pack(side="left", padx=3)
        ModernButton(btn_row, theme, text="Skip All", variant="neutral", command=lambda: self._set_result("skip_all")).pack(side="left", padx=3)

        self.wait_window(self)

    def _set_result(self, res: str) -> None:
        self.result = res
        self.destroy()


class ModernScrollbar(tk.Scrollbar):
    """
    Windows 11 styled dark scrollbar with dark background, dark trough,
    and responsive hover states matching the Info Tab styling.
    """

    def __init__(self, parent: tk.Widget, theme: ThemeManager, **kwargs: Any):
        self.theme = theme
        super().__init__(
            parent,
            bg=theme.surface,
            troughcolor=theme.bg,
            activebackground="#404040",
            highlightbackground=theme.bg,
            highlightcolor=theme.blue,
            borderwidth=0,
            highlightthickness=0,
            relief="flat",
            **kwargs
        )


def setup_treeview_striping(tree: ttk.Treeview, theme: ThemeManager) -> None:
    """Configures alternating row colors (#202020 / #262626) for clean table readability."""
    tree.tag_configure("evenrow", background=theme.bg, foreground=theme.fg)
    tree.tag_configure("oddrow", background="#262626", foreground=theme.fg)
