import math


class Vector2:
    __slots__ = ("x", "y")

    def __init__(self, x=0.0, y=0.0):
        self.x = float(x)
        self.y = float(y)

    def __add__(self, other):
        return Vector2(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector2(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar):
        return Vector2(self.x * scalar, self.y * scalar)

    def __rmul__(self, scalar):
        return self.__mul__(scalar)

    def __truediv__(self, scalar):
        return Vector2(self.x / scalar, self.y / scalar)

    def __neg__(self):
        return Vector2(-self.x, -self.y)

    @property
    def length(self):
        return math.hypot(self.x, self.y)

    def normalize(self):
        length = self.length
        if length == 0:
            return Vector2(0, 0)
        return self / length

    def copy(self):
        return Vector2(self.x, self.y)

    def lerp(self, target, t):
        return Vector2(self.x + (target.x - self.x) * t, self.y + (target.y - self.y) * t)

    def to_tuple(self):
        return (self.x, self.y)
