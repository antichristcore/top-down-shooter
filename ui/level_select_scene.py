import arcade
import arcade.gui as gui
import json
import os

from ui.widgets import CallbackButton


DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
LEVELS_PATH = os.path.join(DATA_DIR, "levels.json")


class LevelSelectScene(arcade.View):
    def __init__(self, window, scene_manager, db, audio, username: str):
        super().__init__(window)
        self.scene_manager = scene_manager
        self.db = db
        self.audio = audio
        self.username = username

        self.ui = gui.UIManager()
        self.anchor = None

        self.levels = self._load_levels()

    def _load_levels(self):
        with open(LEVELS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    def on_show_view(self):
        arcade.set_background_color(arcade.color.DARK_SLATE_BLUE)
        self.ui.enable()
        self.ui.clear()

        self.anchor = gui.UIAnchorLayout()
        vbox = gui.UIBoxLayout(space_between=10)

        vbox.add(gui.UILabel(text="SELECT LEVEL", font_size=34, text_color=arcade.color.WHITE))

        def go_back():
            self.scene_manager.go("menu")

        # кнопки уровней
        for i, lvl in enumerate(self.levels):
            name = str(lvl.get("name", f"Level {i+1}"))
            def make_cb(idx):
                def _cb():
                    # window = Game, у него есть start_game_with_level
                    self.window.start_game_with_level(idx)
                return _cb

            vbox.add(CallbackButton(name, 420, make_cb(i)))

        vbox.add(gui.UISpace(height=8))
        vbox.add(CallbackButton("Back", 260, go_back))

        self.anchor.add(vbox, anchor_x="center_x", anchor_y="center_y")
        self.ui.add(self.anchor)

    def on_hide_view(self):
        self.ui.disable()

    def on_draw(self):
        self.clear()
        self.ui.draw()
