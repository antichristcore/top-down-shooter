import json
import random
from pathlib import Path

import arcade
from arcade.camera import Camera

from entities.enemy import Enemy
from entities.player import Player
from systems.collision_system import circle_circle, resolve_soft_push
from systems.math_utils import Vector2
from systems.particle_system import ParticleSystem
from systems.wave_spawner import WaveSpawner
from ui.base_scene import BaseScene

LEVELS_PATH = Path("data/levels.json")
TILE_SIZE = 32
SFX_PATHS = {
    "shot": Path("assets/shot.wav"),
    "hit": Path("assets/hit.wav"),
    "explosion": Path("assets/explosion.wav"),
}
MUSIC_PATH = Path("assets/music.ogg")


class GameScene(BaseScene):
    def __init__(self, window, settings, score_system):
        super().__init__(window)
        self.settings = settings
        self.score_system = score_system
        self.camera = Camera(window.width, window.height)
        self.gui_camera = Camera(window.width, window.height)
        self.levels = []
        self.level_index = 0
        self.level_config = None
        self.arena_bounds = (0, 0, 0, 0)
        self.player = None
        self.enemies = []
        self.projectiles = []
        self.enemy_projectiles = []
        self.particles = ParticleSystem()
        self.wave_spawner = None
        self.score = 0
        self.move_keys = set()
        self.contact_damage_timer = 0
        self.mouse_world = Vector2(0, 0)
        self.sfx = {}
        self.music = None
        self.load_levels()
        self.load_audio()

    def load_levels(self):
        data = json.loads(LEVELS_PATH.read_text(encoding="utf-8"))
        self.levels = data

    def load_audio(self):
        for key, path in SFX_PATHS.items():
            if path.exists():
                self.sfx[key] = arcade.load_sound(str(path))
        if MUSIC_PATH.exists():
            self.music = arcade.load_sound(str(MUSIC_PATH))

    def play_music(self):
        if not self.music:
            return
        volume = self.settings.effective_music_volume()
        if volume <= 0:
            return
        self.music.play(volume=volume, loop=True)

    def play_sfx(self, name):
        sound = self.sfx.get(name)
        if not sound:
            return
        volume = self.settings.effective_sfx_volume()
        if volume <= 0:
            return
        sound.play(volume=volume)

    def on_show(self, **kwargs):
        self.level_index = kwargs.get("level_index", 0)
        self.score = 0
        self.start_level(self.level_index)
        arcade.set_background_color(arcade.color.DARK_SAND)
        self.play_music()

    def on_hide(self):
        if self.music:
            self.music.stop()

    def start_level(self, index):
        self.level_config = self.levels[index]
        width = self.level_config["arenaWidth"] * TILE_SIZE
        height = self.level_config["arenaHeight"] * TILE_SIZE
        self.arena_bounds = (0, 0, width, height)
        start_pos = (width / 2, height / 2)
        self.player = Player(start_pos)
        self.enemies = []
        self.projectiles = []
        self.enemy_projectiles = []
        self.particles = ParticleSystem()
        self.wave_spawner = WaveSpawner(self.level_config, self.arena_bounds)
        self.contact_damage_timer = 0

    def update(self, delta_time):
        move_vector = Vector2(0, 0)
        if arcade.key.W in self.move_keys or arcade.key.UP in self.move_keys:
            move_vector.y += 1
        if arcade.key.S in self.move_keys or arcade.key.DOWN in self.move_keys:
            move_vector.y -= 1
        if arcade.key.A in self.move_keys or arcade.key.LEFT in self.move_keys:
            move_vector.x -= 1
        if arcade.key.D in self.move_keys or arcade.key.RIGHT in self.move_keys:
            move_vector.x += 1
        self.player.update(delta_time, move_vector, self.arena_bounds)

        self.update_camera()
        self.spawn_waves(delta_time)
        self.update_enemies(delta_time)
        self.update_projectiles(delta_time)
        self.handle_collisions(delta_time)
        self.particles.update(delta_time)
        self.check_win_loss()

    def update_camera(self):
        target_x = self.player.position.x - self.window.width / 2
        target_y = self.player.position.y - self.window.height / 2
        max_x = self.arena_bounds[2] - self.window.width
        max_y = self.arena_bounds[3] - self.window.height
        target_x = max(0, min(target_x, max_x))
        target_y = max(0, min(target_y, max_y))
        self.camera.move_to((target_x, target_y), 0.15)

    def spawn_waves(self, delta_time):
        if not self.wave_spawner:
            return
        should_spawn = self.wave_spawner.update(delta_time)
        if should_spawn:
            wave_size = 3 + self.wave_spawner.spawned_waves * 2
            positions = self.wave_spawner.spawn_positions(wave_size)
            for pos in positions:
                enemy_type = random.choice(self.level_config["enemyTypes"])
                stats = self.level_config["enemyStats"].get(enemy_type, {})
                self.enemies.append(Enemy(enemy_type, pos, stats))

    def update_enemies(self, delta_time):
        for enemy in list(self.enemies):
            enemy.update(delta_time, self.player.position, self.arena_bounds)
            projectile = enemy.maybe_shoot(delta_time, self.player.position)
            if projectile:
                self.enemy_projectiles.append(projectile)
            if not enemy.is_alive():
                self.enemies.remove(enemy)
                self.score += 10
                self.particles.spawn_explosion((enemy.position.x, enemy.position.y))
                self.play_sfx("explosion")

    def update_projectiles(self, delta_time):
        for projectile in list(self.projectiles):
            projectile.update(delta_time, self.arena_bounds)
            if not projectile.alive:
                self.projectiles.remove(projectile)
        for projectile in list(self.enemy_projectiles):
            projectile.update(delta_time, self.arena_bounds)
            if not projectile.alive:
                self.enemy_projectiles.remove(projectile)

    def handle_collisions(self, delta_time):
        for projectile in list(self.projectiles):
            for enemy in list(self.enemies):
                if circle_circle(projectile.position, projectile.radius, enemy.position, enemy.radius):
                    enemy.take_damage(projectile.damage)
                    enemy.apply_knockback(enemy.position - projectile.position, projectile.knockback)
                    projectile.alive = False
                    self.particles.spawn_hit((enemy.position.x, enemy.position.y))
                    self.play_sfx("hit")
                    break
        for projectile in list(self.enemy_projectiles):
            if circle_circle(projectile.position, projectile.radius, self.player.position, self.player.radius):
                self.player.hp -= projectile.damage
                projectile.alive = False
                self.particles.spawn_hit((self.player.position.x, self.player.position.y), color=arcade.color.CYAN)
                self.play_sfx("hit")

        for enemy in self.enemies:
            push_player, push_enemy = resolve_soft_push(self.player.position, self.player.radius, enemy.position, enemy.radius)
            self.player.position += push_player
            enemy.position += push_enemy
        self.contact_damage_timer = max(0, self.contact_damage_timer - delta_time)
        if self.contact_damage_timer <= 0:
            for enemy in self.enemies:
                if circle_circle(self.player.position, self.player.radius, enemy.position, enemy.radius):
                    self.player.hp -= 1
                    self.contact_damage_timer = 0.5
                    break

    def check_win_loss(self):
        if self.player.hp <= 0:
            self.score_system.submit(self.score)
            self.manager.show("game_over", score=self.score, victory=False)
            return
        if self.wave_spawner and self.wave_spawner.wave_complete() and not self.enemies:
            if self.level_index + 1 < len(self.levels):
                self.level_index += 1
                self.start_level(self.level_index)
            else:
                self.score_system.submit(self.score)
                self.manager.show("game_over", score=self.score, victory=True)

    def draw(self):
        self.window.clear()
        self.camera.use()
        self.draw_arena()
        self.player.draw()
        for enemy in self.enemies:
            enemy.draw()
        for projectile in self.projectiles:
            projectile.draw()
        for projectile in self.enemy_projectiles:
            projectile.draw()
        self.particles.draw()
        self.gui_camera.use()
        self.draw_hud()

    def draw_arena(self):
        width = self.arena_bounds[2]
        height = self.arena_bounds[3]
        arcade.draw_rectangle_filled(width / 2, height / 2, width, height, arcade.color.DARK_SAND)
        arcade.draw_rectangle_outline(width / 2, height / 2, width, height, arcade.color.BLACK, 4)

    def draw_hud(self):
        arcade.draw_text(
            f"HP: {self.player.hp}/{self.player.max_hp}",
            20,
            self.window.height - 30,
            arcade.color.WHITE,
            14,
        )
        arcade.draw_text(
            f"Score: {self.score}",
            20,
            self.window.height - 55,
            arcade.color.WHITE,
            14,
        )
        if self.wave_spawner:
            arcade.draw_text(
                f"Wave: {self.wave_spawner.spawned_waves}/{self.wave_spawner.total_waves}",
                20,
                self.window.height - 80,
                arcade.color.WHITE,
                14,
            )
        arcade.draw_text(
            self.level_config["name"],
            self.window.width - 20,
            self.window.height - 30,
            arcade.color.WHITE,
            14,
            anchor_x="right",
        )

    def on_key_press(self, key, modifiers):
        self.move_keys.add(key)
        if key == arcade.key.SPACE:
            projectile = self.player.shoot(self.mouse_world)
            if projectile:
                self.projectiles.append(projectile)
                self.play_sfx("shot")

    def on_key_release(self, key, modifiers):
        if key in self.move_keys:
            self.move_keys.remove(key)

    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            world = self.camera.screen_to_world((x, y))
            projectile = self.player.shoot(world)
            if projectile:
                self.projectiles.append(projectile)
                self.play_sfx("shot")

    def on_mouse_motion(self, x, y, dx, dy):
        self.mouse_world = Vector2(*self.camera.screen_to_world((x, y)))

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.on_mouse_motion(x, y, dx, dy)
