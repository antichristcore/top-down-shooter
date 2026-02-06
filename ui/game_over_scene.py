import arcade
import arcade.gui as gui
from ui.widgets import CallbackButton


class GameOverScene(arcade.View):
    def __init__(self, window, scene_manager, db, audio, username: str,
                 score: int, best_score: int, victory: bool, results: dict):
        super().__init__(window)

        self.scene_manager = scene_manager
        self.db = db
        self.audio = audio
        self.username = username

        self.score = int(score)
        self.best_score = int(best_score)
        self.victory = bool(victory)
        self.results = results if isinstance(results, dict) else {}

        self.ui = gui.UIManager()
        self.anchor = None

    def on_show_view(self):
        arcade.set_background_color(arcade.color.DARK_GREEN if self.victory else arcade.color.DARK_RED)

        self.ui.enable()
        self.ui.clear()

        self.anchor = gui.UIAnchorLayout()
        vbox = gui.UIBoxLayout(space_between=10)

        title = "ПОБЕДА!" if self.victory else "GAME OVER"
        vbox.add(gui.UILabel(text=title, font_size=44, text_color=arcade.color.WHITE))

        vbox.add(gui.UILabel(text=f"Результат: {self.score}", font_size=20, text_color=arcade.color.WHITE))
        vbox.add(gui.UILabel(text=f"Лучший результат:  {self.best_score}", font_size=20, text_color=arcade.color.WHITE))

        vbox.add(gui.UISpace(height=8))
        vbox.add(gui.UILabel(text="РЕЗУЛЬТАТЫ", font_size=26, text_color=arcade.color.WHITE))

        time_s = float(self.results.get("time_seconds", 0.0))
        waves_spawned = int(self.results.get("waves_spawned", 0))
        waves_total = int(self.results.get("waves_total", 0))

        kills_total = int(self.results.get("kills_total", 0))
        kills_by_type = self.results.get("kills_by_type", {})
        if not isinstance(kills_by_type, dict):
            kills_by_type = {}

        shots = int(self.results.get("shots_fired", 0))
        hits = int(self.results.get("shots_hit", 0))

        accuracy = 0.0
        if shots > 0:
            accuracy = (hits / shots) * 100.0

        mm = int(time_s // 60)
        ss = int(time_s % 60)
        time_str = f"{mm:02d}:{ss:02d}"

        vbox.add(gui.UILabel(text=f"Время: {time_str}", font_size=16, text_color=arcade.color.WHITE))
        vbox.add(gui.UILabel(text=f"Волны: {waves_spawned}/{waves_total}", font_size=16, text_color=arcade.color.WHITE))
        vbox.add(gui.UILabel(text=f"Убийства: {kills_total}", font_size=16, text_color=arcade.color.WHITE))
        vbox.add(gui.UILabel(text=f"Выстрелов: {shots}   Попаданий: {hits}   Точность: {accuracy:.1f}%", font_size=16, text_color=arcade.color.WHITE))

        if len(kills_by_type) > 0:
            order = ["Боец", "Стрелок", "Заряд", "Танк"]
            parts = []
            for k in order:
                if k in kills_by_type:
                    parts.append(f"{k}:{int(kills_by_type.get(k, 0))}")
            for k in kills_by_type.keys():
                if k not in order:
                    parts.append(f"{k}:{int(kills_by_type.get(k, 0))}")

            vbox.add(gui.UILabel(text="Убийств по типу " + "  ".join(parts), font_size=14, text_color=arcade.color.WHITE))

        vbox.add(gui.UISpace(height=10))

        def replay():
            self.window.start_game_with_level(self.window.selected_level_index)

        def go_level_select():
            self.scene_manager.go("level_select")

        def go_menu():
            self.scene_manager.go("menu")

        vbox.add(CallbackButton("Повторить", 260, replay))
        vbox.add(CallbackButton("Выбор уровня", 260, go_level_select))
        vbox.add(CallbackButton("Меню", 260, go_menu))

        self.anchor.add(vbox, anchor_x="center_x", anchor_y="center_y")
        self.ui.add(self.anchor)

    def on_hide_view(self):
        self.ui.disable()

    def on_draw(self):
        self.clear()
        self.ui.draw()
