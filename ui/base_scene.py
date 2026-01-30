class BaseScene:
    def __init__(self, window):
        self.window = window
        self.manager = None

    def on_show(self, **kwargs):
        pass

    def on_hide(self):
        pass

    def update(self, delta_time):
        pass

    def draw(self):
        pass

    def on_key_press(self, key, modifiers):
        pass

    def on_key_release(self, key, modifiers):
        pass

    def on_mouse_press(self, x, y, button, modifiers):
        pass

    def on_mouse_release(self, x, y, button, modifiers):
        pass

    def on_mouse_motion(self, x, y, dx, dy):
        pass

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        pass
