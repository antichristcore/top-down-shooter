import arcade


class Button:
    def __init__(self, text, center_x, center_y, width=180, height=44):
        self.text = text
        self.center_x = center_x
        self.center_y = center_y
        self.width = width
        self.height = height
        self.hovered = False

    def hit_test(self, x, y):
        return (
            self.center_x - self.width / 2 <= x <= self.center_x + self.width / 2
            and self.center_y - self.height / 2 <= y <= self.center_y + self.height / 2
        )

    def draw(self):
        color = arcade.color.ALMOND if self.hovered else arcade.color.DARK_SLATE_BLUE
        arcade.draw_rectangle_filled(self.center_x, self.center_y, self.width, self.height, color)
        arcade.draw_text(
            self.text,
            self.center_x,
            self.center_y,
            arcade.color.WHITE,
            14,
            anchor_x="center",
            anchor_y="center",
        )


class Slider:
    def __init__(self, label, value, center_x, center_y, width=220):
        self.label = label
        self.value = value
        self.center_x = center_x
        self.center_y = center_y
        self.width = width
        self.dragging = False

    def set_from_x(self, x):
        left = self.center_x - self.width / 2
        self.value = max(0.0, min(1.0, (x - left) / self.width))

    def hit_knob(self, x, y):
        knob_x = self.center_x - self.width / 2 + self.value * self.width
        return (abs(x - knob_x) < 12) and (abs(y - self.center_y) < 12)

    def draw(self):
        left = self.center_x - self.width / 2
        right = self.center_x + self.width / 2
        arcade.draw_text(self.label, left, self.center_y + 16, arcade.color.WHITE, 12)
        arcade.draw_line(left, self.center_y, right, self.center_y, arcade.color.GRAY, 4)
        knob_x = left + self.value * self.width
        arcade.draw_circle_filled(knob_x, self.center_y, 8, arcade.color.SKY_BLUE)
        arcade.draw_text(f"{int(self.value * 100)}%", right + 10, self.center_y - 8, arcade.color.WHITE, 12)


class MenuScene(arcade.View):
    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        self.play_button = None
        self.exit_button = None
        self.mute_button = None
        self.music_slider = None
        self.sfx_slider = None

    def on_show_view(self):
        center_x = self.window.width / 2
        center_y = self.window.height / 2
        self.play_button = Button("Play", center_x, center_y + 40)
        self.exit_button = Button("Exit", center_x, center_y - 20)
        self.mute_button = Button("Mute", center_x, center_y - 80)
        self.music_slider = Slider("Music", self.settings.music_volume, center_x - 20, center_y - 150)
        self.sfx_slider = Slider("SFX", self.settings.sfx_volume, center_x - 20, center_y - 200)
        arcade.set_background_color(arcade.color.DARK_MIDNIGHT_BLUE)

    def on_draw(self):
        self.window.clear()
        arcade.draw_text(
            "Top-Down Shooter",
            self.window.width / 2,
            self.window.height - 120,
            arcade.color.WHITE,
            32,
            anchor_x="center",
        )
        self.play_button.draw()
        self.exit_button.draw()
        self.mute_button.draw()
        self.music_slider.draw()
        self.sfx_slider.draw()
        mute_state = "ON" if self.settings.mute else "OFF"
        arcade.draw_text(
            f"Mute: {mute_state}",
            self.window.width / 2 + 110,
            self.window.height / 2 - 88,
            arcade.color.WHITE,
            12,
        )

    def on_mouse_motion(self, x, y, dx, dy):
        if not self.play_button:
            return
        self.play_button.hovered = self.play_button.hit_test(x, y)
        self.exit_button.hovered = self.exit_button.hit_test(x, y)
        self.mute_button.hovered = self.mute_button.hit_test(x, y)

    def on_mouse_press(self, x, y, button, modifiers):
        if not self.play_button:
            return
        if self.play_button.hit_test(x, y):
            self.window.show_view(self.window.game_view)
        elif self.exit_button.hit_test(x, y):
            self.window.close()
        elif self.mute_button.hit_test(x, y):
            self.settings.mute = not self.settings.mute
            self.settings.save()
        elif self.music_slider and self.music_slider.hit_knob(x, y):
            self.music_slider.dragging = True
        elif self.sfx_slider and self.sfx_slider.hit_knob(x, y):
            self.sfx_slider.dragging = True

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if not self.music_slider:
            return
        if self.music_slider.dragging:
            self.music_slider.set_from_x(x)
            self.settings.music_volume = self.music_slider.value
            self.settings.save()
        if self.sfx_slider.dragging:
            self.sfx_slider.set_from_x(x)
            self.settings.sfx_volume = self.sfx_slider.value
            self.settings.save()

    def on_mouse_release(self, x, y, button, modifiers):
        if not self.music_slider:
            return
        self.music_slider.dragging = False
        self.sfx_slider.dragging = False
