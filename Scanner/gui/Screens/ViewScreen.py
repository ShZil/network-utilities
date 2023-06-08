from import_handler import ImportDefence
with ImportDefence():
    from kivy.uix.scrollview import ScrollView
    from kivy.uix.label import Label
    from kivy.uix.screenmanager import Screen
    from kivy.uix.boxlayout import BoxLayout
    from kivy.uix.relativelayout import RelativeLayout

from gui.Hover import Hover
from globalstuff import *
from gui.Screens.Pages import Pages


def update_view_screen(text):
    return print("update_view_screen:", text)


class ViewScreenInfo(ScrollView):
    """Holds the requested data in string format, displayed to the user.
    Has a scrolling mechanic.

    Args:
        Label (kivy): the base class from kivy.
    """

    def __init__(self, **kwargs):
        super().__init__(width=1100, **kwargs)
        self.label = Label(
            text='Loading...',
            color=(1, 1, 1, 1),
            font_size=20,
            font_name="Monospace",
            size_hint_y=None,
            text_size=(self.width, None),
            halign='center'
        )
        self.label.bind(texture_size=self.label.setter('size'))
        self.add_widget(self.label)
        global update_view_screen
        update_view_screen = self.data

    def data(self, text):
        if isinstance(text, str):
            self.label.text = text
        else:
            raise TypeError()


class ViewScreen(Screen):
    """Builds an interface that looks like this:

    ```md
    The Window (Unicode Box Art):
        ┌────────────────────────────────────────────┐
        │                  [#1 Title]                │
        │  #3 Know.                                  │
        │  #4 Scan.                                  │
        │  #5 Know.                                  │
        │                                            │
        │                   #2 Data                  │
        │          [_______________________]         │
        │          [_______________________]         │
        │          [_______________________]         │
        │          [_______________________]         │
        │                                            │
        │                                            │
        └────────────────────────────────────────────┘
    ```

    Args:
        Screen (kivy): the base class for a screen.
    """

    def __init__(self, **kw):
        name = 'View'
        super().__init__(name=name, **kw)
        Hover.enter(name)

        everything = RelativeLayout()
        everything.add_widget(Pages())

        body = BoxLayout(orientation='vertical')
        title = title = Label(
            text=f"[color={GREEN}]View Past Scan[/color]",
            size=(0, TITLE_HEIGHT),
            size_hint=(1, None),
            font_size=TITLE_FONT_SIZE,
            underline=True,
            pos_hint={'center_x': .5, 'top': 1},
            markup=True
        )
        body.add_widget(title)
        body.add_widget(ViewScreenInfo())
        everything.add_widget(body)

        self.add_widget(everything)


if __name__ == '__main__':
    print("This file provides the View Screen for the gui.")
    print("It is only accessable through the Import button on the Save Screen.\n")
    print("""
        ┌────────────────────────────────────────────┐
        │                  [#1 Title]                │
        │  #3 Know.                                  │
        │  #4 Scan.                                  │
        │  #5 Know.                                  │
        │                                            │
        │                   #2 Data                  │
        │          [_______________________]         │
        │          [_______________________]         │
        │          [_______________________]         │
        │          [_______________________]         │
        │                                            │
        │                                            │
        └────────────────────────────────────────────┘""")
