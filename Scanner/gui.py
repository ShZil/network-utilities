from import_handler import ImportDefence
with ImportDefence():
    import kivy
    import networkx as nx
    import tkinter as tk
    from threading import Thread
    import numpy  # for networkx
    import scipy  # for networkx
    import win32api
    import PyQt5
    import markdown
    import re
kivy.require('2.1.0')

from globalstuff import G, terminator
from register import Register
from gui.Screens.ScanScreen import ScanScreen
from gui.Screens.SaveScreen import SaveScreen
from gui.Screens.KnowScreen import KnowScreen
from util import color_to_hex

from kivy.config import Config
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.utils import escape_markup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.widget import Widget
from kivy.uix.scrollview import ScrollView

import sys
import traceback

__author__ = 'Shaked Dan Zilberman'

# --- Basically Main ---
def start_kivy():
    """Starts the `kivy` app, and handles the `tkinter` diagram's closing."""
    global is_kivy_running, diagram
    try:
        is_kivy_running = True
        # disable multi-touch emulation
        Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
        MyApp().run()
    except Exception as e:
        traceback.print_exc()
        print(
            f"{type(e).__name__} at {__file__}:{e.__traceback__.tb_lineno}: {e}",
            file=sys.stderr
        )
    finally:
        is_kivy_running = False
        assert diagram is not None
        diagram.show()
        diagram.root.after(1, diagram.root.destroy)
        terminator.set()
        import threading
        print('\n'.join([str(thread) for thread in threading.enumerate()]))
        # sys.exit()
start_kivy.__name__ = 'Main GUI Thread'


def start_tk():
    """Starts the `tkinter` diagram in the background.
    This has to be on the main thread (because `tkinter` said so)."""
    global diagram
    diagram = Diagram()
    diagram.root.mainloop()


if __name__ == '__main__':
    raise NotImplementedError("Use `exe.py` instead.")
    print("Adding the fonts...")
    add_font()
    prestart()
    print("Starting kivy...")
    Thread(target=start_kivy).start()
    start_tk()
