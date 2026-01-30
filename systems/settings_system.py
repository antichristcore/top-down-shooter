import json
from pathlib import Path

SETTINGS_PATH = Path("settings.txt")


class SettingsSystem:
    def __init__(self):
        self.music_volume = 0.6
        self.sfx_volume = 0.7
        self.mute = False
        self.load()

    def load(self):
        if not SETTINGS_PATH.exists():
            return
        data = json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
        self.music_volume = float(data.get("music_volume", 0.6))
        self.sfx_volume = float(data.get("sfx_volume", 0.7))
        self.mute = bool(data.get("mute", False))

    def save(self):
        data = {
            "music_volume": self.music_volume,
            "sfx_volume": self.sfx_volume,
            "mute": self.mute,
        }
        SETTINGS_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def effective_music_volume(self):
        return 0 if self.mute else self.music_volume

    def effective_sfx_volume(self):
        return 0 if self.mute else self.sfx_volume
