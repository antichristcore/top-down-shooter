import arcade

from ui.widgets import Button


class GameOverView(arcade.View):
    def __init__(self, window, score, victory):
        super().__init__(window)
        self.score_system = window.score_system
        self.score = score
        self.victory = victory
        self.replay_button = Button("Replay", window.width / 2, window.height / 2 - 20)
        self.menu_button = Button("Menu", window.width / 2, window.height / 2 - 80)

    def on_show_view(self):
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
        self.replay_button.draw()
        self.menu_button.draw()

    def on_mouse_motion(self, x, y, dx, dy):
        self.replay_button.hovered = self.replay_button.hit_test(x, y)
        self.menu_button.hovered = self.menu_button.hit_test(x, y)

    def on_mouse_press(self, x, y, button, modifiers):
        if self.replay_button.hit_test(x, y):
            from ui.game_scene import GameView

            self.window.show_view(GameView(self.window))
        elif self.menu_button.hit_test(x, y):
            from ui.menu_scene import MenuView

            self.window.show_view(MenuView(self.window))
