import arcade


class SceneManager:
    def __init__(self, window: arcade.Window):
        self.window = window
        self._factories = {}  # name -> callable() -> arcade.View

    def register(self, name: str, factory):
        self._factories[name] = factory

    def show(self, view: arcade.View):
        self.window.show_view(view)

    def go(self, name: str):
        if name not in self._factories:
            raise KeyError("Scene not registered: " + str(name))
        view = self._factories[name]()
        self.show(view)
