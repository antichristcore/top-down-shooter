import os
import arcade
from systems.db_system import DBSystem

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "..", "assets")

class AudioSystem:
    def __init__(self, db: DBSystem, username: str):
        self.db = db
        self.username = username

        self.music_player = None
        self.music_sound = None

        self.sfx_shot = None
        self.sfx_hit = None
        self.sfx_explosion = None

        self.music_volume, self.sfx_volume, self.muted = self.db.get_settings(username)

    def load_assets(self):
        # Все файлы опциональны
        def load_sound(name: str):
            path = os.path.join(ASSETS_DIR, name)
            return arcade.load_sound(path) if os.path.exists(path) else None

        self.music_sound = load_sound("music.ogg")
        self.sfx_shot = load_sound("shot.wav")
        self.sfx_hit = load_sound("hit.wav")
        self.sfx_explosion = load_sound("explosion.wav")

    def _effective_music_volume(self) -> float:
        return 0.0 if self.muted else float(self.music_volume)

    def _effective_sfx_volume(self) -> float:
        return 0.0 if self.muted else float(self.sfx_volume)

    def play_music_loop(self):
        if not self.music_sound:
            return
        # Не запускаем второй раз
        if self.music_player and self.music_player.playing:
            return
        self.music_player = arcade.play_sound(self.music_sound, volume=self._effective_music_volume(), looping=True)

    def stop_music(self):
        try:
            if self.music_player:
                self.music_player.pause()
        except Exception:
            pass

    def play_shot(self):
        if self.sfx_shot:
            arcade.play_sound(self.sfx_shot, volume=self._effective_sfx_volume())

    def play_hit(self):
        if self.sfx_hit:
            arcade.play_sound(self.sfx_hit, volume=self._effective_sfx_volume())

    def play_explosion(self):
        if self.sfx_explosion:
            arcade.play_sound(self.sfx_explosion, volume=self._effective_sfx_volume())

    def set_music_volume(self, v: float):
        self.music_volume = max(0.0, min(1.0, float(v)))
        self.db.set_settings(self.username, self.music_volume, self.sfx_volume, self.muted)

    def set_sfx_volume(self, v: float):
        self.sfx_volume = max(0.0, min(1.0, float(v)))
        self.db.set_settings(self.username, self.music_volume, self.sfx_volume, self.muted)

    def toggle_mute(self):
        self.muted = 0 if self.muted else 1
        self.db.set_settings(self.username, self.music_volume, self.sfx_volume, self.muted)
        # Если музыка играет — "перезапустим" с новой громкостью
        if self.music_sound:
            self.stop_music()
            self.play_music_loop()
