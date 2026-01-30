import arcade
import math
from entities.projectile import Projectile

class Enemy:
    __slots__ = (
        "enemy_type","x","y","radius","speed","hp","max_hp","mass",
        "shoot_interval","_shoot_timer",
        "dash_cooldown","dash_time","_dash_cd","_dash_t",
        "knock_vx","knock_vy",
        "alive",
        "texture"
    )

    def __init__(self, enemy_type, x, y, radius, speed, hp, mass=1.5):
        self.enemy_type = enemy_type
        self.x = x
        self.y = y
        self.radius = radius
        self.speed = speed
        self.hp = hp
        self.max_hp = hp
        self.mass = mass

        self.shoot_interval = 1.0
        self._shoot_timer = 0.0

        self.dash_cooldown = 2.0
        self.dash_time = 0.25
        self._dash_cd = 0.0
        self._dash_t = 0.0

        self.knock_vx = 0.0
        self.knock_vy = 0.0

        self.alive = True


    def apply_knockback(self, from_x: float, from_y: float, force: float):
        dx = self.x - from_x
        dy = self.y - from_y
        length = math.hypot(dx, dy) or 1.0
        dx /= length
        dy /= length
        imp = force / max(0.1, self.mass)
        self.knock_vx += dx * imp
        self.knock_vy += dy * imp

    def update(self, dt: float, player_x: float, player_y: float, walls, collision_circle_rect_fn):
        self._shoot_timer = max(0.0, self._shoot_timer - dt)
        self._dash_cd = max(0.0, self._dash_cd - dt)
        self._dash_t = max(0.0, self._dash_t - dt)

        self.knock_vx *= (0.15 ** dt)
        self.knock_vy *= (0.15 ** dt)

        dx = player_x - self.x
        dy = player_y - self.y
        dist = math.hypot(dx, dy) or 1.0
        dx /= dist
        dy /= dist

        move_speed = self.speed
        if self.enemy_type == "charger":
            if self._dash_t > 0.0:
                move_speed = self.speed * 3.0
            elif self._dash_cd <= 0.0 and dist < 600:
                self._dash_t = self.dash_time
                self._dash_cd = self.dash_cooldown

        vx = dx * move_speed + self.knock_vx
        vy = dy * move_speed + self.knock_vy

        nx = self.x + vx * dt
        ny = self.y + vy * dt

        if not any(collision_circle_rect_fn(nx, self.y, self.radius, r) for r in walls):
            self.x = nx
        if not any(collision_circle_rect_fn(self.x, ny, self.radius, r) for r in walls):
            self.y = ny

    def try_shoot(self, player_x: float, player_y: float):
        if self.enemy_type != "shooter":
            return None
        if self._shoot_timer > 0.0:
            return None

        self._shoot_timer = self.shoot_interval

        dx = player_x - self.x
        dy = player_y - self.y
        dist = math.hypot(dx, dy) or 1.0
        dx /= dist
        dy /= dist

        bullet_speed = 420
        return Projectile(self.x, self.y, dx * bullet_speed, dy * bullet_speed, 4, 10, 240)

    def _color(self):
        return {
            "melee": arcade.color.RED_ORANGE,
            "shooter": arcade.color.LIGHT_CORAL,
            "charger": arcade.color.MAGENTA,
            "tank": arcade.color.DARK_RED
        }.get(self.enemy_type, arcade.color.RED)

    def _class_name(self):
        return {
            "melee": "Боец",
            "shooter": "Стрелок",
            "charger": "Рывок",
            "tank": "Танк"
        }.get(self.enemy_type, self.enemy_type)

    def _draw_hp_bar(self):
        bar_width = self.radius * 2
        bar_height = 6
        bar_x = self.x - bar_width / 2
        bar_y = self.y - self.radius - 12
        arcade.draw_lrbt_rectangle_filled(
            bar_x, bar_x + bar_width, bar_y, bar_y + bar_height, arcade.color.DIM_GRAY
        )
        if self.max_hp > 0:
            fill_width = bar_width * max(0.0, min(1.0, self.hp / self.max_hp))
            arcade.draw_lrbt_rectangle_filled(
                bar_x, bar_x + fill_width, bar_y, bar_y + bar_height, arcade.color.GREEN
            )

    def draw(self):
        size = self.radius * 2
        self.texture = arcade.make_soft_square_texture(64, self._color(), 255, 255)
        arcade.draw_texture_rect(self.texture, arcade.rect.XYWH(self.x, self.y, size, size))
        arcade.draw_text(self._class_name(), self.x, self.y + self.radius + 10, arcade.color.WHITE, 12, anchor_x="center", anchor_y="center")
        self._draw_hp_bar()
