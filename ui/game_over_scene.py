import arcade

from ui.base_scene import BaseScene
from ui.menu_scene import Button


class GameOverScene(BaseScene):
    def __init__(self, window, score_system):
        super().__init__(window)
        self.score_system = score_system
        self.score = 0
        self.victory = False
        self.replay_button = Button("Replay", window.width / 2, window.height / 2 - 20)
        self.menu_button = Button("Menu", window.width / 2, window.height / 2 - 80)

    def on_show(self, **kwargs):
        self.score = kwargs.get("score", 0)
        self.victory = kwargs.get("victory", False)
        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)

    def draw(self):
        self.window.clear()
        title = "Victory!" if self.victory else "Game Over"
        arcade.draw_text(title, self.window.width / 2, self.window.height - 140, arcade.color.WHITE, 32, anchor_x="center")
        arcade.draw_text(
            f"Score: {self.score}",
            self.window.width / 2,
            self.window.height / 2 + 40,
            arcade.color.WHITE,
            20,
            anchor_x="center",
        )
        arcade.draw_text(
            f"Best: {self.score_system.best_score}",
            self.window.width / 2,
            self.window.height / 2 + 10,
            arcade.color.LIGHT_GRAY,
            16,
            anchor_x="center",
        )
        self.replay_button.draw()
        self.menu_button.draw()

    def on_mouse_motion(self, x, y, dx, dy):
        self.replay_button.hovered = self.replay_button.hit_test(x, y)
        self.menu_button.hovered = self.menu_button.hit_test(x, y)

    def on_mouse_press(self, x, y, button, modifiers):
        if self.replay_button.hit_test(x, y):
            self.manager.show("game")
        elif self.menu_button.hit_test(x, y):
            self.manager.show("menu")
