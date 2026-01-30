from systems.math_utils import Vector2


def circle_circle(pos_a, radius_a, pos_b, radius_b):
    return (pos_a - pos_b).length < (radius_a + radius_b)


def circle_rect(circle_pos, radius, rect):
    closest_x = max(rect[0], min(circle_pos.x, rect[2]))
    closest_y = max(rect[1], min(circle_pos.y, rect[3]))
    dx = circle_pos.x - closest_x
    dy = circle_pos.y - closest_y
    return (dx * dx + dy * dy) < (radius * radius)


def resolve_soft_push(pos_a, radius_a, pos_b, radius_b):
    delta = pos_a - pos_b
    dist = delta.length
    if dist == 0:
        return Vector2(0, 0), Vector2(0, 0)
    overlap = radius_a + radius_b - dist
    if overlap <= 0:
        return Vector2(0, 0), Vector2(0, 0)
    push_dir = delta.normalize()
    push = push_dir * (overlap * 0.5)
    return push, -push
