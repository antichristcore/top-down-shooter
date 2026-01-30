import arcade
from core.settings import GameConfig
from core.scene_manager import SceneManager
from systems.db_system import DBSystem
from systems.audio_system import AudioSystem

from ui.menu_scene import MenuScene
from ui.level_select_scene import LevelSelectScene
from ui.game_scene import GameScene
from ui.game_over_scene import GameOverScene


class Game(arcade.Window):
    def __init__(self):
        self.cfg = GameConfig()
        super().__init__(
            self.cfg.screen_width,
            self.cfg.screen_height,
            self.cfg.title,
            resizable=False,
            update_rate=1 / 120
        )

        arcade.set_background_color(arcade.color.BLACK)

        self.scene_manager = SceneManager(self)

        self.db = DBSystem(db_path="top_down_shooter.db")
        self.db.init_schema()

        self.username = self.db.get_or_create_default_user()

        self.audio = AudioSystem(self.db, self.username)
        self.audio.load_assets()

        # выбранный уровень
        self.selected_level_index = 0

        # результаты для экрана GameOver/Results
        self._pending_game_over_score = 0
        self._pending_game_over_best = 0
        self._pending_game_over_victory = False
        self._pending_game_over_results = {}

        self.scene_manager.register(
            "menu",
            lambda: MenuScene(self, self.scene_manager, self.db, self.audio, self.username)
        )
        self.scene_manager.register(
            "level_select",
            lambda: LevelSelectScene(self, self.scene_manager, self.db, self.audio, self.username)
        )
        self.scene_manager.register(
            "game",
            lambda: GameScene(self, self.scene_manager, self.db, self.audio, self.username, self.selected_level_index)
        )
        self.scene_manager.register(
            "game_over",
            lambda: GameOverScene(
                self, self.scene_manager, self.db, self.audio, self.username,
                self._pending_game_over_score,
                self._pending_game_over_best,
                self._pending_game_over_victory,
                self._pending_game_over_results
            )
        )

    def start_game_with_level(self, level_index: int):
        self.selected_level_index = int(level_index)
        self.scene_manager.go("game")

    def open_game_over(self, score: int, best_score: int, victory: bool, results: dict):
        self._pending_game_over_score = int(score)
        self._pending_game_over_best = int(best_score)
        self._pending_game_over_victory = bool(victory)
        self._pending_game_over_results = results if isinstance(results, dict) else {}
        self.scene_manager.go("game_over")

    def run(self):
        self.scene_manager.go("menu")
        arcade.run()
