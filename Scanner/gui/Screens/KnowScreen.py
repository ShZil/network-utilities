from import_handler import ImportDefence
with ImportDefence():
    from kivy.uix.scrollview import ScrollView
    from kivy.uix.label import Label
    from kivy.uix.button import Button
    from kivy.uix.screenmanager import Screen
    from kivy.uix.boxlayout import BoxLayout
    from kivy.uix.relativelayout import RelativeLayout

from threading import Thread
from gui.Hover import Hover
from gui.Screens.Pages import Pages
from gui.KivyExtensions import ButtonColumn, OperationButton
from gui.dialogs import get_string, popup
from gui.Configuration import display_configuration
from gui.Information import display_information
from gui.Activation import activate
from gui.ScanClasses import Analysis
from register import Register
from globalstuff import *
import db


def update_know_screen(text):
    return print("update_know_screen:", text)


class KnowScreen(Screen):
    """Builds an interface that looks like this:

    ```md
    The Window (Unicode Box Art):
        ┌────────────────────────────────────────────┐
        │                  [#1 Title]                │
        │  #4 Save.                                  │
        │  #5 Scan.                                  │
        │  #6 Know.                                  │
        │             #3 Device Profile              │
        │              #2 Data                       │
        │     [_______________________]              │
        │     [_______________________]              │
        │     [_______________________]              │
        │     [_______________________]              │
        │                                            │
        │                                            │
        └────────────────────────────────────────────┘
    ```

    Args:
        Screen (kivy): the base class for a screen.
    """

    def __init__(self, **kw):
        name = 'Know'
        super().__init__(name=name, **kw)
        Hover.enter(name)

        everything = RelativeLayout()
        title = Label(
            text=f"[color={GREEN}]Knowledge about Network[/color]",
            size=(0, TITLE_HEIGHT),
            size_hint=(1, None),
            font_size=TITLE_FONT_SIZE,
            underline=True,
            pos_hint={'center_x': .42, 'top': 1},
            markup=True
        )
        everything.add_widget(title)

        body = BoxLayout(orientation='horizontal')
        body.add_widget(KnowScreenInfoLabel())
        body.add_widget(KnowScreenRightColumn())
        everything.add_widget(body)
        everything.add_widget(Pages())

        self.add_widget(everything)


class KnowScreenRightColumn(ButtonColumn):
    """Builds the right column used in the screen 'Know'.

    ```md
        Know Screen
        . . . ─╥───────────────────────────┐
               ║   [#2 Conf]   [#3 Info]   │
               ╟───────────────────────────┤
               ║        [#7 KnowA]         │
               ║                           │
               ║        [#8 KnowB]         │
               ║                           │
               ║        [#9 KnowC]         │
               ║                           │
               ║        [#10 KnowD]        │
               ║                           │
               ║           . . .           │
               ║                           │
        . . . ─╨───────────────────────────┘
    ```

    Args:
        ButtonColumn (GridLayout): this inherits from ButtonColumn.
    """

    def __init__(self):
        super().__init__(width=RIGHT_COLUMN_WIDTH * 0.8)

        #     Objects #2, #3 -- two operations on each analysis
        operations = BoxLayout(orientation='horizontal', spacing=-3, size_hint=(0.3, None))
        operations.add_widget(OperationButton('🎓', "Analyse", activate))
        operations.add_widget(OperationButton('⚙', "Config", display_configuration))
        operations.add_widget(OperationButton('ℹ', "Info", display_information))

        self.add_widget(operations)

        # Objects #7 - #10
        for name in db.get_analyses():
            Analysis(name, Register()[name], self)


class KnowScreenInfoLabel(ScrollView):
    """Holds the requested data in string format, displayed to the user.
    Has a scrolling mechanic.

    Args:
        Label (kivy): the base class from kivy.
    """

    def __init__(self, **kwargs):
        super().__init__(width=1200, **kwargs)
        self.label = Label(
            text='\n\n\n\n\n\n\n\nLoading data...',
            color=(1, 1, 1, 1),
            font_size=20,
            font_name="Monospace",
            size_hint_y=None,
            text_size=(self.width, None),
            halign='center'
        )
        self.label.bind(texture_size=self.label.setter('size'))
        self.add_widget(self.label)
        global update_know_screen
        update_know_screen = self.data

    def data(self, text):
        if isinstance(text, str):
            self.label.text = text
        else:
            try:
                items = text.tablestring()
                # print('\n'.join(items))
            except AttributeError:
                items = [str(x) for x in text]
            self.label.text = '\n\n\n\n\n\n\n' + '\n'.join(items)


if __name__ == '__main__':
    print("This file provides the Know Screen for the gui.\n")
    print("""
        ┌────────────────────────────────────────────┐
        │                  [#1 Title]                │
        │  #4 Save.                                  │
        │  #5 Scan.                                  │
        │  #6 Know.                                  │
        │             #3 Device Profile              │
        │                   #2 Data                  │
        │          [_______________________]         │
        │          [_______________________]         │
        │          [_______________________]         │
        │          [_______________________]         │
        │                                            │
        │                                            │
        └────────────────────────────────────────────┘""")
