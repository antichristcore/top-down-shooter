class ScoreSystem:
    def __init__(self):
        self.score = 0

    def add_kill(self, enemy_type: str):
        base = {"melee": 50, "shooter": 70, "charger": 80, "tank": 120}.get(enemy_type, 50)
        self.score += int(base)

    def add_wave_complete(self, wave_num: int):
        self.score += int(150 + wave_num * 25)
