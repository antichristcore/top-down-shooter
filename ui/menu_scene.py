import arcade

from ui.widgets import Button, Slider


class MenuView(arcade.View):
    def __init__(self, window):
        super().__init__(window)
        self.settings = window.settings
        self.play_button = Button("Play", window.width / 2, window.height / 2 + 40)
        self.exit_button = Button("Exit", window.width / 2, window.height / 2 - 20)
        self.mute_button = Button("Mute", window.width / 2, window.height / 2 - 80)
        self.music_slider = Slider("Music", self.settings.music_volume, window.width / 2 - 20, window.height / 2 - 150)
        self.sfx_slider = Slider("SFX", self.settings.sfx_volume, window.width / 2 - 20, window.height / 2 - 200)

    def on_show_view(self):
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
        self.play_button.hovered = self.play_button.hit_test(x, y)
        self.exit_button.hovered = self.exit_button.hit_test(x, y)
        self.mute_button.hovered = self.mute_button.hit_test(x, y)

    def on_mouse_press(self, x, y, button, modifiers):
        if self.play_button.hit_test(x, y):
            from ui.game_scene import GameView

            self.window.show_view(GameView(self.window))
        elif self.exit_button.hit_test(x, y):
            self.window.close()
        elif self.mute_button.hit_test(x, y):
            self.settings.mute = not self.settings.mute
            self.settings.save()
        elif self.music_slider.hit_knob(x, y):
            self.music_slider.dragging = True
        elif self.sfx_slider.hit_knob(x, y):
            self.sfx_slider.dragging = True

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if self.music_slider.dragging:
            self.music_slider.set_from_x(x)
            self.settings.music_volume = self.music_slider.value
            self.settings.save()
        if self.sfx_slider.dragging:
            self.sfx_slider.set_from_x(x)
            self.settings.sfx_volume = self.sfx_slider.value
            self.settings.save()

    def on_mouse_release(self, x, y, button, modifiers):
        self.music_slider.dragging = False
        self.sfx_slider.dragging = False
