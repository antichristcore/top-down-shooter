import arcade


class Button:
    def __init__(self, text, center_x, center_y, width=180, height=44):
        self.text = text
        self.center_x = center_x
        self.center_y = center_y
        self.width = width
        self.height = height
        self.hovered = False

    def hit_test(self, x, y):
        return (
            self.center_x - self.width / 2 <= x <= self.center_x + self.width / 2
            and self.center_y - self.height / 2 <= y <= self.center_y + self.height / 2
        )

    def draw(self):
        color = arcade.color.ALMOND if self.hovered else arcade.color.DARK_SLATE_BLUE
        arcade.draw_rectangle_filled(self.center_x, self.center_y, self.width, self.height, color)
        arcade.draw_text(
            self.text,
            self.center_x,
            self.center_y,
            arcade.color.WHITE,
            14,
            anchor_x="center",
            anchor_y="center",
        )


class Slider:
    def __init__(self, label, value, center_x, center_y, width=220):
        self.label = label
        self.value = value
        self.center_x = center_x
        self.center_y = center_y
        self.width = width
        self.dragging = False

    def set_from_x(self, x):
        left = self.center_x - self.width / 2
        self.value = max(0.0, min(1.0, (x - left) / self.width))

    def hit_knob(self, x, y):
        knob_x = self.center_x - self.width / 2 + self.value * self.width
        return (abs(x - knob_x) < 12) and (abs(y - self.center_y) < 12)

    def draw(self):
        left = self.center_x - self.width / 2
        right = self.center_x + self.width / 2
        arcade.draw_text(self.label, left, self.center_y + 16, arcade.color.WHITE, 12)
        arcade.draw_line(left, self.center_y, right, self.center_y, arcade.color.GRAY, 4)
        knob_x = left + self.value * self.width
        arcade.draw_circle_filled(knob_x, self.center_y, 8, arcade.color.SKY_BLUE)
        arcade.draw_text(f"{int(self.value * 100)}%", right + 10, self.center_y - 8, arcade.color.WHITE, 12)
