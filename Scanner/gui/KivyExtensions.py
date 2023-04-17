from import_handler import ImportDefence
with ImportDefence():
    from kivy.uix.button import Button

from globalstuff import *


#     --- Kivy Extensions ---
class ButtonColumn(GridLayout):
    """Organises buttons in a column

    Args:
        GridLayout (tk): the superclass.
    """

    def __init__(self, width: int):
        super().__init__(cols=1, width=width, size_hint=(
            None, 1), spacing=[-3], padding=[-1, -3, -1, -3])
        self.buttons = []  # list of tuples `(button, callback)`
        self.background_color = button_column_background
        self.font_size = BUTTON_COLUMN_FONT_SIZE

    def add(self, text: str, callback=None):
        btn = Button(
            text=text,
            font_size=self.font_size,
            background_color=self.background_color,
            font_name="Roboto"
        )
        if callback is not None:
            btn.bind(on_press=callback)
        super().add_widget(btn)
        Hover.add(btn)
        self.buttons.append((btn, callback))
        return btn

    def add_raw(self, button):
        super().add_widget(button)
        self.buttons.append((button, None))


class MyPaintWidget(Widget):
    """Responsible for the middle diagram (object #9).
    Args:
        Widget (tkinter widget): the superclass.
    """

    def init(self):
        update_kivy_diagram(self, 0)

    def on_touch_down(self, touch):
        update_kivy_diagram(self, 0)


class GreenButton(Button):
    """A button that has green background, and also adds itself to `Hover`."""

    def __init__(self, text, **kwargs):
        super().__init__(
            text=f'[color={GREEN}]{escape_markup(text)}[/color]',
            markup=True,
            **kwargs
        )
        Hover.add(self)


class OperationButton(Button):
    """A button that has grey background, adds itself to `Hover`, defines a `HoverReplace` on itself, and uses font `Symbols`."""

    def __init__(self, text, long_text, onclick, **kwargs):
        super().__init__(
            text=text,
            background_color=OPERATION_BUTTON_BACKGROUND,
            font_name="Symbols",
            **kwargs
        )
        Hover.add(self)
        HoverReplace(self, long_text, OPERATION_BUTTON_FONT_SIZE)
        self.bind(on_press=onclick)


if __name__ == '__main__':
    print("This modules provides some classes that inherit from kivy's classes,")
    print("and adds behaviour or simplfies constructors.")
