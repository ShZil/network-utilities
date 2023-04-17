from import_handler import ImportDefence
with ImportDefence():
    from kivy.uix.relativelayout import RelativeLayout
    from kivy.uix.label import Label

from globalstuff import *
from Screens.Pages import Pages

class ScanScreenMiddleDiagram(RelativeLayout):
    """Builds the middle diagram used in the screen 'Scan'.

    ```md
        Scan Screen
        ┌────────────────────────────────────────────╥─ . . .
        │                  [#1 Title]                ║
        │  #4 Save.                                  ║
        │  #5 Scan.                                  ║
        │  #6 Know.                                  ║
        │           #9 D                             ║
        │                I                           ║
        │                  A                         ║
        │                    G                       ║
        │                      R                     ║
        │                        A                   ║
        │                          M                 ║
        │    [#15 Play]            [#16 Fullscreen]  ║
        └────────────────────────────────────────────╨─ . . .
    ```

    Args:
        RelativeLayout (kivy): the diagram is a type of a Relative Layout, since widgets are placed sporadically.
    """

    def __init__(self, **kw):
        super().__init__(**kw)

        #     Object #1
        title = Label(
            text=f"[color={GREEN}]Local Network Scanner[/color]",
            size=(0, TITLE_HEIGHT),
            size_hint=(1, None),
            font_size=TITLE_FONT_SIZE,
            underline=True,
            pos_hint={'center_x': .5, 'top': 1},
            markup=True
        )

        #     Objects #4, #5, #6 -- Page frippery (top left corner)
        pages = Pages()

        #     Object #15
        play_button = GreenButton(text='▶',
                                  font_size=UNDER_DIAGRAM_FONT_SIZE,
                                  background_color=PAGES_BACKGROUND,
                                  size_hint=(.1, .1),
                                  pos_hint={'x': 0, 'y': 0},
                                  font_name="Symbols")
        play_button.bind(on_press=activate)

        #     Object #16    # Previous icon: 🔍
        open_diagram = GreenButton(text='⛶',
                                   font_size=UNDER_DIAGRAM_FONT_SIZE,
                                   background_color=PAGES_BACKGROUND,
                                   size_hint=(.1, .1),
                                   pos_hint={'right': 1, 'y': 0},
                                   font_name="Symbols")
        open_diagram.bind(on_press=lambda _: diagram.show())

        #     Object #9
        paint = MyPaintWidget(
            size_hint=(1, 1),
            pos_hint={'center_x': .5, 'center_y': .5}
        )
        paint.bind(pos=update_kivy_diagram, size=update_kivy_diagram)

        def update_diagrams(*_):
            update_kivy_diagram(paint)
            if diagram is not None:
                diagram.renew(G)
        Clock.schedule_interval(update_diagrams, 5)

        # Unite all widgets of the middle diagram.
        self.add_widget(paint)
        self.add_widget(pages)
        self.add_widget(open_diagram)
        self.add_widget(play_button)
        self.add_widget(title)


class ScanScreenRightColumn(ButtonColumn):
    """Builds the right column used in the screen 'Scan'.

    ```md
        Scan Screen
        . . . ─╥───────────────────────────┐
               ║   [#2 Conf]   [#3 Info]   │
               ╟───────────────────────────┤
               ║        [#7 ScanA]         │
               ║                           │
               ║        [#8 ScanB]         │
               ║                           │
               ║        [#9 ScanC]         │
               ║                           │
               ║        [#10 ScanD]        │
               ║                           │
               ║           . . .           │
               ║                           │
        . . . ─╨───────────────────────────┘
    ```

    Args:
        ButtonColumn (GridLayout): this inherits from ButtonColumn.
    """

    def __init__(self):
        super().__init__(width=RIGHT_COLUMN_WIDTH)

        #     Objects #2, #3 -- two operations on each scan
        operations = BoxLayout(orientation='horizontal', spacing=-3)
        operations.add_widget(
            OperationButton(
                '⚙',
                "Configure",
                lambda _: display_configuration()
            )
        )
        operations.add_widget(
            OperationButton(
                'ℹ',
                "Information",
                lambda _: display_information()
            )
        )  # Consider a '?' instead

        self.add_widget(operations)

        # Objects #7 - #10
        for name in db.get_scans():
            Scan(name, Register()[name], self)
            # print(name)
        # Scan('ICMP Sweep', lambda: print("ICMP!!!"), self)
        # Scan('ARP Sweep', lambda: print("ARP!!!"), self)
        # Scan('Live ICMP', lambda: print("ICMP..."), self)
        # Scan('Live ARP', lambda: print("ARP..."), self)
        # Scan('OS-ID', lambda: print("It's fun to stay in the O-S-I-D"), self)
        # Scan('TCP Ports', lambda: print("TCP! TCP! TCP!"), self)
        # Scan('UDP Ports', lambda: print("Uridine DiPhosphate (UDP) -- glycogen synthesis polymer"), self)
        # Scan('woo!', temp_increase_graph_degree, self)


class ScanScreen(Screen):
    """Builds an interface that looks like this:

    ```md
    The Window (Unicode Box Art):
        ┌────────────────────────────────────────────╥───────────────────────────┐
        │                  [#1 Title]                ║   [#2 Conf]   [#3 Info]   │
        │  #4 Save.                                  ╟───────────────────────────┤
        │  #5 Scan.                                  ║        [#7 ScanA]         │
        │  #6 Know.                                  ║                           │
        │           #9 D                             ║        [#8 ScanB]         │
        │                I                           ║                           │
        │                  A                         ║        [#9 ScanC]         │
        │                    G                       ║                           │
        │                      R                     ║        [#10 ScanD]        │
        │                        A                   ║                           │
        │                          M                 ║           . . .           │
        │    [#15 Play]            [#16 Fullscreen]  ║                           │
        └────────────────────────────────────────────╨───────────────────────────┘
    ```

    Args:
        Screen (kivy): the base class for a screen.
    """

    def __init__(self, **kw):
        name = 'Scan'
        super().__init__(name=name, **kw)
        Hover.enter(name)

        everything = BoxLayout(orientation='horizontal')
        everything.add_widget(ScanScreenMiddleDiagram())
        everything.add_widget(ScanScreenRightColumn())

        self.add_widget(everything)


if __name__ == '__main__':
    print("This file provides the Scan Screen for the gui.\n")
    print("""
        ┌────────────────────────────────────────────╥───────────────────────────┐
        │                  [#1 Title]                ║   [#2 Conf]   [#3 Info]   │
        │  #4 Save.                                  ╟───────────────────────────┤
        │  #5 Scan.                                  ║        [#7 ScanA]         │
        │  #6 Know.                                  ║                           │
        │           #9 D                             ║        [#8 ScanB]         │
        │                I                           ║                           │
        │                  A                         ║        [#9 ScanC]         │
        │                    G                       ║                           │
        │                      R                     ║        [#10 ScanD]        │
        │                        A                   ║                           │
        │                          M                 ║           . . .           │
        │    [#15 Play]            [#16 Fullscreen]  ║                           │
        └────────────────────────────────────────────╨───────────────────────────┘""")
