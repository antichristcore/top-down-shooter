import arcade

from systems.score_system import ScoreSystem
from systems.settings_system import SettingsSystem
from systems.user_db import UserDatabase
from ui.auth_scene import AuthView


class GameWindow(arcade.Window):
    def __init__(self, width=960, height=640, title="Top-Down Shooter"):
        super().__init__(width, height, title)
        self.settings = SettingsSystem()
        self.score_system = ScoreSystem()
        self.user_db = UserDatabase()
        self.current_user = None
        self.show_view(AuthView(self))

    def close(self):
        self.user_db.close()
        super().close()


def run():
    window = GameWindow()
    arcade.run()
    return window
