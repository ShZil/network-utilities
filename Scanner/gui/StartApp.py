from import_handler import ImportDefence
with ImportDefence():
    from kivy.config import Config

import sys
import traceback
from gui.App import MyApp
from gui.Diagrams import Diagram
from globalstuff import terminator
import threading

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
    print("This file is responsible for starting the kivy and tkinter gui.")
    print("The callers are responsible for thread handling: start_tk on main, start_kivy on separate thread.")
