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

from kivy.clock import Clock
from kivy.config import Config
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.utils import escape_markup
from kivy.graphics import Color, Ellipse, Rectangle, Line
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.scrollview import ScrollView
from kivy.app import App

import sys
import traceback

__author__ = 'Shaked Dan Zilberman'


# --- GUI-invoked code ---

def display_configuration():
    if state.highlighted_scan is None:
        name = "scans"
    elif state.highlighted_scan is DummyScan():
        name = "scans"
    else:
        name = state.highlighted_scan.name
    popup(f"Configuration of {name}", "Coming soon.")
    # win32api.MessageBox(0, "content", "title", 0x00000000)


def activate(x):
    if state.ask_for_permission():
        s = state.highlighted_scan
        if Register().is_running(s.name) or s.is_running:
            popup(
                "Cannot run scan",
                f"**This scan is already running!**\n\n{s.name}",
                error=True
            )
            return

        # print(f"Play {s.name}!")
        if s is DummyScan():
            popup("Cannot start scan", f"Select a scan first!", warning=True)
        if popup("Start scan", f"Starting the scan: {s.name}", cancel=True):
            Register().start(s.name, s.act, s.finished)
        else:
            popup(
                "Canceled scan",
                "The scan has been cancelled.\n\n\n<sub><sup>Cancel culture, I'm telling ya.</sup></sub>",
                warning=True
            )


# --- Classes ---
class Scan:
    font_size = BUTTON_COLUMN_FONT_SIZE
    background_color = button_column_background

    def __init__(self, name, action, parent):
        self.name = name
        self.action = action
        self.x = 0
        self.is_running = False

        self.button = Button(
            text=name,
            font_size=Scan.font_size,
            background_color=Scan.background_color,
            font_name="Roboto"
        )
        self.button.bind(on_press=lambda x: self.select(x))
        parent.add_raw(self.button)
        Hover.add(self.button)

    def select(self, x):
        if state.highlighted_scan == self:
            state.scan(DummyScan())
            return
        state.scan(self)
        with self.button.canvas.after:
            self.highlight = Color(*SCAN_HIGHLIGHT)
            self.highlight_rect = Rectangle(
                pos=(self.button.x, self.button.y),
                size=(self.button.width, self.button.height)
            )
        self.x = x

    def deselect(self):
        self.button.canvas.after.clear()

    def act(self):
        self.is_running = True
        self.button.text += '...'
        try:
            self.action()
        except TypeError:
            self.action(self.x)

    def finished(self):
        self.is_running = False
        if self.button.text.endswith('...') and not Register().is_infinite_scan(self.button.text):
            self.button.text = self.button.text[:-3]


class DummyScan(Scan):
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.name = "Dummy"
        self.is_running = False

    def select(self, x):
        pass

    def deselect(self):
        pass

    def act(self):
        # win32api.MessageBox(0, "You must first select a scan to run.", "Running without a scan", 0x00000000)
        popup("Running without a scan", "You must first select a scan to run.")
        # raise NotImplementedError("A DummyScan cannot be `.act`ed upon.")

    def finished(self):
        pass


class Diagram:
    """This is a class responsible for the hovering diagram, that is created in a separate window when the 'Fullscreen' button is pressed.
    Uses `tkinter` (not `kivy`, like the other parts). Black diagram on white background. Can be expanded in both directions.
    """

    def __init__(self):
        """A few parts:
        - Tk stuff (root, title, width & height)
        - tk.Canvas initialisation (+ fit window)
        - fields for `G` (the graph) and `diagram_cache` (see `Diagram.update`)
        - bind `self.resize` to the relevant user operation
        - bind `self.try_close` to the relevant user operation
        - initial `update` and `hide`.
        """
        self.root = tk.Tk()
        self.root.title("Network Diagram")
        self.width, self.height = DIAGRAM_DIMENSIONS

        self.canvas = tk.Canvas(
            self.root,
            bg=color_to_hex(bg_color),
            height=self.height,
            width=self.width,
            borderwidth=0,
            highlightthickness=0
        )
        self.canvas.pack(expand=True, fill='both')

        self.graph = G
        self.diagram_cache = None

        self.canvas.bind('<Configure>', self.resize)
        self.update()

        self.hide()
        self.root.protocol("WM_DELETE_WINDOW", self.try_close)

    def try_close(self):
        """To prevent the user from really closing this window if the source (kivy) is still open."""
        if is_kivy_running:
            self.hide()
        else:
            self.root.destroy()

    def renew(self, G: nx.Graph):
        """Update the rendered graph.
        Saves a `G.copy()` to `self.graph` and calls `self.update()`.
        Args:
            G (nx.Graph): the new graph.
        """
        renewed = G.copy()
        try:
            if not nx.utils.graphs_equal(renewed, self.graph):
                self.graph = renewed
                self.update()
                return True
        except KeyError as e:
            print(e)
        return False

    def hide(self):
        self.root.withdraw()

    def show(self):
        self.root.update()
        self.root.deiconify()

    def resize(self, event):
        # `geomery` is of the form "{width}x{height}+{x}+{y}"
        geometry = self.root.geometry().replace('+', 'x')
        # Uses this property of the `map` function: "Stops when the shortest
        # iterable is exhausted."
        # Convert to `int` with base 10, but only twice.
        self.width, self.height = map(int, geometry.split('x'), [10, 10])
        self.update()

    def update(self):
        if self.diagram_cache is None:
            self.diagram_cache = TKDiagram(self, DIAGRAM_POINT_RADIUS)
        render_diagram(
            self.diagram_cache,
            0,
            0,
            self.width,
            self.height,
            bg_color,
            fg_color,
            -50
        )
        self.changed = False


