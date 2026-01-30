class GameConfig:
    def __init__(self):
        self.screen_width = 1280
        self.screen_height = 720
        self.title = "Top-Down Shooter (Arcade)"
        self.tile_size = 64

        self.player_radius = 18
        self.player_speed = 280
        self.player_hp = 100

        self.bullet_radius = 5
        self.bullet_speed = 650
        self.bullet_damage = 15
        self.bullet_knockback = 380

        self.contact_damage = 10
        self.contact_damage_interval = 0.5
