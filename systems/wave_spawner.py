import random
import math

class WaveSpawner:
    def __init__(self, level_cfg: dict, arena_w_px: int, arena_h_px: int):
        self.cfg = level_cfg
        self.arena_w_px = arena_w_px
        self.arena_h_px = arena_h_px

        self.waves_total = int(level_cfg["waves"])
        self.spawn_interval = float(level_cfg["spawnIntervalSeconds"])
        self.enemy_types = list(level_cfg["enemyTypes"])
        self.enemy_stats = dict(level_cfg["enemyStats"])

        self.wave_index = 0
        self._timer = 0.0
        self.finished_spawning = False

    def update(self, dt: float) -> bool:
        """Возвращает True, если пора спавнить волну."""
        if self.finished_spawning:
            return False
        self._timer += dt
        if self._timer >= self.spawn_interval:
            self._timer = 0.0
            self.wave_index += 1
            if self.wave_index >= self.waves_total:
                self.finished_spawning = True
            return True
        return False

    def spawn_wave(self):
        # Чем дальше уровень — тем больше врагов
        base_count = 4 + self.wave_index * 2
        # Спаун по границам арены
        enemies = []
        for _ in range(base_count):
            side = random.choice(["left", "right", "bottom", "top"])
            if side == "left":
                x = 80
                y = random.uniform(80, self.arena_h_px - 80)
            elif side == "right":
                x = self.arena_w_px - 80
                y = random.uniform(80, self.arena_h_px - 80)
            elif side == "bottom":
                x = random.uniform(80, self.arena_w_px - 80)
                y = 80
            else:
                x = random.uniform(80, self.arena_w_px - 80)
                y = self.arena_h_px - 80

            et = random.choice(self.enemy_types)
            st = self.enemy_stats.get(et, {"hp": 25, "speed": 120})
            enemies.append((et, x, y, int(st["hp"]), float(st["speed"])))
        return enemies
