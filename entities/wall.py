import arcade


class Wall:
    def __init__(self, rect):
        self.rect = rect

    def draw(self):
        arcade.draw_lrbt_rectangle_filled(
            self.rect.left(), self.rect.right(), self.rect.bottom(), self.rect.top(),
            arcade.color.DARK_SLATE_GRAY
        )
