import arcade

class Particle:
    __slots__ = ("x","y","vx","vy","ttl","size","color","alive")

    def __init__(self, x, y, vx, vy, ttl, size, color):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.ttl = ttl
        self.size = size
        self.color = color
        self.alive = True

    def update(self, dt: float):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.ttl -= dt
        if self.ttl <= 0:
            self.alive = False

    def draw(self):
        alpha = max(0, min(255, int(255 * (self.ttl / 0.5))))
        c = (self.color[0], self.color[1], self.color[2], alpha)
        arcade.draw_circle_filled(self.x, self.y, max(1, self.size), c)
