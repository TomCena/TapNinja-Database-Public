"""
Settings Tab module.
Provides full CSV backup/restore, dynamic Theme Studio color customizations,
and progress wipe controls.
"""

import tkinter as tk
from tkinter import colorchooser, filedialog, messagebox
from typing import Any, Dict, Optional

from ui_components import CardFrame, ModernButton


class SettingsTab(tk.Frame):
    """Encapsulates application settings, backup/restore, color theme customization, and data wipe."""

    def __init__(self, parent: tk.Widget, app: Any):
        super().__init__(parent, bg=app.theme.bg)
        self.app = app
        self.db = app.db
        self.theme = app.theme

        self.theme_vars: Dict[str, str] = dict(self.theme.colors)
        self.theme_color_buttons: Dict[str, tk.Button] = {}
        self.theme_color_frames: Dict[str, tk.Frame] = {}

        self._build_ui()

    def _build_ui(self) -> None:
        container = tk.Frame(self, bg=self.theme.bg)
        container.pack(fill="both", expand=True, padx=20, pady=20)

        # 1. Data Management Card
        card_data = CardFrame(container, self.theme, title="Data Backup & Portability (.db & .csv)", header_color=self.theme.blue, padding=12)
        card_data.pack(fill="x", pady=(0, 15))

        # SQLite (.db) Row
        db_row = tk.Frame(card_data.body, bg=self.theme.surface)
        db_row.pack(fill="x", pady=(2, 6))

        tk.Label(
            db_row, text="SQLite Database Backup (.db):", font=self.theme.fonts["body_bold"],
            bg=self.theme.surface, fg=self.theme.fg, width=28, anchor="w"
        ).pack(side="left", padx=(0, 10))

        ModernButton(
            db_row, self.theme, text="💾 Export Database (.db)", variant="success",
            command=self.export_db, padx=14, pady=5
        ).pack(side="left", padx=(0, 8))

        ModernButton(
            db_row, self.theme, text="📂 Import Database (.db)", variant="warning",
            command=self.import_db, padx=14, pady=5
        ).pack(side="left")

        # CSV (.csv) Row
        csv_row = tk.Frame(card_data.body, bg=self.theme.surface)
        csv_row.pack(fill="x", pady=(6, 2))

        tk.Label(
            csv_row, text="CSV Spreadsheets Backup (.csv):", font=self.theme.fonts["body_bold"],
            bg=self.theme.surface, fg=self.theme.fg, width=28, anchor="w"
        ).pack(side="left", padx=(0, 10))

        ModernButton(
            csv_row, self.theme, text="📤 Export to CSV (.csv)", variant="primary",
            command=self.export_csv, padx=14, pady=5
        ).pack(side="left", padx=(0, 8))

        ModernButton(
            csv_row, self.theme, text="📥 Import from CSV (.csv)", variant="neutral",
            command=self.import_csv, padx=14, pady=5
        ).pack(side="left")

        # 2. Theme Customization Card
        card_theme = CardFrame(container, self.theme, title="Theme Customization Studio", header_color=self.theme.yellow, padding=12)
        card_theme.pack(fill="x", pady=(0, 15))

        theme_grid = tk.Frame(card_theme.body, bg=self.theme.surface)
        theme_grid.pack(fill="x", pady=8)

        theme_labels = {
            "bg_color": "Background",
            "fg_color": "Foreground Text",
            "entry_bg": "Card / Input Surface",
            "btn_bg": "Button / Tabs Background",
            "accent_green": "Emerald Accent",
            "accent_yellow": "Amber / Gold Accent",
            "accent_red": "Rose / Danger Accent",
            "accent_blue": "Blue Accent",
            "accent_purple": "Violet Accent"
        }

        r, c = 0, 0
        for key, label in theme_labels.items():
            tk.Label(
                theme_grid, text=f"{label}:", font=self.theme.fonts["body_bold"],
                bg=self.theme.surface, fg=self.theme.fg
            ).grid(row=r, column=c, padx=6, pady=6, sticky="e")

            curr_val = self.theme.colors.get(key, "#ffffff")
            contrast = self.theme.get_contrast_color(curr_val)

            border_frame = tk.Frame(theme_grid, bg=contrast, padx=1, pady=1)
            border_frame.grid(row=r, column=c + 1, padx=6, pady=6, sticky="w")
            self.theme_color_frames[key] = border_frame

            btn = tk.Button(
                border_frame, bg=curr_val, width=8, height=1, relief="flat", cursor="hand2"
            )
            btn.configure(command=lambda k=key: self.pick_color(k))
            btn.pack(fill="both", expand=True)
            self.theme_color_buttons[key] = btn

            c += 2
            if c >= 6:
                c = 0
                r += 1

        action_row = tk.Frame(card_theme.body, bg=self.theme.surface)
        action_row.pack(fill="x", pady=(10, 4))

        ModernButton(
            action_row, self.theme, text="Save & Apply Theme", variant="success",
            command=self.save_theme, padx=16, pady=6
        ).pack(side="left", padx=(0, 10))

        ModernButton(
            action_row, self.theme, text="Reset Palette to Default", variant="danger",
            command=self.reset_theme, padx=16, pady=6
        ).pack(side="left")

        # 3. Danger Zone Card
        card_danger = CardFrame(container, self.theme, title="Danger Zone", header_color=self.theme.red, padding=12)
        card_danger.pack(fill="x")

        d_row = tk.Frame(card_danger.body, bg=self.theme.surface)
        d_row.pack(fill="x", pady=6)

        self.btn_reset = ModernButton(
            d_row, self.theme, text="Reset All Player Progress", variant="danger",
            command=self.ask_reset_progress, padx=14, pady=6
        )
        self.btn_reset.pack(side="left")

        self.reset_confirm_frame = tk.Frame(d_row, bg=self.theme.surface)
        tk.Label(
            self.reset_confirm_frame, text="Are you sure? All progress data will be permanently wiped.",
            font=self.theme.fonts["body_bold"], fg=self.theme.red, bg=self.theme.surface
        ).pack(side="left", padx=8)

        ModernButton(
            self.reset_confirm_frame, self.theme, text="Yes, Reset Everything", variant="danger",
            command=self.perform_reset_progress, padx=12, pady=4
        ).pack(side="left", padx=4)

        ModernButton(
            self.reset_confirm_frame, self.theme, text="Cancel", variant="neutral",
            command=self.cancel_reset, padx=12, pady=4
        ).pack(side="left", padx=4)

        # Settings Status Bar
        self.settings_status_label = tk.Label(
            container, text="", font=self.theme.fonts["body_bold"],
            bg=self.theme.bg, fg=self.theme.fg
        )
        self.settings_status_label.pack(side="bottom", pady=10)

    def show_status(self, message: str, color: Optional[str] = None) -> None:
        self.settings_status_label.config(text=message, fg=color or self.theme.fg)

    def pick_color(self, key: str) -> None:
        """Opens a color chooser dialog and updates preview buttons."""
        current = self.theme_vars.get(key, self.theme.colors.get(key, "#ffffff"))
        chosen = colorchooser.askcolor(color=current, title=f"Select Color for {key}")[1]
        if chosen:
            self.theme_vars[key] = chosen
            if key in self.theme_color_buttons:
                self.theme_color_buttons[key].configure(bg=chosen)
            if key in self.theme_color_frames:
                self.theme_color_frames[key].configure(bg=self.theme.get_contrast_color(chosen))

    def save_theme(self) -> None:
        """Saves customized colors to SQLite and triggers app-wide theme repaint."""
        self.theme.save_to_db(self.db, self.theme_vars)
        self.app.apply_theme_update()
        self.show_status("Theme saved and applied successfully!", self.theme.green)

    def reset_theme(self) -> None:
        """Resets theme to defaults and repaints app."""
        self.theme.reset_to_default(self.db)
        self.theme_vars = dict(self.theme.colors)
        for key, btn in self.theme_color_buttons.items():
            col = self.theme.colors.get(key, "#ffffff")
            btn.configure(bg=col)
            if key in self.theme_color_frames:
                self.theme_color_frames[key].configure(bg=self.theme.get_contrast_color(col))
        self.app.apply_theme_update()
        self.show_status("Theme reset to default Windows 11 Dark Mica palette.", self.theme.green)

    def export_db(self) -> None:
        """Prompts for target file and exports the complete raw SQLite database (.db)."""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".db",
            filetypes=[("SQLite Database files", "*.db"), ("All files", "*.*")],
            initialfile="datenbank_backup.db"
        )
        if not file_path:
            return
        try:
            self.db.export_db(file_path)
            self.show_status(f"Database (.db) exported successfully to {file_path}", self.theme.green)
        except Exception as e:
            self.show_status(f"Database export failed: {e}", self.theme.red)

    def import_db(self) -> None:
        """Prompts for SQLite .db file, confirms overwrite, restores database, and reloads all tabs."""
        file_path = filedialog.askopenfilename(
            filetypes=[("SQLite Database files", "*.db *.sqlite *.sqlite3"), ("All files", "*.*")]
        )
        if not file_path:
            return

        if not messagebox.askyesno(
            "Confirm Database Restore",
            "Restoring an external .db file will replace your current active database.\n\nDo you want to proceed?"
        ):
            return

        try:
            self.db.import_db(file_path)
            self.app.reload_all_tabs()
            self.show_status(f"Database restored successfully from {file_path}!", self.theme.green)
        except Exception as e:
            self.show_status(f"Database import failed: {e}", self.theme.red)

    def export_csv(self) -> None:
        """Prompts for target file and exports complete database to CSV."""
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if not file_path:
            return
        try:
            self.db.export_csv(file_path)
            self.show_status(f"Data exported successfully to {file_path}", self.theme.green)
        except Exception as e:
            self.show_status(f"Export failed: {e}", self.theme.red)

    def import_csv(self) -> None:
        """Prompts for CSV file, imports records, and refreshes all tabs."""
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not file_path:
            return
        try:
            self.db.import_csv(file_path)
            self.app.reload_all_tabs()
            self.show_status("Data imported successfully!", self.theme.green)
        except Exception as e:
            self.show_status(f"Import failed: {e}", self.theme.red)

    def ask_reset_progress(self) -> None:
        self.btn_reset.pack_forget()
        self.reset_confirm_frame.pack(side="left")
        self.show_status("Waiting for reset confirmation...", self.theme.yellow)

    def cancel_reset(self) -> None:
        self.reset_confirm_frame.pack_forget()
        self.btn_reset.pack(side="left")
        self.show_status("Reset cancelled.", self.theme.fg)

    def perform_reset_progress(self) -> None:
        """Performs full progress wipe and updates all UI tables."""
        try:
            self.db.reset_all_progress()
            self.app.reload_all_tabs()
            self.cancel_reset()
            self.show_status("All progress has been reset.", self.theme.green)
        except Exception as e:
            self.show_status(f"Reset failed: {e}", self.theme.red)
