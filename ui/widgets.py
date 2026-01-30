import arcade.gui as gui


class CallbackButton(gui.UIFlatButton):
    def __init__(self, text: str, width: int, on_click_callback):
        super().__init__(text=text, width=width)
        self._cb = on_click_callback

    def on_click(self, event):
        if self._cb:
            self._cb()
