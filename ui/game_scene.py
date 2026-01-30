import arcade
import json
import os
import random
import math

from arcade.camera import Camera2D

from core.settings import GameConfig
from systems.aabb import AABB
from systems.collision_system import circle_circle_hit, circle_aabb_hit, soft_separate_circles
from systems.score_system import ScoreSystem

from entities.player import Player
from entities.enemy import Enemy
from entities.wall import Wall
from entities.particle import Particle


DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
LEVELS_PATH = os.path.join(DATA_DIR, "levels.json")


class GameScene(arcade.View):
    def __init__(self, window, scene_manager, db, audio, username: str, level_index: int):
        super().__init__(window)

        self.scene_manager = scene_manager
        self.db = db
        self.audio = audio
        self.username = username

        self.cfg = GameConfig()

        self.levels = self._load_levels()
        self.level_index = int(level_index)
        if self.level_index < 0:
            self.level_index = 0
        if self.level_index >= len(self.levels):
            self.level_index = 0
        self.level_cfg = self.levels[self.level_index]

        self.tile = int(self.cfg.tile_size)
        self.arena_w_px = int(self.level_cfg["arenaWidth"]) * self.tile
        self.arena_h_px = int(self.level_cfg["arenaHeight"]) * self.tile

        self.camera = Camera2D()

        self.player = Player(
            x=self.arena_w_px / 2,
            y=self.arena_h_px / 2,
            radius=self.cfg.player_radius,
            speed=self.cfg.player_speed,
            hp=self.cfg.player_hp
        )
        self._player_hp_start = int(self.player.hp)

        self.enemies = []
        self.projectiles = []
        self.enemy_projectiles = []
        self.particles = []

        # ✅ контактный урон игрока (по врагам)
        self.player_contact_damage = getattr(self.cfg, "player_contact_damage", 8)

        # Waves
        self.waves_total = int(self.level_cfg.get("waves", 3))
        self.spawn_interval = float(self.level_cfg.get("spawnIntervalSeconds", 3.0))
        self.enemy_types = list(self.level_cfg.get("enemyTypes", ["melee"]))
        self.enemy_stats = dict(self.level_cfg.get("enemyStats", {}))

        self.waves_spawned = 0
        self._wave_wait_timer = 0.25
        self._waiting_next_wave = True
        self._just_cleared = False

        self.score = ScoreSystem()

        # Maze
        self.maze_is_active = False
        self.maze_floor_points = []

        # Ring
        self.ring_is_active = False
        self._ring_cx = 0.0
        self._ring_cy = 0.0
        self._ring_w = 0.0
        self._ring_h = 0.0

        # Results stats (копим по всей кампании тоже)
        self.time_seconds = 0.0
        self.shots_fired = 0
        self.shots_hit = 0
        self.kills_total = 0
        self.kills_by_type = {}

        self.walls = self._build_walls_for_level()
        self.wall_objs = [Wall(r) for r in self.walls]

        self._place_player_safe()

        self.mouse_world_x = float(self.player.x)
        self.mouse_world_y = float(self.player.y)

        self._contact_timer = 0.0
        self._shooting = False
        self._level_intro_timer = 0.8

    def _load_levels(self):
        with open(LEVELS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    # ------------------------------------------------------------
    # Screen -> World
    # ------------------------------------------------------------

    def _screen_to_world(self, sx: float, sy: float):
        try:
            cx, cy = self.camera.position
        except Exception:
            cx = self.player.x
            cy = self.player.y

        zoom = 1.0
        try:
            zoom = float(self.camera.zoom)
        except Exception:
            zoom = 1.0
        if zoom == 0:
            zoom = 1.0

        wx = (sx - self.window.width / 2) / zoom + cx
        wy = (sy - self.window.height / 2) / zoom + cy
        return wx, wy

    # ------------------------------------------------------------
    # Anti-push into walls
    # ------------------------------------------------------------

    def _push_circle_out_of_walls(self, x: float, y: float, r: float, walls):
        moved_any = False
        for _ in range(8):
            moved_this_iter = False

            for w in walls:
                if not circle_aabb_hit(x, y, r, w):
                    continue

                l = w.left()
                rr = w.right()
                b = w.bottom()
                t = w.top()

                px = min(max(x, l), rr)
                py = min(max(y, b), t)

                dx = x - px
                dy = y - py
                dist2 = dx * dx + dy * dy

                if dist2 > 1e-9:
                    dist = math.sqrt(dist2)
                    pen = r - dist
                    if pen > 0:
                        nx = dx / dist
                        ny = dy / dist
                        x += nx * (pen + 0.5)
                        y += ny * (pen + 0.5)
                        moved_this_iter = True
                        moved_any = True
                else:
                    left_pen = (x - l)
                    right_pen = (rr - x)
                    bottom_pen = (y - b)
                    top_pen = (t - y)

                    m = min(left_pen, right_pen, bottom_pen, top_pen)

                    if m == left_pen:
                        x = l - r - 0.5
                    elif m == right_pen:
                        x = rr + r + 0.5
                    elif m == bottom_pen:
                        y = b - r - 0.5
                    else:
                        y = t + r + 0.5

                    moved_this_iter = True
                    moved_any = True

            if not moved_this_iter:
                break

        return x, y, moved_any

    def _player_post_physics_fix(self, prev_x: float, prev_y: float):
        x, y, _ = self._push_circle_out_of_walls(self.player.x, self.player.y, self.player.radius, self.walls)
        self.player.x = x
        self.player.y = y

        if any(circle_aabb_hit(self.player.x, self.player.y, self.player.radius, w) for w in self.walls):
            self.player.x = prev_x
            self.player.y = prev_y
            x2, y2, _ = self._push_circle_out_of_walls(self.player.x, self.player.y, self.player.radius, self.walls)
            self.player.x = x2
            self.player.y = y2

    # ------------------------------------------------------------
    # Fixed maze
    # ------------------------------------------------------------

    def _fixed_maze_map(self):
        return [
            "#############################",
            "#...........#...............#",
            "#.#####.###.#.#####.#######.#",
            "#.#...#...#.#.....#.....#...#",
            "#.#.#.###.#.#####.#####.#.###",
            "#...#.....#.....#.....#.#...#",
            "###.###########.#####.#.###.#",
            "#...#.........#.....#.#...#.#",
            "#.###.#######.#####.#.###.#.#",
            "#.....#.....#.....#.#.....#.#",
            "#.#####.###.#####.#.#######.#",
            "#.......#...#.....#.........#",
            "#############################",
        ]

    def _merge_wall_runs_in_row(self, grid_row, y, cell, x_offset, y_offset):
        walls = []
        x = 0
        w = len(grid_row)
        while x < w:
            if grid_row[x] != "#":
                x += 1
                continue
            start = x
            while x < w and grid_row[x] == "#":
                x += 1
            end = x
            run_len = end - start
            cx = x_offset + (start * cell) + (run_len * cell) / 2
            cy = y_offset + (y * cell) + cell / 2
            walls.append(AABB(cx, cy, run_len * cell, cell))
        return walls

    def _build_fixed_maze_walls_and_floors(self, cell):
        grid = self._fixed_maze_map()
        rows = len(grid)
        cols = len(grid[0]) if rows > 0 else 0

        maze_w = cols * cell
        maze_h = rows * cell
        x_offset = (self.arena_w_px - maze_w) / 2
        y_offset = (self.arena_h_px - maze_h) / 2

        walls = []
        floors = []

        for y in range(rows):
            walls.extend(self._merge_wall_runs_in_row(grid[y], y, cell, x_offset, y_offset))

        for y in range(rows):
            row = grid[y]
            for x in range(cols):
                if row[x] == ".":
                    fx = x_offset + x * cell + cell / 2
                    fy = y_offset + y * cell + cell / 2
                    floors.append((fx, fy))

        self.maze_is_active = True
        self.maze_floor_points = floors
        return walls

    # ------------------------------------------------------------
    # Level loading (for Campaign)
    # ------------------------------------------------------------

    def _apply_level_cfg(self, level_index: int):
        self.level_index = int(level_index)
        if self.level_index < 0:
            self.level_index = 0
        if self.level_index >= len(self.levels):
            self.level_index = 0

        self.level_cfg = self.levels[self.level_index]

        self.arena_w_px = int(self.level_cfg["arenaWidth"]) * self.tile
        self.arena_h_px = int(self.level_cfg["arenaHeight"]) * self.tile

        self.waves_total = int(self.level_cfg.get("waves", 3))
        self.spawn_interval = float(self.level_cfg.get("spawnIntervalSeconds", 3.0))
        self.enemy_types = list(self.level_cfg.get("enemyTypes", ["melee"]))
        self.enemy_stats = dict(self.level_cfg.get("enemyStats", {}))

        self.waves_spawned = 0
        self._wave_wait_timer = 0.25
        self._waiting_next_wave = True
        self._just_cleared = False

        self.enemies = []
        self.projectiles = []
        self.enemy_projectiles = []
        self.particles = []

        self.walls = self._build_walls_for_level()
        self.wall_objs = [Wall(r) for r in self.walls]

        self._place_player_safe()
        self._level_intro_timer = 0.8

    def _advance_campaign_or_finish(self):
        # ✅ если кампанию включили — идём дальше по списку уровней
        if not bool(getattr(self.window, "campaign_mode", False)):
            self._go_game_over(True)
            return

        next_index = self.level_index + 1
        if next_index >= len(self.levels):
            # кампания закончилась
            self._go_game_over(True)
            return

        self._apply_level_cfg(next_index)

    # ------------------------------------------------------------
    # Player placement
    # ------------------------------------------------------------

    def _place_player_safe(self):
        if self.maze_is_active and self.maze_floor_points:
            cx = self.arena_w_px / 2
            cy = self.arena_h_px / 2
            best = self.maze_floor_points[0]
            best_d = 10**18
            for (x, y) in self.maze_floor_points:
                dx = x - cx
                dy = y - cy
                d = dx * dx + dy * dy
                if d < best_d:
                    best_d = d
                    best = (x, y)
            self.player.x, self.player.y = best
            return

        if self.ring_is_active:
            self.player.x = self._ring_cx
            self.player.y = self._ring_cy
            x2, y2, _ = self._push_circle_out_of_walls(self.player.x, self.player.y, self.player.radius, self.walls)
            self.player.x = x2
            self.player.y = y2
            return

        self.player.x = self.arena_w_px / 2
        self.player.y = self.arena_h_px / 2

    # ------------------------------------------------------------
    # Walls
    # ------------------------------------------------------------

    def _build_walls_for_level(self):
        walls = []

        self.maze_is_active = False
        self.maze_floor_points = []
        self.ring_is_active = False

        thickness = 60
        walls.append(AABB(self.arena_w_px / 2, -thickness / 2, self.arena_w_px, thickness))
        walls.append(AABB(self.arena_w_px / 2, self.arena_h_px + thickness / 2, self.arena_w_px, thickness))
        walls.append(AABB(-thickness / 2, self.arena_h_px / 2, thickness, self.arena_h_px))
        walls.append(AABB(self.arena_w_px + thickness / 2, self.arena_h_px / 2, thickness, self.arena_h_px))

        name = str(self.level_cfg.get("name", "")).lower()

        if "лабиринт" in name:
            walls.extend(self._build_fixed_maze_walls_and_floors(self.tile))
            return walls

        if "кольцевая" in name:
            self.ring_is_active = True
            self._ring_cx = self.arena_w_px / 2
            self._ring_cy = self.arena_h_px / 2
            self._ring_w = self.arena_w_px * 0.55
            self._ring_h = self.arena_h_px * 0.55

            seg = self.tile * 0.9

            cx = self._ring_cx
            cy = self._ring_cy
            rw = self._ring_w
            rh = self._ring_h

            walls.append(AABB(cx, cy + rh / 2, rw, seg))
            walls.append(AABB(cx, cy - rh / 2, rw, seg))
            walls.append(AABB(cx - rw / 2, cy, seg, rh))
            walls.append(AABB(cx + rw / 2, cy, seg, rh))
            return walls

        for _ in range(7):
            x = random.uniform(self.tile * 2, self.arena_w_px - self.tile * 2)
            y = random.uniform(self.tile * 2, self.arena_h_px - self.tile * 2)
            w = random.uniform(self.tile * 0.7, self.tile * 1.8)
            h = random.uniform(self.tile * 0.7, self.tile * 1.8)
            walls.append(AABB(x, y, w, h))

        return walls

    # ------------------------------------------------------------
    # FX
    # ------------------------------------------------------------

    def on_show_view(self):
        arcade.set_background_color(arcade.color.DARK_OLIVE_GREEN)
        self.audio.play_music_loop()

    def _emit_hit_particles(self, x: float, y: float, count: int):
        for _ in range(count):
            ang = random.uniform(0, math.tau)
            sp = random.uniform(120, 420)
            self.particles.append(Particle(
                x=x, y=y,
                vx=math.cos(ang) * sp,
                vy=math.sin(ang) * sp,
                ttl=random.uniform(0.15, 0.5),
                size=random.uniform(2, 5),
                color=arcade.color.ORANGE
            ))

    def _emit_explosion(self, x: float, y: float):
        for _ in range(24):
            ang = random.uniform(0, math.tau)
            sp = random.uniform(180, 520)
            self.particles.append(Particle(
                x=x, y=y,
                vx=math.cos(ang) * sp,
                vy=math.sin(ang) * sp,
                ttl=random.uniform(0.2, 0.6),
                size=random.uniform(3, 7),
                color=arcade.color.YELLOW_ORANGE
            ))

    # ------------------------------------------------------------
    # Spawn helpers
    # ------------------------------------------------------------

    def _pick_spawn_in_maze(self, min_dist_from_player: float):
        if not self.maze_floor_points:
            return (self.arena_w_px / 2, self.arena_h_px / 2)
        for _ in range(300):
            x, y = random.choice(self.maze_floor_points)
            dx = x - self.player.x
            dy = y - self.player.y
            if (dx * dx + dy * dy) < (min_dist_from_player * min_dist_from_player):
                continue
            return (x, y)
        return random.choice(self.maze_floor_points)

    def _pick_spawn_in_ring(self, min_dist_from_player: float):
        cx = self._ring_cx
        cy = self._ring_cy
        half_w = self._ring_w / 2
        half_h = self._ring_h / 2

        margin = self.tile * 0.8
        left = cx - half_w + margin
        right = cx + half_w - margin
        bottom = cy - half_h + margin
        top = cy + half_h - margin

        for _ in range(400):
            x = random.uniform(left, right)
            y = random.uniform(bottom, top)

            dx = x - self.player.x
            dy = y - self.player.y
            if (dx * dx + dy * dy) < (min_dist_from_player * min_dist_from_player):
                continue

            if any(circle_aabb_hit(x, y, 20, r) for r in self.walls):
                continue

            return (x, y)

        return (cx, cy)

    def _spawn_wave(self):
        wave_idx = self.waves_spawned
        base_count = 4 + wave_idx * 2

        for _ in range(base_count):
            et = random.choice(self.enemy_types)
            st = self.enemy_stats.get(et, {"hp": 25, "speed": 120})

            radius = {"melee": 16, "shooter": 16, "charger": 18, "tank": 24}.get(et, 16)
            mass = {"tank": 3.0}.get(et, 1.6)

            if self.maze_is_active:
                x, y = self._pick_spawn_in_maze(self.tile * 3.0)
            elif self.ring_is_active:
                x, y = self._pick_spawn_in_ring(self.tile * 3.0)
            else:
                x = random.uniform(self.tile * 2, self.arena_w_px - self.tile * 2)
                y = random.uniform(self.tile * 2, self.arena_h_px - self.tile * 2)

            e = Enemy(
                enemy_type=et,
                x=float(x),
                y=float(y),
                radius=float(radius),
                speed=float(st.get("speed", 120)),
                hp=int(st.get("hp", 25)),
                mass=float(mass)
            )

            if et == "tank":
                e.shoot_interval = 1.4

            if any(circle_aabb_hit(e.x, e.y, e.radius, r) for r in self.walls):
                for _ in range(80):
                    if self.maze_is_active:
                        sx, sy = self._pick_spawn_in_maze(self.tile * 2.0)
                    elif self.ring_is_active:
                        sx, sy = self._pick_spawn_in_ring(self.tile * 2.0)
                    else:
                        sx = random.uniform(self.tile * 2, self.arena_w_px - self.tile * 2)
                        sy = random.uniform(self.tile * 2, self.arena_h_px - self.tile * 2)
                    e.x = float(sx)
                    e.y = float(sy)
                    if not any(circle_aabb_hit(e.x, e.y, e.radius, r) for r in self.walls):
                        break

            self.enemies.append(e)

    # ------------------------------------------------------------
    # Waves update: next wave only after clear
    # ------------------------------------------------------------

    def _update_waves(self, dt: float):
        if len(self.enemies) > 0:
            self._waiting_next_wave = True
            self._just_cleared = False
            return

        if self.waves_spawned > 0 and not self._just_cleared:
            self.score.add_wave_complete(self.waves_spawned)
            self._just_cleared = True
            self._wave_wait_timer = self.spawn_interval
            self._waiting_next_wave = True

        if self.waves_spawned >= self.waves_total:
            return

        if self._waiting_next_wave:
            self._wave_wait_timer -= dt
            if self._wave_wait_timer <= 0:
                self._spawn_wave()
                self.waves_spawned += 1
                self._waiting_next_wave = False
                self._just_cleared = False

    # ------------------------------------------------------------

    def _clamp_camera(self):
        half_w = self.window.width / 2
        half_h = self.window.height / 2

        cx = self.player.x
        cy = self.player.y

        if cx < half_w:
            cx = half_w
        if cy < half_h:
            cy = half_h
        if cx > self.arena_w_px - half_w:
            cx = self.arena_w_px - half_w
        if cy > self.arena_h_px - half_h:
            cy = self.arena_h_px - half_h

        self.camera.position = (cx, cy)

    def _is_win_condition_met(self) -> bool:
        if self.level_cfg.get("winCondition") != "kill_all_after_waves":
            return False
        return (self.waves_spawned >= self.waves_total) and (len(self.enemies) == 0)

    def _collect_results(self):
        return {
            "time_seconds": float(self.time_seconds),
            "waves_spawned": int(self.waves_spawned),
            "waves_total": int(self.waves_total),
            "shots_fired": int(self.shots_fired),
            "shots_hit": int(self.shots_hit),
            "kills_total": int(self.kills_total),
            "kills_by_type": dict(self.kills_by_type),
            "hp_start": int(self._player_hp_start),
            "hp_end": int(self.player.hp),
            "campaign_mode": bool(getattr(self.window, "campaign_mode", False)),
        }

    def _go_game_over(self, victory: bool):
        best = self.db.try_set_best_score(self.username, self.score.score)
        self.window.open_game_over(self.score.score, best, victory, self._collect_results())

    # ------------------------------------------------------------

    def on_update(self, dt: float):
        self.time_seconds += dt

        if self.player.hp <= 0:
            self._go_game_over(False)
            return

        if self._level_intro_timer > 0:
            self._level_intro_timer -= dt
            if self._level_intro_timer < 0:
                self._level_intro_timer = 0

        self._update_waves(dt)

        self.player.update(dt, self.walls, circle_aabb_hit)

        if self._shooting:
            p = self.player.shoot_towards(
                self.mouse_world_x, self.mouse_world_y,
                self.cfg.bullet_speed, self.cfg.bullet_radius,
                self.cfg.bullet_damage, self.cfg.bullet_knockback
            )
            if p is not None:
                self.projectiles.append(p)
                self.shots_fired += 1
                self.audio.play_shot()

        for e in self.enemies:
            e.update(dt, self.player.x, self.player.y, self.walls, circle_aabb_hit)
            ep = e.try_shoot(self.player.x, self.player.y)
            if ep is not None:
                self.enemy_projectiles.append(ep)

        prev_px = float(self.player.x)
        prev_py = float(self.player.y)

        # игрок-враг (раздвижение)
        for e in self.enemies:
            if circle_circle_hit(self.player.x, self.player.y, self.player.radius, e.x, e.y, e.radius):
                ax, ay, bx, by = soft_separate_circles(
                    self.player.x, self.player.y, self.player.radius,
                    e.x, e.y, e.radius
                )
                self.player.x, self.player.y, e.x, e.y = ax, ay, bx, by

        # враг-враг (раздвижение)
        n = len(self.enemies)
        for i in range(n):
            a = self.enemies[i]
            for j in range(i + 1, n):
                b = self.enemies[j]
                if circle_circle_hit(a.x, a.y, a.radius, b.x, b.y, b.radius):
                    ax, ay, bx, by = soft_separate_circles(a.x, a.y, a.radius, b.x, b.y, b.radius)
                    a.x, a.y, b.x, b.y = ax, ay, bx, by

        # не даём затолкать игрока в стену
        self._player_post_physics_fix(prev_px, prev_py)

        # ✅ контактный урон (и по игроку, и по врагу)
        self._contact_timer -= dt
        if self._contact_timer <= 0:
            for e in self.enemies:
                if circle_circle_hit(self.player.x, self.player.y, self.player.radius, e.x, e.y, e.radius):
                    # урон игроку
                    self.player.hp -= self.cfg.contact_damage

                    # ✅ урон врагу от героя
                    e.hp -= int(self.player_contact_damage)

                    self._emit_hit_particles(self.player.x, self.player.y, 12)
                    self.audio.play_hit()

                    if e.hp <= 0:
                        e.alive = False
                        self.score.add_kill(e.enemy_type)
                        self.kills_total += 1
                        self.kills_by_type[e.enemy_type] = int(self.kills_by_type.get(e.enemy_type, 0)) + 1
                        self._emit_explosion(e.x, e.y)
                        self.audio.play_explosion()

                    self._contact_timer = self.cfg.contact_damage_interval
                    break

        # пули игрока -> враги
        for b in self.projectiles:
            b.update(dt)

            if any(circle_aabb_hit(b.x, b.y, b.radius, r) for r in self.walls):
                b.alive = False
                continue

            for e in self.enemies:
                if circle_circle_hit(b.x, b.y, b.radius, e.x, e.y, e.radius):
                    self.shots_hit += 1
                    e.hp -= b.damage
                    e.apply_knockback(b.x, b.y, b.knockback)
                    self._emit_hit_particles(b.x, b.y, 10)
                    self.audio.play_hit()
                    b.alive = False

                    if e.hp <= 0:
                        e.alive = False
                        self.score.add_kill(e.enemy_type)
                        self.kills_total += 1
                        self.kills_by_type[e.enemy_type] = int(self.kills_by_type.get(e.enemy_type, 0)) + 1
                        self._emit_explosion(e.x, e.y)
                        self.audio.play_explosion()
                    break

        # пули врагов -> игрок
        for b in self.enemy_projectiles:
            b.update(dt)

            if any(circle_aabb_hit(b.x, b.y, b.radius, r) for r in self.walls):
                b.alive = False
                continue

            if circle_circle_hit(b.x, b.y, b.radius, self.player.x, self.player.y, self.player.radius):
                self.player.hp -= b.damage
                self._emit_hit_particles(b.x, b.y, 14)
                self.audio.play_hit()
                b.alive = False

        # чистка
        self.projectiles = [b for b in self.projectiles if b.alive]
        self.enemy_projectiles = [b for b in self.enemy_projectiles if b.alive]
        self.enemies = [e for e in self.enemies if e.alive]

        for p in self.particles:
            p.update(dt)
        self.particles = [p for p in self.particles if p.alive]

        # победа
        if self._is_win_condition_met():
            # ✅ одиночный уровень: сразу результаты
            # ✅ кампания: грузим следующий (или результаты в конце)
            self._advance_campaign_or_finish()
            return

        self._clamp_camera()

    def on_draw(self):
        self.clear()

        with self.camera.activate():
            arcade.draw_lrbt_rectangle_filled(
                0, self.arena_w_px,
                 0, self.arena_h_px,
                arcade.color.DARK_OLIVE_GREEN
            )

            for w in self.wall_objs:
                w.draw()

            self.player.draw()

            for e in self.enemies:
                e.draw()

            for b in self.projectiles:
                b.draw()

            for b in self.enemy_projectiles:
                arcade.draw_circle_filled(b.x, b.y, b.radius, arcade.color.LIGHT_GRAY)

            for p in self.particles:
                p.draw()

        arcade.draw_text("HP: " + str(self.player.hp), 20, self.window.height - 40, arcade.color.WHITE, 18)
        arcade.draw_text("Score: " + str(self.score.score), 20, self.window.height - 70, arcade.color.WHITE, 18)

        if len(self.enemies) > 0:
            shown_wave = self.waves_spawned
        else:
            shown_wave = min(self.waves_spawned + 1, self.waves_total)

        arcade.draw_text(
            "Wave: " + str(shown_wave) + "/" + str(self.waves_total),
            20, self.window.height - 100, arcade.color.WHITE, 14
        )

        lvl_name = str(self.level_cfg.get("name", ""))
        camp = bool(getattr(self.window, "campaign_mode", False))
        if camp:
            lvl_name = lvl_name + f"  (Campaign {self.level_index + 1}/{len(self.levels)})"

        arcade.draw_text(
            "Level: " + lvl_name,
            20, self.window.height - 125, arcade.color.WHITE, 14
        )

    def on_key_press(self, key, modifiers):
        if key == arcade.key.W or key == arcade.key.UP:
            self.player.up = True
        if key == arcade.key.S or key == arcade.key.DOWN:
            self.player.down = True
        if key == arcade.key.A or key == arcade.key.LEFT:
            self.player.left = True
        if key == arcade.key.D or key == arcade.key.RIGHT:
            self.player.right = True

        if key == arcade.key.ESCAPE:
            self.scene_manager.go("level_select")

    def on_key_release(self, key, modifiers):
        if key == arcade.key.W or key == arcade.key.UP:
            self.player.up = False
        if key == arcade.key.S or key == arcade.key.DOWN:
            self.player.down = False
        if key == arcade.key.A or key == arcade.key.LEFT:
            self.player.left = False
        if key == arcade.key.D or key == arcade.key.RIGHT:
            self.player.right = False

    def on_mouse_motion(self, x, y, dx, dy):
        wx, wy = self._screen_to_world(float(x), float(y))
        self.mouse_world_x = wx
        self.mouse_world_y = wy

    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            wx, wy = self._screen_to_world(float(x), float(y))
            self.mouse_world_x = wx
            self.mouse_world_y = wy
            self._shooting = True

    def on_mouse_release(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            self._shooting = False
