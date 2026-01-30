import arcade

class Projectile:
    __slots__ = ("x","y","vx","vy","radius","damage","knockback","alive")

    def __init__(self, x, y, vx, vy, radius, damage, knockback):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.radius = radius
        self.damage = damage
        self.knockback = knockback
        self.alive = True

    def update(self, dt: float):
        self.x += self.vx * dt
        self.y += self.vy * dt

    def draw(self):
        arcade.draw_circle_filled(self.x, self.y, self.radius, arcade.color.YELLOW)
