from import_handler import ImportDefence
with ImportDefence():
    from kivy.uix.button import Button
    from kivy.graphics import Color, Rectangle

from gui.dialogs import popup
from globalstuff import *
from register import Register
from gui.Hover import Hover


class Scan:
    font_size = BUTTON_COLUMN_FONT_SIZE
    background_color = button_column_background

    def __init__(self, name, action, parent):
        self.name = name
        self.action = action
        self.x = 0
        self.is_running = False

        self.button = Button(
            text=name,
            font_size=Scan.font_size,
            background_color=Scan.background_color,
            font_name="Roboto"
        )
        self.button.bind(on_press=lambda x: self.select(x))
        parent.add_raw(self.button)
        Hover.add(self.button)

    def select(self, x):
        if state.highlighted_scan == self:
            state.scan(DummyScan())
            return
        state.scan(self)
        with self.button.canvas.after:
            self.highlight = Color(*SCAN_HIGHLIGHT)
            self.highlight_rect = Rectangle(
                pos=(self.button.x, self.button.y),
                size=(self.button.width, self.button.height)
            )
        self.x = x

    def deselect(self):
        self.button.canvas.after.clear()

    def act(self):
        self.is_running = True
        self.button.text += '...'
        try:
            self.action()
        except TypeError:
            self.action(self.x)

    def finished(self):
        self.is_running = False
        if self.button.text.endswith('...') and not Register().is_infinite_scan(self.button.text):
            self.button.text = self.button.text[:-3]


class DummyScan(Scan):
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.name = "Dummy"
        self.is_running = False

    def select(self, x):
        pass

    def deselect(self):
        pass

    def act(self):
        # win32api.MessageBox(0, "You must first select a scan to run.", "Running without a scan", 0x00000000)
        popup("Running without a scan", "You must first select a scan to run.")
        # raise NotImplementedError("A DummyScan cannot be `.act`ed upon.")

    def finished(self):
        pass
