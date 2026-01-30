import sqlite3
from typing import Optional, Tuple

class DBSystem:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def init_schema(self):
        with self._connect() as con:
            cur = con.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users(
                    username TEXT PRIMARY KEY
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS settings(
                    username TEXT PRIMARY KEY,
                    music_volume REAL NOT NULL DEFAULT 0.6,
                    sfx_volume REAL NOT NULL DEFAULT 0.8,
                    muted INTEGER NOT NULL DEFAULT 0,
                    FOREIGN KEY(username) REFERENCES users(username)
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS highscores(
                    username TEXT PRIMARY KEY,
                    best_score INTEGER NOT NULL DEFAULT 0,
                    FOREIGN KEY(username) REFERENCES users(username)
                )
            """)
            con.commit()

    def get_or_create_default_user(self) -> str:
        # Для простоты: один пользователь "player". Можно расширить вводом имени в меню.
        username = "player"
        self.ensure_user(username)
        return username

    def ensure_user(self, username: str):
        with self._connect() as con:
            cur = con.cursor()
            cur.execute("INSERT OR IGNORE INTO users(username) VALUES(?)", (username,))
            cur.execute("INSERT OR IGNORE INTO settings(username) VALUES(?)", (username,))
            cur.execute("INSERT OR IGNORE INTO highscores(username) VALUES(?)", (username,))
            con.commit()

    def get_settings(self, username: str) -> Tuple[float, float, int]:
        self.ensure_user(username)
        with self._connect() as con:
            cur = con.cursor()
            cur.execute("SELECT music_volume, sfx_volume, muted FROM settings WHERE username=?", (username,))
            row = cur.fetchone()
            return float(row[0]), float(row[1]), int(row[2])

    def set_settings(self, username: str, music_volume: float, sfx_volume: float, muted: int):
        self.ensure_user(username)
        with self._connect() as con:
            cur = con.cursor()
            cur.execute("""
                UPDATE settings SET music_volume=?, sfx_volume=?, muted=? WHERE username=?
            """, (float(music_volume), float(sfx_volume), int(muted), username))
            con.commit()

    def get_best_score(self, username: str) -> int:
        self.ensure_user(username)
        with self._connect() as con:
            cur = con.cursor()
            cur.execute("SELECT best_score FROM highscores WHERE username=?", (username,))
            row = cur.fetchone()
            return int(row[0]) if row else 0

    def try_set_best_score(self, username: str, score: int) -> int:
        """Возвращает актуальный рекорд после обновления."""
        best = self.get_best_score(username)
        if score > best:
            with self._connect() as con:
                cur = con.cursor()
                cur.execute("UPDATE highscores SET best_score=? WHERE username=?", (int(score), username))
                con.commit()
            return score
        return best
