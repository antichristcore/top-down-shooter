import json
from datetime import datetime
from pathlib import Path

SCORES_PATH = Path("scores.txt")


class ScoreSystem:
    def __init__(self):
        self.best_score = 0
        self.last_score = 0
        self.last_time = ""
        self.load()

    def load(self):
        if not SCORES_PATH.exists():
            return
        data = json.loads(SCORES_PATH.read_text(encoding="utf-8"))
        self.best_score = data.get("best_score", 0)
        self.last_score = data.get("last_score", 0)
        self.last_time = data.get("last_time", "")

    def submit(self, score):
        self.last_score = score
        self.last_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if score > self.best_score:
            self.best_score = score
        self.save()

    def save(self):
        data = {
            "best_score": self.best_score,
            "last_score": self.last_score,
            "last_time": self.last_time,
        }
        SCORES_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
