from import_handler import ImportDefence
with ImportDefence():
    from kivy.uix.screenmanager import Screen
    from kivy.uix.relativelayout import RelativeLayout
    from kivy.uix.label import Label

from globalstuff import *
from threading import Thread
from files import importer, exporter
from gui.Hover import Hover, HoverReplaceBackground
from gui.dialogs import popup
from gui.KivyExtensions import GreenButton
from gui.Screens.Pages import Pages


class SaveScreenExportButton(GreenButton):
    def __init__(self, **kwargs):
        super().__init__('↥', size_hint=(.15, .15), pos_hint={'x': 0.2, 'top': 0.75},
                         font_name="Symbols+", background_color=(0, 0, 0, 1), **kwargs)
        HoverReplaceBackground(
            self,
            'Export',
            SAVE_BUTTONS_FONT_SIZE,
            SAVE_BUTTONS_HOVER_BACKGROUND
        )
        self.bind(on_press=self.export)

    def export(self, _):
        def _exporting():
            try:
                path = exporter()
                print("Showing popup")
                popup("Exported", f"Saved the scan to {path}")
            except FileExistsError:
                popup(
                    "File Exists Error",
                    "A file already exists in that path.",
                    error=True
                )
            except FileNotFoundError:
                popup(
                    "File Error",
                    "A file cannot be written in that location.",
                    error=True
                )
        Thread(target=_exporting).start()


class SaveScreenImportButton(GreenButton):
    def __init__(self, **kwargs):
        super().__init__('⭳', size_hint=(.15, .15), pos_hint={'x': 0.65, 'top': 0.75},
                         font_name="Symbols++", background_color=(0, 0, 0, 1), **kwargs)
        HoverReplaceBackground(
            self,
            'Import',
            SAVE_BUTTONS_FONT_SIZE,
            SAVE_BUTTONS_HOVER_BACKGROUND
        )
        self.bind(on_press=self.do_import)

    def do_import(self, _):
        def _importing():
            content = ''
            try:
                content = importer()
            except FileNotFoundError:
                popup("File Not Found", "The file you selected was not found.")
            except ValueError as e:
                popup("Error in parsing Scan File", e.args[0])
            try:
                if content != '':
                    update_view_screen(content)
                else:
                    update_view_screen("Couldn't decrypt file.")
            except Exception as e:
                print(e)

        Thread(target=_importing).start()
        State().screen("View")


class SaveScreen(Screen):
    """Builds an interface that looks like this:

    ```md
    The Window (Unicode Box Art):
        ┌────────────────────────────────────────────┐
        │                  [#1 Title]                │
        │  #4 Save.                                  │
        │  #5 Scan.                                  │
        │  #6 Know.                                  │
        │                                            │
        │       #2 Export            #3 Import       │
        │                                            │
        │                                            │
        │                                            │
        │                                            │
        │                                            │
        │                                            │
        └────────────────────────────────────────────┘
    ```

    Args:
        Screen (kivy): the base class for a screen.
    """

    def __init__(self, **kw):
        name = 'Save'
        super().__init__(name=name, **kw)
        Hover.enter(name)

        everything = RelativeLayout()
        title = Label(
            text=f"[color={GREEN}]Saving and Opening Scans[/color]",
            size=(0, TITLE_HEIGHT),
            size_hint=(1, None),
            font_size=TITLE_FONT_SIZE,
            underline=True,
            pos_hint={'center_x': .5, 'top': 1},
            markup=True
        )
        everything.add_widget(title)
        everything.add_widget(Pages())
        everything.add_widget(SaveScreenExportButton())
        everything.add_widget(SaveScreenImportButton())
        # *************** add the recents
        # everything.add_widget(SaveScreenRecents())

        self.add_widget(everything)


if __name__ == '__main__':
    print("This file provides the Save Screen for the gui.\n")
    print("""
        ┌────────────────────────────────────────────┐
        │                  [#1 Title]                │
        │  #4 Save.                                  │
        │  #5 Scan.                                  │
        │  #6 Know.                                  │
        │                                            │
        │       #2 Export            #3 Import       │
        │                                            │
        │                                            │
        │                                            │
        │                                            │
        │                                            │
        │                                            │
        └────────────────────────────────────────────┘""")
