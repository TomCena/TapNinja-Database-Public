"""
Theme Manager module for Windows 11 Dark Mica aesthetic.
Configures typography, TTK component styles, native Windows DWM Dark title bar,
and dynamic palette updates.
"""

import tkinter as tk
from tkinter import ttk, font
import ctypes
from typing import Any, Dict, Optional, Tuple

from constants import DEFAULT_THEME


def apply_windows_dark_titlebar(window: tk.Tk | tk.Toplevel) -> None:
    """Enables native Windows 11 Immersive Dark Mode and Mica title bar via DWM API."""
    try:
        window.update_idletasks()
        hwnd = ctypes.windll.user32.GetParent(window.winfo_id())
        if not hwnd:
            hwnd = window.winfo_id()

        # DWMWA_USE_IMMERSIVE_DARK_MODE: 20 on Win11 22000+, 19 on older Win10 builds
        val_true = ctypes.c_int(2)
        res = ctypes.windll.dwmapi.DwmSetWindowAttribute(
            hwnd, 20, ctypes.byref(val_true), ctypes.sizeof(val_true)
        )
        if res != 0:
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd, 19, ctypes.byref(val_true), ctypes.sizeof(val_true)
            )

        # DWMWA_SYSTEMBACKDROP_TYPE: 38 (2 = DWMSBT_MAINWINDOW / Mica)
        backdrop_mica = ctypes.c_int(2)
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            hwnd, 38, ctypes.byref(backdrop_mica), ctypes.sizeof(backdrop_mica)
        )
    except Exception:
        pass


