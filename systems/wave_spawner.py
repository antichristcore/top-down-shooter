import random


class WaveSpawner:
    def __init__(self, level_config, arena_bounds):
        self.level = level_config
        self.arena_bounds = arena_bounds
        self.spawn_interval = level_config["spawnIntervalSeconds"]
        self.total_waves = level_config["waves"]
        self.spawned_waves = 0
        self.spawn_timer = self.spawn_interval
        self.active = True

    def update(self, delta_time):
        if not self.active:
            return False
        self.spawn_timer -= delta_time
        if self.spawn_timer <= 0 and self.spawned_waves < self.total_waves:
            self.spawn_timer = self.spawn_interval
            self.spawned_waves += 1
            return True
        if self.spawned_waves >= self.total_waves:
            self.active = False
        return False

    def spawn_positions(self, count):
        positions = []
        for _ in range(count):
            x = random.uniform(self.arena_bounds[0] + 40, self.arena_bounds[2] - 40)
            y = random.uniform(self.arena_bounds[1] + 40, self.arena_bounds[3] - 40)
            positions.append((x, y))
        return positions

    def wave_complete(self):
        return self.spawned_waves >= self.total_waves
