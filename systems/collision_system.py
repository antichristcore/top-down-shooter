import math
from systems.aabb import AABB


def circle_circle_hit(x1: float, y1: float, r1: float, x2: float, y2: float, r2: float) -> bool:
    dx = x1 - x2
    dy = y1 - y2
    return (dx * dx + dy * dy) < (r1 + r2) * (r1 + r2)


def circle_aabb_hit(cx: float, cy: float, cr: float, rect: AABB) -> bool:
    l = rect.left()
    r = rect.right()
    b = rect.bottom()
    t = rect.top()

    closest_x = min(max(cx, l), r)
    closest_y = min(max(cy, b), t)
    dx = cx - closest_x
    dy = cy - closest_y
    return (dx * dx + dy * dy) < (cr * cr)


def soft_separate_circles(x1, y1, r1, x2, y2, r2):
    dx = x1 - x2
    dy = y1 - y2
    dist = math.hypot(dx, dy)
    if dist == 0:
        dist = 1.0
    overlap = (r1 + r2) - dist
    if overlap <= 0:
        return (x1, y1, x2, y2)

    nx = dx / dist
    ny = dy / dist
    push = overlap * 0.5
    return (x1 + nx * push, y1 + ny * push, x2 - nx * push, y2 - ny * push)