class ThemeManager:
    """Manages color tokens, TTK styles, and typography for the Windows 11 Dark Mica aesthetic."""

    def __init__(self, style: Optional[ttk.Style] = None):
        self.style = style or ttk.Style()
        self.colors: Dict[str, str] = dict(DEFAULT_THEME)
        self.font_family = self._resolve_font_family()
        self.fonts = self._setup_fonts()

    def _resolve_font_family(self) -> str:
        """Prefers modern Windows 11 'Segoe UI Variable Text', falling back to 'Segoe UI'."""
        try:
            available = font.families()
            if "Segoe UI Variable Text" in available:
                return "Segoe UI Variable Text"
            if "Segoe UI" in available:
                return "Segoe UI"
        except Exception:
            pass
        return "Segoe UI"

    def _setup_fonts(self) -> Dict[str, Tuple[str, int, str] | Tuple[str, int]]:
        """Creates a cohesive typography hierarchy."""
        fam = self.font_family
        return {
            "title": (fam, 16, "bold"),
            "section": (fam, 13, "bold"),
            "card_title": (fam, 11, "bold"),
            "body": (fam, 10),
            "body_bold": (fam, 10, "bold"),
            "small": (fam, 9),
            "small_bold": (fam, 9, "bold"),
            "code": ("Consolas", 10),
            "metric_large": (fam, 20, "bold"),
            "metric_sub": (fam, 9)
        }

    # --- Color Accessors ---
    @property
    def bg(self) -> str:
        return self.colors.get("bg_color", DEFAULT_THEME["bg_color"])

    @property
    def fg(self) -> str:
        return self.colors.get("fg_color", DEFAULT_THEME["fg_color"])

    @property
    def surface(self) -> str:
        return self.colors.get("entry_bg", DEFAULT_THEME["entry_bg"])

    @property
    def input_bg(self) -> str:
        return self.colors.get("input_bg", DEFAULT_THEME["input_bg"])

    @property
    def btn_bg(self) -> str:
        return self.colors.get("btn_bg", DEFAULT_THEME["btn_bg"])

    @property
    def blue(self) -> str:
        return self.colors.get("accent_blue", DEFAULT_THEME["accent_blue"])

    @property
    def blue_dark(self) -> str:
        return self.colors.get("accent_blue_dark", DEFAULT_THEME["accent_blue_dark"])

    @property
    def green(self) -> str:
        return self.colors.get("accent_green", DEFAULT_THEME["accent_green"])

    @property
    def yellow(self) -> str:
        return self.colors.get("accent_yellow", DEFAULT_THEME["accent_yellow"])

    @property
    def red(self) -> str:
        return self.colors.get("accent_red", DEFAULT_THEME["accent_red"])

    @property
    def purple(self) -> str:
        return self.colors.get("accent_purple", DEFAULT_THEME["accent_purple"])

    @property
    def border(self) -> str:
        return self.colors.get("border_color", DEFAULT_THEME["border_color"])

    @property
    def border_focus(self) -> str:
        return self.colors.get("border_focus", DEFAULT_THEME["border_focus"])

    @property
    def text_dim(self) -> str:
        return self.colors.get("text_dim", DEFAULT_THEME["text_dim"])

    def load_from_db(self, db_manager: Any) -> None:
        """Loads saved color overrides from the SQLite database."""
        for key in DEFAULT_THEME:
            saved_val = db_manager.get_setting(f"theme_{key}")
            if saved_val:
                self.colors[key] = saved_val

    def save_to_db(self, db_manager: Any, new_colors: Dict[str, str]) -> None:
        """Saves custom colors to the SQLite database."""
        for key, val in new_colors.items():
            self.colors[key] = val
            db_manager.set_setting(f"theme_{key}", val)

    def reset_to_default(self, db_manager: Any) -> None:
        """Resets palette to default Windows 11 Dark Mica tokens."""
        self.colors = dict(DEFAULT_THEME)
        for key in DEFAULT_THEME:
            db_manager.run_query("DELETE FROM settings WHERE key = ?", (f"theme_{key}",))

    def apply_ttk_styles(self) -> None:
        """Configures TTK widgets to match Windows 11 Dark Mica and segmented navigation pills."""
        self.style.theme_use("clam")

        # 1. Segmented Navigation Pills (TNotebook & TNotebook.Tab)
        self.style.configure(
            "TNotebook",
            background=self.bg,
            borderwidth=0,
            tabmargins=[4, 4, 4, 0]
        )
        self.style.configure(
            "TNotebook.Tab",
            background="#2b2b2b",
            foreground=self.fg,
            padding=[16, 7],
            font=self.fonts["body_bold"],
            borderwidth=0,
            focuscolor=""
        )
        self.style.map(
            "TNotebook.Tab",
            background=[("selected", "#383838"), ("active", "#333333")],
            foreground=[("selected", self.blue), ("active", "#ffffff")]
        )

        # 2. Modern Table View (Treeview)
        self.style.configure(
            "Treeview",
            background=self.bg,
            foreground=self.fg,
            fieldbackground=self.bg,
            rowheight=30,
            font=self.fonts["body"],
            borderwidth=0,
            relief="flat"
        )
        self.style.configure(
            "Treeview.Heading",
            background="#282828",
            foreground=self.fg,
            font=self.fonts["small_bold"],
            relief="flat",
            borderwidth=0,
            padding=[10, 8]
        )
        self.style.map(
            "Treeview.Heading",
            background=[("active", "#333333")],
            foreground=[("active", self.blue)]
        )
        self.style.map(
            "Treeview",
            background=[("selected", "#383838")],
            foreground=[("selected", self.blue)]
        )

        # 3. Progressbars
        self.style.configure(
            "TProgressbar",
            troughcolor="#2b2b2b",
            background=self.blue,
            borderwidth=0,
            thickness=12
        )

        # 4. Comboboxes
        self.style.configure(
            "TCombobox",
            background=self.input_bg,
            foreground=self.fg,
            fieldbackground=self.input_bg,
            selectbackground="#383838",
            selectforeground=self.fg,
            arrowcolor=self.fg,
            padding=5,
            relief="flat"
        )
        self.style.map(
            "TCombobox",
            fieldbackground=[("readonly", self.input_bg)],
            selectbackground=[("readonly", "#383838")]
        )

        # 5. Scrollbars
        self.style.configure(
            "TScrollbar",
            background=self.surface,
            troughcolor=self.bg,
            bordercolor=self.bg,
            darkcolor=self.surface,
            lightcolor=self.surface,
            arrowcolor=self.fg,
            arrowsize=11,
            borderwidth=0,
            relief="flat"
        )
        self.style.map(
            "TScrollbar",
            background=[("active", "#404040"), ("pressed", self.blue), ("disabled", "#222222")],
            troughcolor=[("active", self.bg), ("disabled", self.bg)],
            arrowcolor=[("active", self.blue)]
        )
        self.style.configure("Vertical.TScrollbar", background=self.surface, troughcolor=self.bg, borderwidth=0, relief="flat")
        self.style.configure("Horizontal.TScrollbar", background=self.surface, troughcolor=self.bg, borderwidth=0, relief="flat")

    def get_contrast_color(self, hex_color: str) -> str:
        """Calculates WCAG contrast color (#ffffff or #000000) for a given background hex."""
        try:
            hex_color = hex_color.lstrip('#')
            if len(hex_color) == 6:
                r = int(hex_color[0:2], 16)
                g = int(hex_color[2:4], 16)
                b = int(hex_color[4:6], 16)
                luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255.0
                return "#000000" if luminance > 0.5 else "#ffffff"
        except Exception:
            pass
        return "#ffffff"

    def update_widget_tree(self, widget: tk.Widget, old_colors: Optional[Dict[str, str]] = None) -> None:
        """Recursively repaints existing widgets when the theme palette is updated."""
        w_class = widget.winfo_class()
        try:
            if w_class in ("Frame", "LabelFrame"):
                curr_bg = widget.cget("bg")
                if old_colors and curr_bg == old_colors.get("bg_color"):
                    widget.configure(bg=self.bg)
                elif old_colors and curr_bg == old_colors.get("entry_bg"):
                    widget.configure(bg=self.surface)
            elif w_class == "Label":
                curr_bg = widget.cget("bg")
                if old_colors and curr_bg == old_colors.get("bg_color"):
                    widget.configure(bg=self.bg)
                elif old_colors and curr_bg == old_colors.get("entry_bg"):
                    widget.configure(bg=self.surface)
            elif w_class == "Entry":
                widget.configure(bg=self.input_bg, fg=self.fg, insertbackground=self.fg)
            elif w_class == "Text":
                widget.configure(bg=self.surface, fg=self.fg, insertbackground=self.fg)
        except Exception:
            pass

        for child in widget.winfo_children():
            self.update_widget_tree(child, old_colors)