class TKDiagram:
    def __init__(self, diagram, radius):
        self.diagram = diagram
        self.radius = radius
        self.color_cache = '#000000'

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, exception_traceback):
        pass

    def color(self, r=None, g=None, b=None):
        if r is None:
            return self.color_cache
        self.color_cache = color_to_hex((r, g, b))

    def rectangle(self, x, y, w, h):
        self.diagram.canvas.create_rectangle(x, y, w, h, fill=self.color())

    def circle(self, x, y, node):
        r = self.radius
        x0 = x - r
        y0 = y - r
        x1 = x + r
        y1 = y + r
        self.diagram.canvas.create_text(
            x0,
            y0 - 30,
            text=node.to_string('\n'),
            fill=self.color(),
            font=("Consolas", 10),
            justify=tk.CENTER
        )
        return self.diagram.canvas.create_oval(
            x0, y0, x1, y1, fill=self.color())

    def line(self, x0, y0, x1, y1, stroke):
        self.diagram.canvas.create_line(
            x0, y0, x1, y1, width=stroke, fill=self.color())

    def __contains__(self, pos):
        return True


class KivyDiagram:
    def __init__(self, widget, radius):
        self.widget = widget
        self.radius = radius

    def __enter__(self):
        self.widget.canvas.__enter__()
        return self

    def __exit__(self, exception_type, exception_value, exception_traceback):
        self.widget.canvas.__exit__()

    def color(self, r, g, b):
        Color(r, g, b)

    def rectangle(self, x, y, w, h):
        Rectangle(pos=(x, y), size=(w, h))

    def circle(self, x, y, node):
        r = self.radius
        Ellipse(pos=(x - r, y - r), size=(2 * r, 2 * r))

    def line(self, x0, y0, x1, y1, stroke):
        Line(points=(x0, y0, x1, y1), width=stroke)

    def __contains__(self, pos):
        x, y = pos
        r = self.radius
        def collides(x0, y0): return self.widget.collide_point(x0, y0)
        if r == 0:
            return collides(x, y)
        return collides(x + r, y + r) and collides(x - r, y - r)


# --- Rendering ---
def update_kivy_diagram(painter, _=0):
    """Renders stuff on the diagram (object #9).
    Caches `painter` on first call.
    Args:
        painter (MyPaintWidget): the diagram to paint on. **This is passed in once**. All next calls will use the object that was given in the first call.
        value (int): just for compatibility.
    """
    if hasattr(update_kivy_diagram, 'cache'):
        painter = update_kivy_diagram.cache
    else:
        update_kivy_diagram.cache = painter
        update_kivy_diagram.diagram_cache = KivyDiagram(
            painter, DIAGRAM_POINT_RADIUS
        )

    render_diagram(update_kivy_diagram.diagram_cache, *painter.pos,
                   *painter.size, bg_color, fg_color, -TITLE_HEIGHT)


def render_diagram(draw, x, y, w, h, bg, fg, dh=0):
    """An abstract representation of the algorithm used to render the diagram.
    To interface with ~reality~ the screen, it uses the `draw` argument,
    which is a context manager supporting various methods.
    Currently, there are two implementations: `KivyDiagram` and `TKDiagram`.
    """
    scale = min(w, h + dh) * DIAGRAM_SCALE
    stroke = 1
    H = G.copy()

    pos = nx.kamada_kawai_layout(H, center=(x + w / 2, y + h / 2), scale=scale)

    with draw:
        draw.color(*bg)
        draw.rectangle(x, y, w, h)
        draw.color(*fg)

        for node, (x0, y0) in pos.items():
            if (x0, y0) in draw:
                draw.circle(x0, y0, node)

        for edge in H.edges:
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            if (x0, y0) in draw and (x1, y1) in draw:
                draw.line(x0, y0, x1, y1, stroke)


# --- Screens ---

# --- Basically Main ---
class State:
    def __init__(self) -> None:
        self.screenManager = None
        self.currentScreen = None
        self.permission = False
        self.highlighted_scan = DummyScan()
        self.scans = [DummyScan()]

    def setScreenManager(self, screens):
        self.screenManager = screens

    def screen(self, name=None):
        if name is None:
            return self.currentScreen
        Hover.enter(name)
        self.screenManager.current = name
        self.currentScreen = name

    def resize_callback(self, *_):
        # Called from Hover's `._bind`.
        def _resize_callback(*_):
            self.scan(self.highlighted_scan)
            self.highlighted_scan.select(0)

        Clock.schedule_once(_resize_callback, 0.15)

    def scan(self, scan):
        if scan not in self.scans:
            self.scans.append(scan)
        self.highlighted_scan = scan
        for scan in self.scans:
            scan.deselect()

    def ask_for_permission(self):
        if not self.permission:
            self.permission = win32api.MessageBox(
                0,
                'Do you have legal permission to execute scans on this network?',
                'Confirm permission',
                0x00000004
            ) == 6
        return self.permission


class MyApp(App):
    """The main application, using `kivy`.
    Includes five screens:
    1. ScanScreen
    2. SaveScreen
    3. KnowScreen
    4. StartScreen (soon ******************)
    5. ViewScreen (only accessible through `KnowScreen.ImportButton`)


    Args:
        App (tk): the tkinter base app.
    """

    def build(self):
        self.title = 'Local Network Scanner'
        self.icon = 'favicon.png'
        from kivy.core.window import Window
        Window.size = (1300, 800)
        global state
        state = State()
        screens = ScreenManager(transition=FadeTransition())
        state.setScreenManager(screens)

        screens.add_widget(ScanScreen())
        screens.add_widget(SaveScreen())
        screens.add_widget(KnowScreen())
        screens.add_widget(ViewScreen())

        state.screen('Scan')

        Hover.start()

        return screens


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
