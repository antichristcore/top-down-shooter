import arcade

from core.scene_manager import SceneManager
from systems.score_system import ScoreSystem
from systems.settings_system import SettingsSystem
from systems.user_db import UserDatabase
from ui.auth_scene import AuthScene
from ui.game_over_scene import GameOverScene
from ui.game_scene import GameScene
from ui.menu_scene import MenuScene


class Game(arcade.Window):
    def __init__(self, width=960, height=640, title="Top-Down Shooter"):
        super().__init__(width, height, title)
        self.manager = SceneManager()
        self.settings = SettingsSystem()
        self.score_system = ScoreSystem()
        self.user_db = UserDatabase()
        self.auth_scene = AuthScene(self, self.user_db)
        self.menu_scene = MenuScene(self, self.settings)
        self.game_scene = GameScene(self, self.settings, self.score_system)
        self.game_over_scene = GameOverScene(self, self.score_system)
        self.manager.add("auth", self.auth_scene)
        self.manager.add("menu", self.menu_scene)
        self.manager.add("game", self.game_scene)
        self.manager.add("game_over", self.game_over_scene)
        self.manager.show("auth")

    def on_draw(self):
        self.manager.draw()

    def on_update(self, delta_time):
        self.manager.update(delta_time)

    def on_key_press(self, key, modifiers):
        self.manager.on_key_press(key, modifiers)

    def on_key_release(self, key, modifiers):
        self.manager.on_key_release(key, modifiers)

    def on_mouse_press(self, x, y, button, modifiers):
        self.manager.on_mouse_press(x, y, button, modifiers)

    def on_mouse_release(self, x, y, button, modifiers):
        self.manager.on_mouse_release(x, y, button, modifiers)

    def on_mouse_motion(self, x, y, dx, dy):
        self.manager.on_mouse_motion(x, y, dx, dy)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.manager.on_mouse_drag(x, y, dx, dy, buttons, modifiers)

    def close(self):
        self.user_db.close()
        super().close()


def run():
    game = Game()
    arcade.run()
    return game
