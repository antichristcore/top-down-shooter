import math
import random
import arcade

from systems.math_utils import Vector2


class Particle:
    def __init__(self, position, velocity, color, ttl, radius):
        self.position = Vector2(position[0], position[1])
        self.velocity = Vector2(velocity[0], velocity[1])
        self.color = color
        self.ttl = ttl
        self.radius = radius

    def update(self, delta_time):
        self.position += self.velocity * delta_time
        self.ttl -= delta_time

    def draw(self):
        alpha = max(0, min(255, int(255 * (self.ttl / 1.0))))
        color = (*self.color[:3], alpha)
        arcade.draw_circle_filled(self.position.x, self.position.y, self.radius, color)


class ParticleSystem:
    def __init__(self):
        self.particles = []

    def spawn_explosion(self, position, color=arcade.color.ORANGE, count=12):
        for _ in range(count):
            angle = random.uniform(0, 6.283)
            speed = random.uniform(60, 160)
            velocity = (speed * math.sin(angle), speed * math.cos(angle))
            self.particles.append(Particle(position, velocity, color, ttl=0.8, radius=3))

    def spawn_hit(self, position, color=arcade.color.YELLOW, count=6):
        for _ in range(count):
            angle = random.uniform(0, 6.283)
            speed = random.uniform(40, 90)
            velocity = (speed * math.sin(angle), speed * math.cos(angle))
            self.particles.append(Particle(position, velocity, color, ttl=0.4, radius=2))

    def update(self, delta_time):
        for particle in list(self.particles):
            particle.update(delta_time)
            if particle.ttl <= 0:
                self.particles.remove(particle)

    def draw(self):
        for particle in self.particles:
            particle.draw()
