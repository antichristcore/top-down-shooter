import arcade
import arcade.gui as gui
from ui.widgets import CallbackButton


class MenuScene(arcade.View):
    def __init__(self, window, scene_manager, db, audio, username: str):
        super().__init__(window)
        self.scene_manager = scene_manager
        self.db = db
        self.audio = audio
        self.username = username

        self.ui = gui.UIManager()
        self.anchor = None

        self.music_slider = None
        self.sfx_slider = None
        self.mute_button = None

        self._last_music = 0.0
        self._last_sfx = 0.0

    def on_show_view(self):
        arcade.set_background_color(arcade.color.DARK_MIDNIGHT_BLUE)

        self.ui.enable()
        self.ui.clear()

        self.audio.play_music_loop()

        self.anchor = gui.UIAnchorLayout()
        vbox = gui.UIBoxLayout(space_between=12)

        vbox.add(gui.UILabel(text="TOP-DOWN SHOOTER", font_size=36, text_color=arcade.color.WHITE))

        def go_level_select():
            self.scene_manager.go("level_select")

        def do_exit():
            arcade.close_window()

        vbox.add(CallbackButton("Play", 260, go_level_select))
        vbox.add(CallbackButton("Exit", 260, do_exit))

        vbox.add(gui.UILabel(text="Music", font_size=16, text_color=arcade.color.WHITE))
        self.music_slider = gui.UISlider(
            value=float(self.audio.music_volume),
            min_value=0.0,
            max_value=1.0,
            width=260
        )
        vbox.add(self.music_slider)

        vbox.add(gui.UILabel(text="SFX", font_size=16, text_color=arcade.color.WHITE))
        self.sfx_slider = gui.UISlider(
            value=float(self.audio.sfx_volume),
            min_value=0.0,
            max_value=1.0,
            width=260
        )
        vbox.add(self.sfx_slider)

        def toggle_mute():
            self.audio.toggle_mute()
            self.mute_button.text = "Mute: ON" if self.audio.muted else "Mute: OFF"

        self.mute_button = CallbackButton(
            "Mute: ON" if self.audio.muted else "Mute: OFF",
            260,
            toggle_mute
        )
        vbox.add(self.mute_button)

        self.anchor.add(vbox, anchor_x="center_x", anchor_y="center_y")
        self.ui.add(self.anchor)

        self._last_music = float(self.music_slider.value)
        self._last_sfx = float(self.sfx_slider.value)

    def on_hide_view(self):
        self.ui.disable()

    def on_update(self, dt: float):
        mv = float(self.music_slider.value) if self.music_slider else 0.0
        sv = float(self.sfx_slider.value) if self.sfx_slider else 0.0

        if abs(mv - self._last_music) > 0.001:
            self._last_music = mv
            self.audio.set_music_volume(mv)

        if abs(sv - self._last_sfx) > 0.001:
            self._last_sfx = sv
            self.audio.set_sfx_volume(sv)

    def on_draw(self):
        self.clear()
        self.ui.draw()
