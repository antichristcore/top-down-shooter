import arcade

from ui.menu_scene import Button


class GameOverScene(arcade.View):
    def __init__(self, score_system):
        super().__init__()
        self.score_system = score_system
        self.score = 0
        self.victory = False
        self.replay_button = None
        self.menu_button = None

    def configure(self, score, victory):
        self.score = score
        self.victory = victory

    def on_show_view(self):
        center_x = self.window.width / 2
        center_y = self.window.height / 2
        self.replay_button = Button("Replay", center_x, center_y - 20)
        self.menu_button = Button("Menu", center_x, center_y - 80)
        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)

    def on_draw(self):
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
        if self.replay_button:
            self.replay_button.draw()
            self.menu_button.draw()

    def on_mouse_motion(self, x, y, dx, dy):
        if not self.replay_button:
            return
        self.replay_button.hovered = self.replay_button.hit_test(x, y)
        self.menu_button.hovered = self.menu_button.hit_test(x, y)

    def on_mouse_press(self, x, y, button, modifiers):
        if not self.replay_button:
            return
        if self.replay_button.hit_test(x, y):
            self.window.game_view.reset()
            self.window.show_view(self.window.game_view)
        elif self.menu_button.hit_test(x, y):
            self.window.show_view(self.window.menu_view)
