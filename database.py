"""
Database management module for the TapNinja Database application.
Handles SQLite connections, schema initialization, migrations, CRUD operations,
CSV import/export, and data resets.
"""

import sqlite3
import os
import csv
from contextlib import contextmanager
from typing import Any, Dict, Generator, List, Optional, Tuple

from constants import (
    HERO_NAMES, RARE_HEROES, EPIC_HEROES, HERO_DETAILS_MAP,
    PET_NAMES, BUILDINGS_LIST, EQUIPMENT_DATA,
    FASHION_ITEMS, SEASONAL_RESOURCES, SECRET_ACHIEVEMENTS
)


class DatabaseManager:
    """Manages SQLite database interactions with safe context handling and migrations."""

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            self.db_name = os.path.join(script_dir, "datenbank.db")
        else:
            self.db_name = db_path
        self.init_db()

    @contextmanager
    def get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Context manager for SQLite connections ensuring proper commit and close."""
        conn = sqlite3.connect(self.db_name)
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def run_query(self, query: str, parameters: tuple = ()) -> sqlite3.Cursor:
        """Executes a SQL query and commits the changes."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            result = cursor.execute(query, parameters)
            conn.commit()
            return result

    def fetch_all(self, query: str, parameters: tuple = ()) -> List[Tuple[Any, ...]]:
        """Executes a query and returns all matching rows."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(query, parameters)
            return cursor.fetchall()

    def fetch_one(self, query: str, parameters: tuple = ()) -> Optional[Tuple[Any, ...]]:
        """Executes a query and returns a single row if available."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(query, parameters)
            return cursor.fetchone()

    def get_rarity(self, name: str) -> str:
        """Determines the rarity of a hero based on their registry category."""
        if name in RARE_HEROES:
            return "Rare"
        if name in EPIC_HEROES:
            return "Epic"
        return "Legendary"

    def init_db(self) -> None:
        """Initializes tables and performs non-destructive schema migrations."""
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()

            # --- Create Core Tables ---
            c.execute("""
                CREATE TABLE IF NOT EXISTS daten (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    sterne TEXT,
                    xp_level TEXT,
                    dust_used TEXT,
                    dust_needed TEXT,
                    rarity TEXT,
                    faction TEXT,
                    class TEXT
                )
            """)
            c.execute("""
                CREATE TABLE IF NOT EXISTS pets (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    sterne TEXT,
                    bond_level TEXT,
                    feathers_used TEXT,
                    feathers_needed TEXT
                )
            """)
            c.execute("""
                CREATE TABLE IF NOT EXISTS buildings (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE,
                    level TEXT
                )
            """)
            c.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            """)
            c.execute("""
                CREATE TABLE IF NOT EXISTS elixir_data (
                    id INTEGER PRIMARY KEY,
                    date TEXT NOT NULL,
                    total_elixir REAL
                )
            """)
            c.execute("""
                CREATE TABLE IF NOT EXISTS pulls_scrolls (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    stars INTEGER,
                    date TEXT
                )
            """)
            c.execute("""
                CREATE TABLE IF NOT EXISTS pulls_eggs (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    stars INTEGER,
                    date TEXT
                )
            """)
            c.execute("""
                CREATE TABLE IF NOT EXISTS equipment (
                    name TEXT PRIMARY KEY,
                    level INTEGER
                )
            """)
            c.execute("""
                CREATE TABLE IF NOT EXISTS fashion (
                    name TEXT PRIMARY KEY,
                    is_unlocked INTEGER
                )
            """)
            c.execute("""
                CREATE TABLE IF NOT EXISTS seasonal_data (
                    resource TEXT PRIMARY KEY
                )
            """)
            c.execute("""
                CREATE TABLE IF NOT EXISTS secret_achievements (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    is_completed INTEGER DEFAULT 0
                )
            """)

            # --- Backward-Compatible Column Migrations ---
            def add_column_if_missing(table: str, column: str, col_type: str, default_val: str = "'-'"):
                c.execute(f"PRAGMA table_info({table})")
                existing_cols = [info[1] for info in c.fetchall()]
                if column not in existing_cols:
                    c.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_type} DEFAULT {default_val}")

            add_column_if_missing("daten", "dust_used", "TEXT")
            add_column_if_missing("daten", "dust_needed", "TEXT")
            add_column_if_missing("daten", "rarity", "TEXT", "NULL")
            add_column_if_missing("daten", "faction", "TEXT", "NULL")
            add_column_if_missing("daten", "class", "TEXT", "NULL")
            add_column_if_missing("pets", "feathers_used", "TEXT")
            add_column_if_missing("pets", "feathers_needed", "TEXT")
            add_column_if_missing("seasonal_data", "season_1", "TEXT", "'-'")

            # --- Data Population & Enrichment ---
            c.execute("SELECT id, name FROM daten WHERE rarity IS NULL OR faction IS NULL OR class IS NULL")
            for row_id, name in c.fetchall():
                rarity = self.get_rarity(name)
                faction, cls = HERO_DETAILS_MAP.get(name, ("-", "-"))
                c.execute("UPDATE daten SET rarity = ?, faction = ?, class = ? WHERE id = ?", (rarity, faction, cls, row_id))

            for name in HERO_NAMES:
                c.execute("SELECT 1 FROM daten WHERE name = ?", (name,))
                if not c.fetchone():
                    rarity = self.get_rarity(name)
                    faction, cls = HERO_DETAILS_MAP.get(name, ("-", "-"))
                    c.execute(
                        "INSERT INTO daten (name, sterne, xp_level, rarity, faction, class) VALUES (?, '-', '-', ?, ?, ?)",
                        (name, rarity, faction, cls)
                    )

            for name in PET_NAMES:
                c.execute("SELECT 1 FROM pets WHERE name = ?", (name,))
                if not c.fetchone():
                    c.execute("INSERT INTO pets (name, sterne, bond_level) VALUES (?, '-', '-')", (name,))

            c.executemany(
                "INSERT OR IGNORE INTO buildings (name, level) VALUES (?, '-')",
                [(n,) for n in BUILDINGS_LIST]
            )
            c.executemany(
                "INSERT OR IGNORE INTO equipment (name, level) VALUES (?, 0)",
                [(n,) for n in EQUIPMENT_DATA]
            )
            c.executemany(
                "INSERT OR IGNORE INTO fashion (name, is_unlocked) VALUES (?, ?)",
                [(n, 1 if n == "Default" else 0) for n in FASHION_ITEMS]
            )
            c.executemany(
                "INSERT OR IGNORE INTO seasonal_data (resource) VALUES (?)",
                [(r,) for r in SEASONAL_RESOURCES]
            )
            c.executemany(
                "INSERT OR IGNORE INTO secret_achievements (id, name, is_completed) VALUES (?, ?, 0)",
                [(a["id"], a["name"]) for a in SECRET_ACHIEVEMENTS]
            )

            conn.commit()

    # --- Settings Helpers ---

    def get_setting(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Retrieves a single setting string by key."""
        res = self.fetch_one("SELECT value FROM settings WHERE key = ?", (key,))
        return res[0] if res else default

    def get_secret_achievements(self) -> Dict[int, bool]:
        """Returns mapping of achievement_id -> is_completed (bool)."""
        rows = self.fetch_all("SELECT id, is_completed FROM secret_achievements")
        return {row[0]: bool(row[1]) for row in rows}

    def set_secret_achievement_status(self, achievement_id: int, is_completed: bool) -> None:
        """Updates completion status for a secret achievement."""
        self.run_query(
            "UPDATE secret_achievements SET is_completed = ? WHERE id = ?",
            (1 if is_completed else 0, achievement_id)
        )

    def set_setting(self, key: str, value: str) -> None:
        """Saves or updates a key-value setting."""
        self.run_query("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, str(value)))

    # --- Seasonal Helpers ---

    def is_season_empty(self, season_num: int) -> bool:
        """Checks if a season column has no recorded data (all '-', empty, or null)."""
        col_name = f"season_{season_num}"
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute("PRAGMA table_info(seasonal_data)")
            existing_cols = [info[1] for info in c.fetchall()]
            if col_name not in existing_cols:
                return True
            c.execute(f"SELECT COUNT(*) FROM seasonal_data WHERE {col_name} IS NOT NULL AND TRIM({col_name}) NOT IN ('-', '', 'none', 'null')")
            count = c.fetchone()[0]
            return count == 0

    def delete_season(self, season_num: int) -> None:
        """Drops a specific season column from the seasonal_data table."""
        col_name = f"season_{season_num}"
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute("PRAGMA table_info(seasonal_data)")
            existing_cols = [info[1] for info in c.fetchall()]
            if col_name in existing_cols:
                try:
                    c.execute(f"ALTER TABLE seasonal_data DROP COLUMN {col_name}")
                    conn.commit()
                except sqlite3.OperationalError:
                    pass

    def cleanup_empty_seasons(self, preserve_single: bool = True) -> List[int]:
        """Identifies and drops all empty season columns from the database."""
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute("PRAGMA table_info(seasonal_data)")
            columns = [info[1] for info in c.fetchall()]
            season_cols = [col for col in columns if col.startswith("season_")]

            empty_cols = []
            non_empty_cols = []

            for col in season_cols:
                c.execute(f"SELECT COUNT(*) FROM seasonal_data WHERE {col} IS NOT NULL AND TRIM({col}) NOT IN ('-', '', 'none', 'null')")
                count = c.fetchone()[0]
                if count == 0:
                    empty_cols.append(col)
                else:
                    non_empty_cols.append(col)

            # If all seasons are empty and preserve_single is True, keep season_1
            if preserve_single and not non_empty_cols and empty_cols:
                keep_col = "season_1" if "season_1" in empty_cols else empty_cols[0]
                empty_cols.remove(keep_col)
                non_empty_cols.append(keep_col)

            for col in empty_cols:
                try:
                    c.execute(f"ALTER TABLE seasonal_data DROP COLUMN {col}")
                except sqlite3.OperationalError:
                    pass
            conn.commit()

            # Return remaining season numbers
            c.execute("PRAGMA table_info(seasonal_data)")
            current_cols = [info[1] for info in c.fetchall()]
            remaining = []
            for col in current_cols:
                if col.startswith("season_"):
                    try:
                        remaining.append(int(col.split('_')[1]))
                    except (ValueError, IndexError):
                        continue
            if not remaining and preserve_single:
                self.ensure_season_column_exists("season_1")
                remaining = [1]
            return sorted(remaining)

    def get_existing_seasons(self, auto_cleanup: bool = True) -> List[int]:
        """Returns a sorted list of existing season numbers, automatically cleaning up empty seasons if requested."""
        if auto_cleanup:
            return self.cleanup_empty_seasons()

        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute("PRAGMA table_info(seasonal_data)")
            columns = [info[1] for info in c.fetchall()]
            season_nums = []
            for col in columns:
                if col.startswith("season_"):
                    try:
                        season_nums.append(int(col.split('_')[1]))
                    except (ValueError, IndexError):
                        continue
            return sorted(season_nums)

    def ensure_season_column_exists(self, season_col_name: str) -> None:
        """Checks if a season column exists in seasonal_data and creates it if not."""
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute("PRAGMA table_info(seasonal_data)")
            existing_cols = [info[1] for info in c.fetchall()]
            if season_col_name not in existing_cols:
                c.execute(f"ALTER TABLE seasonal_data ADD COLUMN {season_col_name} TEXT DEFAULT '-'")
                conn.commit()

    def create_new_season(self) -> int:
        """Creates a new incremental season column in seasonal_data."""
        existing = self.get_existing_seasons(auto_cleanup=False)
        next_num = max(existing) + 1 if existing else 1
        col_name = f"season_{next_num}"
        self.ensure_season_column_exists(col_name)
        return next_num

    def save_seasonal_bulk(self, season_num: int, data: dict) -> None:
        """Saves bulk resource values for a specified season."""
        col_name = f"season_{season_num}"
        self.ensure_season_column_exists(col_name)
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            for res_name, val in data.items():
                val_clean = str(val).strip() if str(val).strip() else "-"
                c.execute(f"UPDATE seasonal_data SET {col_name} = ? WHERE resource = ?", (val_clean, res_name))
            conn.commit()

    def clear_season_data(self, season_num: int) -> None:
        """Clears all resource values for a season and drops the empty season from the database."""
        self.delete_season(season_num)
        self.cleanup_empty_seasons()

    def export_seasonal_csv(self, file_path: str) -> None:
        """Exports the seasonal data table to a dedicated CSV file."""
        self.cleanup_empty_seasons()
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            with open(file_path, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                c.execute("PRAGMA table_info(seasonal_data)")
                headers = [info[1] for info in c.fetchall()]
                writer.writerow(headers)

                c.execute("SELECT * FROM seasonal_data ORDER BY resource ASC")
                writer.writerows(c.fetchall())

    def import_seasonal_csv(self, file_path: str) -> None:
        """Imports seasonal data from a CSV file, adding missing season columns as needed."""
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            with open(file_path, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                headers = next(reader, None)
                if not headers:
                    return

                headers = [h.strip() for h in headers]
                if not headers or headers[0].lower() != 'resource':
                    raise ValueError("CSV must have 'resource' as the first column.")

                c.execute("PRAGMA table_info(seasonal_data)")
                existing_cols = [info[1] for info in c.fetchall()]

                for row in reader:
                    if not row:
                        continue
                    row_dict = dict(zip(headers, row))
                    resource = row_dict.pop('resource', None)
                    if not resource:
                        continue

                    # Ensure resource row exists
                    c.execute("INSERT OR IGNORE INTO seasonal_data (resource) VALUES (?)", (resource,))

                    for season_col, value in row_dict.items():
                        if season_col.startswith('season_'):
                            if season_col not in existing_cols:
                                c.execute(f"ALTER TABLE seasonal_data ADD COLUMN {season_col} TEXT DEFAULT '-'")
                                existing_cols.append(season_col)
                            value_to_insert = value.strip() if value.strip() else "-"
                            c.execute(f"UPDATE seasonal_data SET {season_col} = ? WHERE resource = ?", (value_to_insert, resource))

            conn.commit()

    # --- CSV Export & Import ---

    def export_csv(self, file_path: str) -> None:
        """Exports all entities into a unified, backward-compatible CSV format."""
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            with open(file_path, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(["Type", "Name/Key", "Val1", "Val2", "Val3", "Val4", "Val5"])

                # Heroes
                c.execute("SELECT name, sterne, xp_level, dust_used, dust_needed, rarity FROM daten")
                for row in c.fetchall():
                    writer.writerow(["HERO", row[0], row[1], row[2], row[3], row[4], row[5]])

                # Pets
                c.execute("SELECT name, sterne, bond_level, feathers_used, feathers_needed FROM pets")
                for row in c.fetchall():
                    writer.writerow(["PET", row[0], row[1], row[2], row[3], row[4], ""])

                # Buildings
                c.execute("SELECT name, level FROM buildings")
                for row in c.fetchall():
                    writer.writerow(["BUILDING", row[0], row[1], "", "", "", ""])

                # Equipment
                c.execute("SELECT name, level FROM equipment")
                for row in c.fetchall():
                    writer.writerow(["EQUIPMENT", row[0], row[1], "", "", "", ""])

                # Fashion
                c.execute("SELECT name, is_unlocked FROM fashion")
                for row in c.fetchall():
                    writer.writerow(["FASHION", row[0], row[1], "", "", "", ""])

                # Secret Achievements
                c.execute("SELECT id, is_completed FROM secret_achievements")
                for row in c.fetchall():
                    writer.writerow(["ACHIEVEMENT", str(row[0]), str(row[1]), "", "", "", ""])

                # Settings
                c.execute("SELECT key, value FROM settings")
                for row in c.fetchall():
                    writer.writerow(["SETTING", row[0], row[1], "", "", "", ""])

                # Elixir
                c.execute("SELECT date, total_elixir FROM elixir_data ORDER BY date ASC")
                for row in c.fetchall():
                    writer.writerow(["ELIXIR", row[0], row[1], "", "", "", ""])

    def import_csv(self, file_path: str) -> None:
        """Imports all data from a CSV file with support for all versions."""
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            with open(file_path, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                next(reader, None)  # Skip header row

                for row in reader:
                    if not row:
                        continue
                    type_ = row[0].strip().upper()

                    if type_ == "HERO" and len(row) >= 7:
                        c.execute(
                            "UPDATE daten SET sterne=?, xp_level=?, dust_used=?, dust_needed=?, rarity=? WHERE name=?",
                            (row[2], row[3], row[4], row[5], row[6], row[1])
                        )
                    elif type_ == "PET":
                        if len(row) >= 6:
                            c.execute(
                                "UPDATE pets SET sterne=?, bond_level=?, feathers_used=?, feathers_needed=? WHERE name=?",
                                (row[2], row[3], row[4], row[5], row[1])
                            )
                        elif len(row) >= 4:
                            c.execute(
                                "UPDATE pets SET sterne=?, bond_level=? WHERE name=?",
                                (row[2], row[3], row[1])
                            )
                    elif type_ == "BUILDING" and len(row) >= 3:
                        c.execute("UPDATE buildings SET level=? WHERE name=?", (row[2], row[1]))
                    elif type_ == "EQUIPMENT" and len(row) >= 3:
                        c.execute("UPDATE equipment SET level=? WHERE name=?", (row[2], row[1]))
                    elif type_ == "FASHION" and len(row) >= 3:
                        try:
                            unlocked = int(row[2])
                            c.execute("INSERT OR REPLACE INTO fashion (name, is_unlocked) VALUES (?, ?)", (row[1], unlocked))
                        except ValueError:
                            pass
                    elif type_ == "ACHIEVEMENT" and len(row) >= 3:
                        try:
                            ach_id = int(row[1])
                            completed = int(row[2])
                            c.execute("UPDATE secret_achievements SET is_completed=? WHERE id=?", (completed, ach_id))
                        except ValueError:
                            pass
                    elif type_ == "SETTING" and len(row) >= 3:
                        c.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (row[1], row[2]))
                    elif type_ == "ELIXIR" and len(row) >= 3:
                        date_val, elixir_val = row[1], row[2]
                        c.execute("SELECT id FROM elixir_data WHERE date = ?", (date_val,))
                        existing = c.fetchone()
                        if existing:
                            c.execute("UPDATE elixir_data SET total_elixir=? WHERE id=?", (elixir_val, existing[0]))
                        else:
                            c.execute("INSERT INTO elixir_data (date, total_elixir) VALUES (?, ?)", (date_val, elixir_val))

            conn.commit()

    def export_db(self, target_path: str) -> None:
        """Exports a full raw SQLite .db backup file using the transactional backup API."""
        with sqlite3.connect(self.db_name) as source_conn:
            with sqlite3.connect(target_path) as dest_conn:
                source_conn.backup(dest_conn)

    def import_db(self, source_path: str) -> None:
        """Restores the database from a raw SQLite .db file and ensures schema migrations."""
        with sqlite3.connect(source_path) as test_conn:
            c = test_conn.cursor()
            c.execute("PRAGMA integrity_check")
            res = c.fetchone()
            if not res or res[0] != "ok":
                raise ValueError("Selected file is corrupted or not a valid SQLite database.")

            # Restore using backup API
            with sqlite3.connect(self.db_name) as current_conn:
                test_conn.backup(current_conn)

        # Run schema migrations in case an older version was restored
        self.init_db()

    def reset_all_progress(self) -> None:
        """Resets all player game progress while preserving registry structure."""
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute("UPDATE daten SET sterne='-', xp_level='-', dust_used='-', dust_needed='-'")
            c.execute("UPDATE pets SET sterne='-', bond_level='-', feathers_used='-', feathers_needed='-'")
            c.execute("UPDATE buildings SET level='-'")
            c.execute("UPDATE equipment SET level=0")
            c.execute("UPDATE fashion SET is_unlocked = CASE WHEN name = 'Default' THEN 1 ELSE 0 END")
            c.execute("UPDATE secret_achievements SET is_completed = 0")
            # Clear all seasonal data columns to '-'
            c.execute("PRAGMA table_info(seasonal_data)")
            cols = [info[1] for info in c.fetchall() if info[1].startswith("season_")]
            for col in cols:
                c.execute(f"UPDATE seasonal_data SET {col} = '-'")
            c.execute("DELETE FROM elixir_data")
            c.execute("DELETE FROM pulls_scrolls")
            c.execute("DELETE FROM pulls_eggs")
            c.execute("DELETE FROM sqlite_sequence WHERE name IN ('elixir_data', 'pulls_scrolls', 'pulls_eggs')")
            conn.commit()
