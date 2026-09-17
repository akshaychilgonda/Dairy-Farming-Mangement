"""
database.py
------------
Handles everything related to the SQLite database:
 - creating the connection
 - creating all tables (schema) if they do not already exist
 - small generic helper functions used by every page
   (fetch_df, execute, execute_many, get_setting, set_setting)

Using SQLite keeps this beginner-friendly and needs ZERO server setup.
If you later want MySQL, only this file needs to change.
"""

import sqlite3
import hashlib
import pandas as pd
from datetime import datetime
from config import DB_PATH


def get_connection():
    """Return a new SQLite connection with foreign keys enabled."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db():
    """
    Create every table used by the application, only if it does not exist yet.
    Safe to call every time the app starts (no data loss).
    """
    conn = get_connection()
    cur = conn.cursor()

    # ---------------- USERS ----------------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'Farmer',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # ---------------- ANIMALS ----------------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS animals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tag_number TEXT UNIQUE NOT NULL,
            name TEXT,
            animal_type TEXT NOT NULL,
            breed TEXT,
            gender TEXT,
            dob DATE,
            purchase_date DATE,
            purchase_price REAL DEFAULT 0,
            current_weight REAL,
            lactation_number INTEGER DEFAULT 0,
            pregnancy_status TEXT DEFAULT 'Not Pregnant',
            expected_calving_date DATE,
            health_status TEXT DEFAULT 'Healthy',
            photo_path TEXT,
            notes TEXT,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # ---------------- MILK PRODUCTION ----------------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS milk_production (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            animal_id INTEGER NOT NULL,
            date DATE NOT NULL,
            morning_milk REAL DEFAULT 0,
            evening_milk REAL DEFAULT 0,
            total_milk REAL DEFAULT 0,
            fat REAL,
            snf REAL,
            price_per_liter REAL DEFAULT 0,
            total_income REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (animal_id) REFERENCES animals(id) ON DELETE CASCADE
        );
    """)

    # ---------------- FEED RECORDS (daily feeding log) ----------------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS feed_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            animal_group TEXT,
            feed_type TEXT NOT NULL,
            quantity REAL NOT NULL,
            unit TEXT,
            feeding_time TEXT,
            cost REAL DEFAULT 0,
            date DATE NOT NULL,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # ---------------- FEED INVENTORY (stock) ----------------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS feed_inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            feed_name TEXT NOT NULL,
            current_quantity REAL DEFAULT 0,
            unit TEXT,
            purchase_date DATE,
            purchase_price REAL DEFAULT 0,
            supplier TEXT,
            min_stock_level REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # ---------------- HEALTH RECORDS ----------------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS health_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            animal_id INTEGER NOT NULL,
            date DATE NOT NULL,
            symptoms TEXT,
            disease TEXT,
            temperature REAL,
            vet_doctor TEXT,
            medicine TEXT,
            dosage TEXT,
            treatment_start DATE,
            treatment_end DATE,
            cost REAL DEFAULT 0,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (animal_id) REFERENCES animals(id) ON DELETE CASCADE
        );
    """)

    # ---------------- VACCINATIONS ----------------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS vaccinations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            animal_id INTEGER NOT NULL,
            vaccine_name TEXT NOT NULL,
            previous_date DATE,
            next_date DATE,
            notes TEXT,
            status TEXT DEFAULT 'Pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (animal_id) REFERENCES animals(id) ON DELETE CASCADE
        );
    """)

    # ---------------- BREEDING RECORDS ----------------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS breeding_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            animal_id INTEGER NOT NULL,
            heat_date DATE,
            ai_date DATE,
            bull_info TEXT,
            pregnancy_confirm_date DATE,
            expected_calving_date DATE,
            actual_calving_date DATE,
            calf_info TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (animal_id) REFERENCES animals(id) ON DELETE CASCADE
        );
    """)

    # ---------------- EXPENSES ----------------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            amount REAL NOT NULL,
            animal_id INTEGER,
            payment_method TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (animal_id) REFERENCES animals(id) ON DELETE SET NULL
        );
    """)

    # ---------------- INCOME ----------------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS income (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE NOT NULL,
            income_type TEXT NOT NULL,
            amount REAL NOT NULL,
            customer TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # ---------------- TASKS ----------------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_name TEXT NOT NULL,
            category TEXT DEFAULT 'Custom',
            due_date DATE NOT NULL,
            due_time TEXT,
            status TEXT DEFAULT 'Pending',
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # ---------------- ALERTS / REMINDERS (custom, user-created) ----------------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            alert_type TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            reminder_date DATE NOT NULL,
            reminder_time TEXT,
            level TEXT DEFAULT 'Upcoming',
            status TEXT DEFAULT 'Pending',
            animal_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (animal_id) REFERENCES animals(id) ON DELETE SET NULL
        );
    """)

    # ---------------- SETTINGS (key/value store) ----------------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT UNIQUE NOT NULL,
            value TEXT
        );
    """)

    conn.commit()

    # Create a default farmer login (username: farmer / password: farmer123) if no users exist
    cur.execute("SELECT COUNT(*) FROM users;")
    if cur.fetchone()[0] == 0:
        cur.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            ("farmer", hash_password("farmer123"), "Admin"),
        )
        conn.commit()

    # Default settings
    default_settings = {
        "language": "English",
        "enable_inapp_notifications": "1",
        "enable_email_notifications": "0",
        "enable_whatsapp_notifications": "0",
        "notification_email": "",
        "farm_name": "My Dairy Farm",
        "vaccination_due_soon_days": "7",
        "vaccination_upcoming_days": "30",
    }
    for k, v in default_settings.items():
        cur.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", (k, v))
    conn.commit()
    conn.close()


# ---------------------------------------------------------------
# GENERIC HELPERS (used everywhere so pages stay short & simple)
# ---------------------------------------------------------------
def fetch_df(query, params=()):
    """Run a SELECT query and return the result as a pandas DataFrame."""
    conn = get_connection()
    try:
        df = pd.read_sql_query(query, conn, params=params)
    finally:
        conn.close()
    return df


def execute(query, params=()):
    """Run an INSERT / UPDATE / DELETE query. Returns the last row id."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(query, params)
        conn.commit()
        last_id = cur.lastrowid
    finally:
        conn.close()
    return last_id


def get_setting(key, default=None):
    df = fetch_df("SELECT value FROM settings WHERE key = ?", (key,))
    if len(df) == 0:
        return default
    return df.iloc[0]["value"]


def set_setting(key, value):
    execute(
        "INSERT INTO settings (key, value) VALUES (?, ?) "
        "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
        (key, str(value)),
    )


def hash_password(password: str) -> str:
    """Simple SHA-256 hashing — good enough for a single-farm local app."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def verify_user(username: str, password: str) -> bool:
    df = fetch_df("SELECT password_hash FROM users WHERE username = ?", (username,))
    if len(df) == 0:
        return False
    return df.iloc[0]["password_hash"] == hash_password(password)


def get_animal_options():
    """Return list of (id, 'TAG - Name') tuples for select boxes."""
    df = fetch_df("SELECT id, tag_number, name FROM animals WHERE is_active = 1 ORDER BY tag_number")
    options = [(int(r.id), f"{r.tag_number} - {r.name or 'Unnamed'}") for r in df.itertuples()]
    return options
