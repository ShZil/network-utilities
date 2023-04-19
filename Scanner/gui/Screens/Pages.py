from import_handler import ImportDefence
with ImportDefence():
    from kivy.uix.boxlayout import BoxLayout

from globalstuff import *


class Pages(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', size_hint=(.15, .15),
                         pos_hint={'x': 0, 'top': 1}, **kwargs)

        labels = ['Save.', 'Scan.', 'Know.']
        actions = [
            lambda _: State().screen("Save"),
            lambda _: State().screen("Scan"),
            lambda _: State().screen("Know")
        ]
        buttons = [
            GreenButton(
                text=label,
                font_size=20,
                background_color=PAGES_BACKGROUND,
                font_name="Arial"
            )
            for label in labels]
        for button, action in zip(buttons, actions):
            button.bind(on_press=action)
            self.add_widget(button)


if __name__ == '__main__':
    print("This module provides a GUI widget (BoxLayout),")
    print("That should be used on each screen to transition between Save, Scan, and Know.")
