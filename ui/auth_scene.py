import arcade

from ui.base_scene import BaseScene


class AuthScene(BaseScene):
    def __init__(self, window, user_db):
        super().__init__(window)
        self.user_db = user_db
        self.username = ""
        self.message = "Введите логин и нажмите Enter"

    def on_show(self, **kwargs):
        self.username = ""
        self.message = "Введите логин и нажмите Enter"
        arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)

    def draw(self):
        arcade.start_render()
        arcade.draw_text(
            "Авторизация",
            self.window.width / 2,
            self.window.height - 140,
            arcade.color.WHITE,
            28,
            anchor_x="center",
        )
        arcade.draw_text(
            "Логин:",
            self.window.width / 2 - 160,
            self.window.height / 2 + 20,
            arcade.color.LIGHT_GRAY,
            16,
        )
        arcade.draw_rectangle_outline(
            self.window.width / 2 + 10,
            self.window.height / 2 + 28,
            260,
            36,
            arcade.color.WHITE,
            2,
        )
        arcade.draw_text(
            self.username,
            self.window.width / 2 - 110,
            self.window.height / 2 + 18,
            arcade.color.WHITE,
            16,
        )
        arcade.draw_text(
            self.message,
            self.window.width / 2,
            self.window.height / 2 - 40,
            arcade.color.LIGHT_GRAY,
            14,
            anchor_x="center",
        )

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ENTER:
            try:
                self.user_db.ensure_user(self.username)
            except ValueError:
                self.message = "Логин не может быть пустым"
                return
            self.manager.show("menu")
            return
        if key == arcade.key.BACKSPACE:
            self.username = self.username[:-1]
            return
        if key in (arcade.key.ESCAPE, arcade.key.TAB):
            return
        char = chr(key) if 32 <= key <= 126 else ""
        if char:
            self.username += char
