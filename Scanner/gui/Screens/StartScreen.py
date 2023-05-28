from import_handler import ImportDefence
with ImportDefence():
    from kivy.uix.relativelayout import RelativeLayout
    from kivy.uix.label import Label
    from kivy.uix.screenmanager import Screen
    from gui.Screens.Pages import Pages
    from kivy.uix.image import Image
    from globalstuff import *
    from gui.Hover import Hover

class StartScreen(Screen):
    """Builds an interface that looks like this:

    ```md
    The Window (Unicode Box Art):
        ┌────────────────────────────────────────────┐
        │                  [#1 Title]                │
        │  #4 Save.                                  │
        │  #5 Scan.  #2 instructions                 │
        │  #6 Know.                                  │
        │                                            │
        │                                            │
        │                  #3 Content                │
        │                                            │
        │                                            │
        └────────────────────────────────────────────┘
    ```

    Args:
        Screen (kivy): the base class for a screen.
    """

    def __init__(self, **kw):
        name = 'Start'
        super().__init__(name=name, **kw)
        Hover.enter(name)

        everything = RelativeLayout()

        from kivy.core.window import Window
        ratio = 1.6
        background = Image(
            source='background.png',
            pos_hint={'center_x': .5, 'center_y': .5},
            size_hint=(None, None),
            size=tuple(s * ratio for s in Window.size),
            allow_stretch=True,
            keep_ratio=False
        )
        everything.add_widget(background)

        logo = Image(source='favicon.png', pos_hint={'center_x': .695, 'center_y': .906})
        everything.add_widget(logo)

        title = Label(
            text=f"[color={GREEN}]Network Scannıng[/color]",  # `logo` replaces the i dot.
            size=(0, 3 * TITLE_HEIGHT),
            size_hint=(1, None),
            font_size=3 * TITLE_FONT_SIZE,
            underline=True,
            pos_hint={'center_x': .5, 'top': 1},
            markup=True
        )
        everything.add_widget(title)
        instructions = Label(
            text=f"<--- Click on any screen to enter it.",
            font_size=20,
            size=(0, TITLE_HEIGHT),
            size_hint=(1, None),
            pos_hint={'center_x': .22, 'top': 1},
            markup=True
        )
        everything.add_widget(instructions)
        main = Label(
            text=f"Welcome to the Network Scanner!\nEnjoy your stay.",
            font_size=30,
            pos_hint={'center_x': .5, 'center_y': 0.6},
            markup=True,
            halign="center", valign="middle"
        )
        everything.add_widget(main)
        more = Label(
            text=f"Use `Scan` to execute scans on your local network.\nUse `Save` to save the results of those scans.\nUse `Know` to analyse your knowledge.\n\nMake sure you have permission to execute actions on the network!",
            font_size=20,
            pos_hint={'center_x': .5, 'center_y': 0.4},
            markup=True,
            halign="center", valign="middle"
        )
        everything.add_widget(more)

        # Objects #4, #5, #6 -- Page frippery (top left corner)
        everything.add_widget(Pages())

        self.add_widget(everything)


if __name__ == '__main__':
    print("This file provides the Start Screen for the gui.\n")
    print("""
        ┌────────────────────────────────────────────┐
        │                  [#1 Title]                │
        │  #4 Save.                                  │
        │  #5 Scan.  #2 instructions                 │
        │  #6 Know.                                  │
        │                                            │
        │                                            │
        │                  #3 Content                │
        │                                            │
        │                                            │
        └────────────────────────────────────────────┘""")
