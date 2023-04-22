from import_handler import ImportDefence
with ImportDefence():
    from kivy.config import Config

import sys
from datetime import datetime
import traceback
from gui.App import MyApp
from gui.Diagrams import Diagrams, TKDiagram
from globalstuff import terminator
import threading

def start_kivy():
    """Starts the `kivy` app, and handles the `tkinter` diagram's closing."""
    global is_kivy_running
    try:
        is_kivy_running = True
        # disable multi-touch emulation
        Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
        MyApp().run()
    except Exception as e:
        traceback.print_exc()
        print(
            f"{type(e).__name__} at {__file__}:{e.__traceback__.tb_lineno}: {e}\n{datetime.now()}",
            file=open('error log.txt', 'a', encoding='utf-8')
        )
    finally:
        is_kivy_running = False
        try:
            TKDiagram().show()
        except RuntimeError:
            pass
        root = TKDiagram().root
        root.after(1, root.destroy)
        terminator.set()
        print('\n'.join([str(thread) for thread in threading.enumerate()]))
        # sys.exit()
start_kivy.__name__ = 'Main GUI Thread'


def start_tk():
    """Starts the `tkinter` diagram in the background.
    This has to be on the main thread (because `tkinter` said so)."""
    Diagrams().add(TKDiagram())
    TKDiagram().root.mainloop()  # main thread waits here until the user leaves the application.


if __name__ == '__main__':
    print("This file is responsible for starting the kivy and tkinter gui.")
    print("The callers are responsible for thread handling: start_tk on main, start_kivy on separate thread.")
