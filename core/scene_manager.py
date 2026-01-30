class SceneManager:
    def __init__(self):
        self._scenes = {}
        self.current = None

    def add(self, name, scene):
        self._scenes[name] = scene
        scene.manager = self

    def show(self, name, **kwargs):
        scene = self._scenes.get(name)
        if scene is None:
            raise ValueError(f"Scene '{name}' not found")
        if self.current:
            self.current.on_hide()
        self.current = scene
        self.current.on_show(**kwargs)

    def update(self, delta_time):
        if self.current:
            self.current.update(delta_time)

    def draw(self):
        if self.current:
            self.current.draw()

    def on_key_press(self, key, modifiers):
        if self.current:
            self.current.on_key_press(key, modifiers)

    def on_key_release(self, key, modifiers):
        if self.current:
            self.current.on_key_release(key, modifiers)

    def on_mouse_press(self, x, y, button, modifiers):
        if self.current:
            self.current.on_mouse_press(x, y, button, modifiers)

    def on_mouse_release(self, x, y, button, modifiers):
        if self.current:
            self.current.on_mouse_release(x, y, button, modifiers)

    def on_mouse_motion(self, x, y, dx, dy):
        if self.current:
            self.current.on_mouse_motion(x, y, dx, dy)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if self.current:
            self.current.on_mouse_drag(x, y, dx, dy, buttons, modifiers)
