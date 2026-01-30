import arcade

from systems.math_utils import Vector2


class Projectile:
    def __init__(self, position, velocity, damage, radius, owner, knockback=80):
        self.position = Vector2(position[0], position[1])
        self.velocity = Vector2(velocity[0], velocity[1])
        self.damage = damage
        self.radius = radius
        self.owner = owner
        self.knockback = knockback
        self.alive = True

    def update(self, delta_time, arena_bounds):
        self.position += self.velocity * delta_time
        if (
            self.position.x < arena_bounds[0]
            or self.position.x > arena_bounds[2]
            or self.position.y < arena_bounds[1]
            or self.position.y > arena_bounds[3]
        ):
            self.alive = False

    def draw(self):
        color = arcade.color.CYAN if self.owner == "player" else arcade.color.SALMON
        arcade.draw_circle_filled(self.position.x, self.position.y, self.radius, color)
