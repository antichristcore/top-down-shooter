class AABB:
    def __init__(self, cx: float, cy: float, w: float, h: float):
        self.cx = cx
        self.cy = cy
        self.w = w
        self.h = h

    def left(self) -> float:
        return self.cx - self.w / 2

    def right(self) -> float:
        return self.cx + self.w / 2

    def bottom(self) -> float:
        return self.cy - self.h / 2

    def top(self) -> float:
        return self.cy + self.h / 2
