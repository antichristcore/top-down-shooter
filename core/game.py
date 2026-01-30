import arcade

from systems.score_system import ScoreSystem
from systems.settings_system import SettingsSystem
from systems.user_db import UserDatabase
from ui.auth_scene import AuthScene
from ui.game_over_scene import GameOverScene
from ui.game_scene import GameScene
from ui.menu_scene import MenuScene


class GameWindow(arcade.Window):
    def __init__(self, width=960, height=640, title="Top-Down Shooter"):
        super().__init__(width, height, title)
        self.settings = SettingsSystem()
        self.score_system = ScoreSystem()
        self.user_db = UserDatabase()
        self.auth_view = AuthScene(self.user_db)
        self.menu_view = MenuScene(self.settings)
        self.game_view = GameScene(self.settings, self.score_system)
        self.game_over_view = GameOverScene(self.score_system)
        self.show_view(self.auth_view)

    def close(self):
        self.user_db.close()
        super().close()


def run():
    window = GameWindow()
    arcade.run()
    return window
