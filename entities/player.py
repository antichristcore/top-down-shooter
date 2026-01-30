import arcade
import math
from entities.projectile import Projectile

class Player:
    __slots__ = (
        "x","y","radius","speed","hp","mass",
        "up","down","left","right",
        "shoot_cooldown","_shoot_timer"
    )

    def __init__(self, x, y, radius, speed, hp, mass=1.0):
        self.x = x
        self.y = y
        self.radius = radius
        self.speed = speed
        self.hp = hp
        self.mass = mass

        self.up = self.down = self.left = self.right = False
        self.shoot_cooldown = 0.12
        self._shoot_timer = 0.0

    def update(self, dt: float, walls, collision_circle_rect_fn):
        self._shoot_timer = max(0.0, self._shoot_timer - dt)

        dx = (1 if self.right else 0) - (1 if self.left else 0)
        dy = (1 if self.up else 0) - (1 if self.down else 0)

        if dx != 0 or dy != 0:
            length = math.hypot(dx, dy)
            dx /= length
            dy /= length

        nx = self.x + dx * self.speed * dt
        ny = self.y + dy * self.speed * dt

        tx = nx
        if not any(collision_circle_rect_fn(tx, self.y, self.radius, r) for r in walls):
            self.x = tx
        ty = ny
        if not any(collision_circle_rect_fn(self.x, ty, self.radius, r) for r in walls):
            self.y = ty

    def can_shoot(self) -> bool:
        return self._shoot_timer <= 0.0

    def shoot_towards(self, target_x: float, target_y: float, bullet_speed: float, bullet_radius: float, bullet_damage: int, bullet_knockback: float):
        if not self.can_shoot():
            return None
        self._shoot_timer = self.shoot_cooldown

        dx = target_x - self.x
        dy = target_y - self.y
        length = math.hypot(dx, dy) or 1.0
        dx /= length
        dy /= length

        return Projectile(
            self.x, self.y,
            dx * bullet_speed, dy * bullet_speed,
            bullet_radius, bullet_damage, bullet_knockback
        )

    def draw(self):
        arcade.draw_circle_filled(self.x, self.y, self.radius, arcade.color.AZURE)
        arcade.draw_text(f"{self.hp}", self.x - 10, self.y - 8, arcade.color.BLACK, 12)
