import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path("users.db")


class UserDatabase:
    def __init__(self):
        self.connection = sqlite3.connect(DB_PATH)
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                last_login TEXT NOT NULL
            )
            """
        )
        self.connection.commit()

    def ensure_user(self, username):
        username = username.strip()
        if not username:
            raise ValueError("Username cannot be empty")
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor = self.connection.cursor()
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        if row:
            cursor.execute("UPDATE users SET last_login = ? WHERE id = ?", (now, row[0]))
        else:
            cursor.execute("INSERT INTO users (username, last_login) VALUES (?, ?)", (username, now))
        self.connection.commit()
        return username

    def close(self):
        self.connection.close()
