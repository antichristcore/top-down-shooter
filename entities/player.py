import arcade
from entities.projectile import Projectile


class Player:
    def __init__(self, position, radius=16, speed=200, max_hp=10):
        self.position = arcade.Vector(position[0], position[1])
        self.radius = radius
        self.speed = speed
        self.max_hp = max_hp
        self.hp = max_hp
        self.velocity = arcade.Vector(0, 0)
        self.shoot_cooldown = 0.2
        self._shoot_timer = 0

    def update(self, delta_time, move_vector, arena_bounds):
        self.velocity = move_vector.normalize() * self.speed if move_vector.length > 0 else arcade.Vector(0, 0)
        self.position += self.velocity * delta_time
        self.position.x = max(arena_bounds[0] + self.radius, min(self.position.x, arena_bounds[2] - self.radius))
        self.position.y = max(arena_bounds[1] + self.radius, min(self.position.y, arena_bounds[3] - self.radius))
        self._shoot_timer = max(0, self._shoot_timer - delta_time)

    def can_shoot(self):
        return self._shoot_timer <= 0

    def shoot(self, target_pos):
        if not self.can_shoot():
            return None
        direction = arcade.Vector(target_pos[0] - self.position.x, target_pos[1] - self.position.y)
        if direction.length == 0:
            return None
        direction = direction.normalize()
        velocity = direction * 450
        self._shoot_timer = self.shoot_cooldown
        return Projectile(self.position.copy(), velocity, damage=1, radius=4, owner="player", knockback=120)

    def draw(self):
        arcade.draw_circle_filled(self.position.x, self.position.y, self.radius, arcade.color.BLUE)
        arcade.draw_circle_outline(self.position.x, self.position.y, self.radius, arcade.color.WHITE, 2)
