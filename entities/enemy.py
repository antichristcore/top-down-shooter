import arcade
from entities.projectile import Projectile


class Enemy:
    def __init__(self, enemy_type, position, stats):
        self.enemy_type = enemy_type
        self.position = arcade.Vector(position[0], position[1])
        self.radius = 14 if enemy_type != "tank" else 20
        self.speed = stats.get("speed", 100)
        self.max_hp = stats.get("hp", 3)
        self.hp = self.max_hp
        self.mass = stats.get("mass", 1.0)
        self.velocity = arcade.Vector(0, 0)
        self.attack_timer = 0
        self.shoot_timer = 0
        self.attack_interval = 1.2 if enemy_type == "shooter" else 0.5
        self.charge_timer = 0
        self.charge_interval = 2.5
        self.charge_duration = 0.4
        self.charge_speed = self.speed * 2.2
        self.hit_flash_timer = 0

    def is_alive(self):
        return self.hp > 0

    def apply_knockback(self, direction, force):
        if direction.length == 0:
            return
        impulse = direction.normalize() * (force / max(self.mass, 0.1))
        self.velocity += impulse

    def take_damage(self, amount):
        self.hp -= amount
        self.hit_flash_timer = 0.12

    def update(self, delta_time, player_position, arena_bounds):
        to_player = arcade.Vector(player_position.x - self.position.x, player_position.y - self.position.y)
        distance = to_player.length
        move_dir = to_player.normalize() if distance > 1 else arcade.Vector(0, 0)
        speed = self.speed
        if self.enemy_type == "charger":
            self.charge_timer -= delta_time
            if self.charge_timer <= 0:
                self.charge_timer = self.charge_interval
                self.attack_timer = self.charge_duration
            if self.attack_timer > 0:
                self.attack_timer -= delta_time
                speed = self.charge_speed
        if self.enemy_type == "tank":
            speed *= 0.7
        if self.enemy_type == "shooter" and distance < 140:
            move_dir = move_dir * -1
        desired_velocity = move_dir * speed
        self.velocity = self.velocity.lerp(desired_velocity, 0.2)
        self.position += self.velocity * delta_time
        self.position.x = max(arena_bounds[0] + self.radius, min(self.position.x, arena_bounds[2] - self.radius))
        self.position.y = max(arena_bounds[1] + self.radius, min(self.position.y, arena_bounds[3] - self.radius))
        self.attack_timer = max(0, self.attack_timer - delta_time)
        self.shoot_timer = max(0, self.shoot_timer - delta_time)
        self.hit_flash_timer = max(0, self.hit_flash_timer - delta_time)

    def maybe_shoot(self, delta_time, player_position):
        if self.enemy_type != "shooter":
            return None
        if self.shoot_timer > 0:
            return None
        self.shoot_timer = self.attack_interval
        direction = arcade.Vector(player_position.x - self.position.x, player_position.y - self.position.y)
        if direction.length == 0:
            return None
        velocity = direction.normalize() * 280
        return Projectile(self.position.copy(), velocity, damage=1, radius=4, owner="enemy", knockback=60)

    def draw(self):
        base_color = arcade.color.ORANGE_RED if self.enemy_type == "melee" else arcade.color.RED
        if self.enemy_type == "shooter":
            base_color = arcade.color.PURPLE_HEART
        if self.enemy_type == "charger":
            base_color = arcade.color.YELLOW_ORANGE
        if self.enemy_type == "tank":
            base_color = arcade.color.DARK_BROWN
        if self.hit_flash_timer > 0:
            base_color = arcade.color.WHITE
        arcade.draw_circle_filled(self.position.x, self.position.y, self.radius, base_color)
        health_width = 24
        health_height = 4
        health_ratio = max(0, self.hp) / self.max_hp
        arcade.draw_rectangle_filled(self.position.x, self.position.y + self.radius + 8, health_width, health_height, arcade.color.DARK_GRAY)
        arcade.draw_rectangle_filled(
            self.position.x - (health_width / 2) + (health_width * health_ratio / 2),
            self.position.y + self.radius + 8,
            health_width * health_ratio,
            health_height,
            arcade.color.LIME_GREEN,
        )
