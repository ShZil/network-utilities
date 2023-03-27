import sys
import traceback
from ipconfig import ipconfig
from import_handler import ImportDefence
with ImportDefence():
    import kivy
    import networkx as nx
    import tkinter as tk
    from threading import Thread, Event, enumerate as enumerate_threads
    import numpy, scipy  # for networkx
    import win32api
    import PyQt5
    import markdown
    import re
kivy.require('2.1.0')

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, Ellipse, Rectangle, Line
from kivy.core.text import LabelBase
from kivy.utils import escape_markup
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.config import Config
from kivy.clock import Clock
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt


from util import one_cache
import db
from register import Register
from files import importer, exporter

__author__ = 'Shaked Dan Zilberman'


# --- Global Values ---
from globalstuff import G
diagram = None
state = None
is_kivy_running = True
terminator = Event()
update_know_screen = lambda text: print(text)
update_view_screen = lambda text: print(text)


# --- Design Settings ---
bg_color = (0, 0, .01)  # tuple[float]: rgb
fg_color = (0.023, 0.92, 0.125)  # tuple[float]: rgb
button_column_background = [0.1, 1, 0.3, 1]  # list[float]: rgba
DIAGRAM_DIMENSIONS = (300, 300)  # tuple[int]: width, height
HOVER_REPLACE_FACTOR = 0.75  # float; under `HoverReplace`, `new_text_size = HOVER_REPLACE_FACTOR * old_text_size`, e.g. fontsizeof("Information") = 0.75 * fontsizeof("ℹ").
DIAGRAM_POINT_RADIUS = 5  # int: px
BUTTON_COLUMN_FONT_SIZE = 24  # int: px
SCAN_HIGHLIGHT = (0, 1, 0, 0.2)  # tuple[float]: rgba; used as overlay, do not set alpha=1, because that will hide the text.
OPERATION_BUTTON_FONT_SIZE = 30  # int: px
OPERATION_BUTTON_BACKGROUND = [0.8, 0.8, 0.8, 1]  # list[float]: rgba
TITLE_HEIGHT = 70  # int: px; the padding used by the kivy diagram from the top, to avoid hiding the title.
DIAGRAM_SCALE = 1 / 2.3  # float
PAGES_BACKGROUND = [0, 0, 0, 0]  # list[float]: rgba
TITLE_FONT_SIZE = 30  # int: px
GREEN = '00ff00'  # str: hex color
UNDER_DIAGRAM_FONT_SIZE = 30  # int: px
RIGHT_COLUMN_WIDTH = 300  # int: px; in Scan screen.
SAVE_BUTTONS_HOVER_BACKGROUND = [0, 0, 1, 1]  # list[tuple]: rgba
SAVE_BUTTONS_FONT_SIZE = 50  # int: px


# --- Small Utilities ---
color_hex = lambda rgb: '#%02x%02x%02x' % tuple([int(c * 255) for c in rgb])


def add_font():
    """Loads a font (`kivy`'s)."""
    def _add_font(path, name, fallback='fonts/Segoe UI Symbol.ttf'):
        path = f'fonts/{path}'
        try:
            LabelBase.register(name=name, fn_regular=path)
        except OSError:
            LabelBase.register(name=name, fn_regular=fallback)
    
    _add_font('BainsleyBold.ttf', 'Symbols')
    _add_font('Segoe UI Symbol.ttf', 'Symbols+')
    _add_font('Symbola.ttf', 'Symbols++')
    _add_font('Consolas.ttf', 'Monospace')

def prestart():
    """Code to execute when the program starts to load, but before the GUI windows start."""
    pass

# --- GUI-invoked code ---
def display_information():
    if state.highlighted_scan is DummyScan() or state.highlighted_scan is None:
        popup(f"General Information", general_information(), info=True)
    else:
        # win32api.MessageBox(0, information_about(state.highlighted_scan.name), f"Information about {state.highlighted_scan.name}", 0x00000000)
        popup(f"Information about {state.highlighted_scan.name}", information_about(state.highlighted_scan.name), info=True)


def popup(title, message, *, error=False, warning=False, question=False, info=False, cancel=False):
    if error or warning or question or info:
        with QApplication([]):
            md_text = markdown.markdown(message)
            html_text = f"<html><body>{md_text}</body></html>"

            popup = QMessageBox()
            popup.setWindowTitle(title)
            popup.setTextFormat(Qt.RichText)
            popup.setStandardButtons(QMessageBox.Ok)
            popup.setEscapeButton(QMessageBox.Ok)
            popup.setDefaultButton(QMessageBox.Ok)
            icon = QMessageBox.Critical if error else QMessageBox.Warning if warning else QMessageBox.Question if question else QMessageBox.Information
            popup.setIcon(icon)
            popup.setText(html_text)

            popup.exec_()
            return -1
    elif cancel:
        return win32api.MessageBox(0, message, title, 0x00000001) != 2
    else:
        win32api.MessageBox(0, message, title, 0x00000000)


def information_about(name: str) -> str:
    # Get the entry about the scan and destructure it
    entry = db.get_information_about_scan(name)
    name0, description, time, reward, certainty, safety, mode, repeats = entry
    if name != name0:
        raise ValueError(f"Weird name problem: key is `{name}`, database says `{name0}`.")
    
    # Generate phrases
    perrepeat = " per repeat" if repeats else ""
    hasrepeats = "Repeatable" if repeats else "Not repeatable"
    certainty_prompt = "That's pretty uncertain" if certainty <= 50 else "That's mildly certain" if certainty <= 80 else "That's pretty certain" if certainty <= 100 else "???"
    safety_prompt = "That's really unsafe" if safety <= 30 else "That's pretty unsafe" if safety <= 70 else "That's quite safe" if safety < 100 else "That's perfectly safe -- completely undetectable"

    # If the description includes a packet model, escape it into a code block.
    if not description.endswith(('.', '. ', '>')): description += '.'
    description = re.sub("<[^<>]+>", "<br>```\\g<0>```", description, flags=re.DOTALL)

    # Return everything in markdown format.
    return '\n'.join([
        f"# {name}",
        f"## Description",
        f"{description}",
        f"## Time estimate",
        f"{time}s{perrepeat}",
        f"## Risk and Reward",
        f"### What you get",
        f"{reward}",
        f"### How reliable is that?",
        f"{certainty}% certain that the data are correct.",
        f"{certainty_prompt}.",
        f"### Safety",
        f"Running this is {safety}% safe.",
        f"{safety_prompt}.",
        f"## Others",
        f"- {hasrepeats}",
        f"- Mode: {mode}"
    ])


def general_information() -> str:
    computers_in_network = len(ipconfig()["All Possible Addresses"])
    interface = ipconfig()["Interface"]
    mask = ipconfig()["Subnet Mask"]
    
    def _get_readable_threads():
        find_between = lambda s, brackets: (s.split(brackets[0]))[1].split(brackets[1])[0]

        threads = enumerate_threads()
        threads = [thread.name for thread in threads]
        threads = [name if '(' not in name else find_between(name, '()') for name in threads]
        uniques = set(threads)
        counts = [threads.count(name) for name in uniques]
        threads = [f"{count} × {name}" if count > 1 else name for name, count in zip(uniques, counts)]
        threads = ['* ' + name for name in threads]
        return threads
    
    from NetworkStorage import here, router
    return '\n\n'.join([
        f"# General Information",
        f"## This device",
        f"IPv4 Address: {here.ip}",
        f"Network Interface: {interface}",
        f"## Router (Gateway)",
        f"IPv4 Address: {router.ip}",
        f"## Local Network",
        f"Subnet mask: {mask}",
        f"Possible IPv4 addresses: {computers_in_network} addresses",
        f"## Others",
        f"Premission to scan: {state.permission}",
        f"## Current Threads",
        *_get_readable_threads()
    ])


def display_configuration():
    name = "scans" if state.highlighted_scan is DummyScan() or state.highlighted_scan is None else state.highlighted_scan.name
    popup(f"Configuration of {name}", "Coming soon.")
    # win32api.MessageBox(0, "content", "title", 0x00000000)

    
def activate(x):
    if state.ask_for_permission():
        s = state.highlighted_scan
        if Register().is_running(s.name) or s.is_running:
            popup("Cannot run scan", f"**This scan is already running!**\n\n{s.name}", error=True)
            return
        
        # print(f"Play {s.name}!")
        if s is DummyScan():
            popup("Cannot start scan", f"Select a scan first!", warning=True)
        if popup("Start scan", f"Starting the scan: {s.name}", cancel=True):
            Register().start(s.name, s.act, s.finished)
        else:
            popup("Canceled scan", "The scan has been cancelled.\n\n\n<sub><sup>Cancel culture, I'm telling ya.</sup></sub>", warning=True)


# --- Classes ---
class Scan:
    font_size = BUTTON_COLUMN_FONT_SIZE
    background_color = button_column_background

    def __init__(self, name, action, parent):
        self.name = name
        self.action = action
        self.x = 0
        self.is_running = False

        self.button = Button(text=name, font_size=Scan.font_size, background_color=Scan.background_color, font_name="Roboto")
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
            self.highlight_rect = Rectangle(pos=(self.button.x, self.button.y), size=(self.button.width, self.button.height))
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
        if self.button.text.endswith('...') and 'Live' not in self.button.text:
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

        self.canvas = tk.Canvas(self.root, bg=color_hex(bg_color), height=self.height, width=self.width, borderwidth=0, highlightthickness=0)
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
        # Uses this property of the `map` function: "Stops when the shortest iterable is exhausted."
        self.width, self.height = map(int, geometry.split('x'), [10, 10])  # Convert to `int` with base 10, but only twice.
        self.update()


    def update(self):
        if self.diagram_cache is None:
            self.diagram_cache = TKDiagram(self, DIAGRAM_POINT_RADIUS)
        render_diagram(self.diagram_cache, 0, 0, self.width, self.height, bg_color, fg_color)
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
        if r is None: return self.color_cache
        self.color_cache = color_hex((r, g, b))


    def rectangle(self, x, y, w, h):
        self.diagram.canvas.create_rectangle(x, y, w, h, fill=self.color())
    

    def circle(self, x, y):
        r = self.radius
        x0 = x - r
        y0 = y - r
        x1 = x + r
        y1 = y + r
        return self.diagram.canvas.create_oval(x0, y0, x1, y1, fill=self.color())
    

    def line(self, x0, y0, x1, y1, stroke):
        self.diagram.canvas.create_line(x0, y0, x1, y1, width=stroke, fill=self.color())

        
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
    

    def circle(self, x, y):
        r = self.radius
        Ellipse(pos=(x - r, y - r), size=(2 * r, 2 * r))
    

    def line(self, x0, y0, x1, y1, stroke):
        Line(points=(x0, y0, x1, y1), width=stroke)
    
    
    def __contains__(self, pos):
        x, y = pos
        r = self.radius
        collides = lambda x0, y0: self.widget.collide_point(x0, y0)
        if r == 0: return collides(x, y)
        return collides(x + r, y + r) and collides(x - r, y - r)


#     --- Hovering ---
class Hover:
    """Enables hovering cursor and behaviours. Uses singleton structure (because it accesses a system function of changing cursor).
    Includes two lists: `items`, where each item can change the cursor to `pointer` if hovered (`item.collide_point(x, y) -> True`);
    and `behaviors`, where each item is a `HoverBehavior`, and they do more exotic stuff, abstracted by `.show()` and `.hide()`.

    Raises:
        AttributeError: raised when `.add(item)` receives an `item` that has no method `.collide_point(int,int)`.
        TypeError: raised when `.add_behavior(behavior)` receives a `behavior` that is not of type `HoverBehavior`.
    """
    items = {}
    behaviors = {}
    current_screen = ""


    @staticmethod
    @one_cache
    def _bind():
        from kivy.core.window import Window
        Window.bind(mouse_pos=Hover.update)
        Window.bind(size=state.resize_callback)

    
    @staticmethod
    def add(instance):
        Hover._bind()
        if Hover.current_screen == "": raise KeyError("Hover cannot add without screen")
        try:
            instance.collide_point(0, 0)
        except AttributeError:
            raise AttributeError("The instance passed to `Hover.add` doesn't support `.collide_point(int,int)`.")
        Hover.items[Hover.current_screen].append(instance)


    @staticmethod
    def add_behavior(behavior):
        Hover._bind()
        if Hover.current_screen == "": raise KeyError("Hover cannot add without screen")
        if not isinstance(behavior, HoverBehavior):
            raise TypeError("The behavior passed to `Hover.add_behavior` isn't a `HoverBehavior`.")
        Hover.behaviors[Hover.current_screen].append(behavior)
        # A behaviour should support 3 methods: `collide_point(int,int)`, `show()`, and `hide()`, and that's enforced by the HoverBehaviour interface.
    

    def update(window, pos):
        if any([item.collide_point(*pos) for item in Hover.items[Hover.current_screen]]):
            window.set_system_cursor("hand")
        else:
            window.set_system_cursor("arrow")

        for behavior in Hover.behaviors[Hover.current_screen]:
            if behavior.collide_point(*pos):
                behavior.show()
            else:
                behavior.hide()
    

    def enter(screen: str):
        Hover.current_screen = screen
        if screen not in Hover.items:
            Hover.items[screen] = []
        if screen not in Hover.behaviors:
            Hover.behaviors[screen] = []
    

    @staticmethod
    def start():
        # Hide everything when the screen loads. Kinda misleading name -- this function is called last in initalisation -- it marks the start of the UI.
        for screen in Hover.behaviors.keys():
            for behavior in Hover.behaviors[screen]:
                behavior.hide()


class HoverBehavior:
    """
    Inherit from this class to create behaviours,
    and pass the instances to `Hover.add_behavior(...)`.
    """
    def show(self):
        raise NotImplementedError()


    def hide(self):
        raise NotImplementedError()

    
    def collide_point(self, x, y):
        raise NotImplementedError()


class HoverReplace(HoverBehavior):
    """A `HoverBehavior` that replaces the text shown on a label.
    When hovered, it displays the string in `text`,
    otherwise, it displays the initial string.
    """

    def __init__(self, widget, text, font_size, font="Arial"):
        self.widget = widget
        self.text = text
        self.save = self.widget.text
        self.font_size = font_size
        self.save_font = self.widget.font_name
        self.font = font
        Hover.add_behavior(self)
    

    def show(self):
        self.widget.text = self.text
        self.widget.font_name = self.font
        self.widget.font_size = self.font_size * HOVER_REPLACE_FACTOR
    

    def hide(self):
        self.widget.text = self.save
        self.widget.font_name = self.save_font
        self.widget.font_size = self.font_size


    def collide_point(self, x, y):
        return self.widget.collide_point(x, y)


class HoverReplaceBackground(HoverReplace):
    """A `HoverBehavior` that replaces the text shown on a label.
    When hovered, it displays the string in `text` (AND a different background colour),
    otherwise, it displays the initial string.
    """

    def __init__(self, widget, text, font_size, new_bg, font="Arial"):
        super().__init__(widget, text, font_size, font)
        self.save_bg = self.widget.background_color
        self.bg = new_bg
    

    def show(self):
        super().show()
        self.widget.background_color = self.bg
    

    def hide(self):
        super().hide()
        self.widget.background_color = self.save_bg


#     --- Kivy Extensions ---
class ButtonColumn(GridLayout):
    """Organises buttons in a column
    
    Args:
        GridLayout (tk): the superclass.
    """
    def __init__(self, width: int):
        super().__init__(cols=1, width=width, size_hint=(None, 1), spacing=[-3], padding=[-1, -3, -1, -3])
        self.buttons = []  # list of tuples `(button, callback)`
        self.background_color = button_column_background
        self.font_size = BUTTON_COLUMN_FONT_SIZE
    

    def add(self, text: str, callback=None):
        btn = Button(text=text, font_size=self.font_size, background_color=self.background_color, font_name="Roboto")
        if callback is not None:
            btn.bind(on_press=callback)
        super().add_widget(btn)
        Hover.add(btn)
        self.buttons.append((btn, callback))
        return btn
    

    def add_raw(self, button):
        super().add_widget(button)
        self.buttons.append((button, None))


class MyPaintWidget(Widget):
    """Responsible for the middle diagram (object #9).
    Args:
        Widget (tkinter widget): the superclass.
    """
    def init(self):
        update_kivy_diagram(self, 0)

    def on_touch_down(self, touch):
        update_kivy_diagram(self, 0)


class GreenButton(Button):
    """A button that has green background, and also adds itself to `Hover`."""
    def __init__(self, text, **kwargs):
        super().__init__(text=f'[color={GREEN}]{escape_markup(text)}[/color]', markup=True, **kwargs)
        Hover.add(self)


class OperationButton(Button):
    """A button that has grey background, adds itself to `Hover`, defines a `HoverReplace` on itself, and uses font `Symbols`."""
    def __init__(self, text, long_text, onclick, **kwargs):
        super().__init__(text=text, background_color=OPERATION_BUTTON_BACKGROUND, font_name="Symbols", **kwargs)
        Hover.add(self)
        HoverReplace(self, long_text, OPERATION_BUTTON_FONT_SIZE)
        self.bind(on_press=onclick)


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
        update_kivy_diagram.diagram_cache = KivyDiagram(painter, DIAGRAM_POINT_RADIUS)
    
    render_diagram(update_kivy_diagram.diagram_cache, *painter.pos, *painter.size, bg_color, fg_color, -TITLE_HEIGHT)


def render_diagram(draw, x, y, w, h, bg, fg, dh=0):
    """An abstract representation of the algorithm used to render the diagram.
    To interface with ~reality~ the screen, it uses the `draw` argument,
    which is a context manager supporting various methods.
    Currently, there are two implementations: `KivyDiagram` and `TKDiagram`.
    """
    scale = min(w, h + dh) * DIAGRAM_SCALE
    stroke = 1
    H = G.copy()
    
    pos = nx.kamada_kawai_layout(H, center=(x + w/2, y + h/2), scale=scale)
    
    with draw:
        draw.color(*bg)
        draw.rectangle(x, y, w, h)
        draw.color(*fg)
        
        for node, (x0, y0) in pos.items():
            if (x0, y0) in draw:
                draw.circle(x0, y0)
        
        for edge in H.edges:
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            if (x0, y0) in draw and (x1, y1) in draw:
                draw.line(x0, y0, x1, y1, stroke)


# --- Screens ---
class Pages(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', size_hint=(.15, .15), pos_hint={'x': 0, 'top': 1}, **kwargs)
        
        labels = ['Save.', 'Scan.', 'Know.']
        actions = [lambda _: state.screen("Save"), lambda _: state.screen("Scan"), lambda _: state.screen("Know")]
        buttons = [GreenButton(text=label, font_size=20, background_color=PAGES_BACKGROUND, font_name="Arial") for label in labels]
        for button, action in zip(buttons, actions):
            button.bind(on_press=action)
            self.add_widget(button)


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
        title = Label(text=f"[color={GREEN}]Local Network Scanner[/color]", size=(0, TITLE_HEIGHT), size_hint=(1, None), font_size=TITLE_FONT_SIZE, underline=True, pos_hint={'center_x': .5, 'top': 1}, markup=True)

        #     Objects #4, #5, #6 -- Page frippery (top left corner)
        pages = Pages()

        #     Object #15
        play_button = GreenButton(text='▶', font_size=UNDER_DIAGRAM_FONT_SIZE, background_color=PAGES_BACKGROUND, size_hint=(.1, .1), pos_hint={'x': 0, 'y': 0}, font_name="Symbols")
        play_button.bind(on_press=activate)

        #     Object #16    # Previous icon: 🔍
        open_diagram = GreenButton(text='⛶', font_size=UNDER_DIAGRAM_FONT_SIZE, background_color=PAGES_BACKGROUND, size_hint=(.1, .1), pos_hint={'right': 1, 'y': 0}, font_name="Symbols")
        open_diagram.bind(on_press=lambda _: diagram.show())

        #     Object #9
        paint = MyPaintWidget(size_hint=(1, 1), pos_hint={'center_x': .5, 'center_y': .5})
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
        operations.add_widget(OperationButton('⚙', "Configure", lambda _: display_configuration()))
        operations.add_widget(OperationButton('ℹ', "Information", lambda _: display_information()))  # Consider a '?' instead

        self.add_widget(operations)


        # Objects #7 - #10
        for name in db.get_scans():
            Scan(name, Register()[name], self)
            print(name)
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


class SaveScreenExportButton(GreenButton):
    def __init__(self, **kwargs):
        super().__init__('↥', size_hint=(.15, .15), pos_hint={'x': 0.2, 'top': 0.75}, font_name="Symbols+", background_color=(0, 0, 0, 1), **kwargs)
        HoverReplaceBackground(self, 'Export', SAVE_BUTTONS_FONT_SIZE, SAVE_BUTTONS_HOVER_BACKGROUND)
        self.bind(on_press=self.export)
    
    def export(self, _):
        def _exporting():
            try:
                path = exporter()
                popup("Exported", f"Saved the scan to {path}")
            except FileExistsError:
                popup("File Exists Error", "A file already exists in that path.", error=True)
            except FileNotFoundError:
                popup("File Error", "A file cannot be written in that location.", error=True)
        Thread(target=_exporting).start()


class SaveScreenImportButton(GreenButton):
    def __init__(self, **kwargs):
        super().__init__('⭳', size_hint=(.15, .15), pos_hint={'x': 0.65, 'top': 0.75}, font_name="Symbols++", background_color=(0, 0, 0, 1), **kwargs)
        HoverReplaceBackground(self, 'Import', SAVE_BUTTONS_FONT_SIZE, SAVE_BUTTONS_HOVER_BACKGROUND)
        self.bind(on_press=self.do_import)
    
    def do_import(self, _):
        def _importing():
            try:
                update_view_screen(importer())
            except FileNotFoundError:
                popup("File Not Found", "The file you selected was not found.", error=True)
            except ValueError as e:
                popup("Error in parsing Scan File", e.args[0], error=True)
        Thread(target=_importing).start()
        state.screen("View")
        


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
        │                            #7 Recent1      │
        │                            #8 Recent2      │
        │                            #9 Recent3      │
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
        title = Label(text=f"[color={GREEN}]Saving and Opening Scans[/color]", size=(0, TITLE_HEIGHT), size_hint=(1, None), font_size=TITLE_FONT_SIZE, underline=True, pos_hint={'center_x': .5, 'top': 1}, markup=True)
        everything.add_widget(title)
        everything.add_widget(Pages())
        everything.add_widget(SaveScreenExportButton())
        everything.add_widget(SaveScreenImportButton())
        # *************** add the recents
        # everything.add_widget(SaveScreenRecents())

        self.add_widget(everything)


class KnowScreenInfoLabel(ScrollView):
    """Holds the requested data in string format, displayed to the user.
    Has a scrolling mechanic.

    Args:
        Label (kivy): the base class from kivy.
    """
    def __init__(self, **kwargs):
        super().__init__(width=1100, **kwargs)
        self.label = Label(text='No data', color=(1, 1, 1, 1), font_size=20, font_name="Monospace", size_hint_y=None, text_size=(self.width, None), halign='center')
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
            self.label.text = '\n'.join(items)


class ViewScreenInfo(ScrollView):
    """Holds the requested data in string format, displayed to the user.
    Has a scrolling mechanic.

    Args:
        Label (kivy): the base class from kivy.
    """
    def __init__(self, **kwargs):
        super().__init__(width=1100, **kwargs)
        self.label = Label(text='Loading...', color=(1, 1, 1, 1), font_size=20, font_name="Monospace", size_hint_y=None, text_size=(self.width, None), halign='center')
        self.label.bind(texture_size=self.label.setter('size'))
        self.add_widget(self.label)
        global update_view_screen
        update_view_screen = self.data
    

    def data(self, text):
        if isinstance(text, str):
            self.label.text = text
        else:
            raise TypeError()


class KnowScreen(Screen):
    """Builds an interface that looks like this:
    
    ```md
    The Window (Unicode Box Art):
        ┌────────────────────────────────────────────┐
        │                  [#1 Title]                │
        │  #4 Save.                                  │
        │  #5 Scan.                                  │
        │  #6 Know.                                  │
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
        name = 'Know'
        super().__init__(name=name, **kw)
        Hover.enter(name)

        everything = BoxLayout(orientation='vertical')
        title = Label(text=f"[color={GREEN}]Knowledge about Network[/color]", size=(0, TITLE_HEIGHT), size_hint=(1, None), font_size=TITLE_FONT_SIZE, underline=True, pos_hint={'center_x': .5, 'top': 1}, markup=True)
        everything.add_widget(title)
        everything.add_widget(Pages())
        everything.add_widget(KnowScreenInfoLabel())

        self.add_widget(everything)


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

        everything = BoxLayout(orientation='vertical')
        title = title = Label(text=f"[color={GREEN}]View Past Scan[/color]", size=(0, TITLE_HEIGHT), size_hint=(1, None), font_size=TITLE_FONT_SIZE, underline=True, pos_hint={'center_x': .5, 'top': 1}, markup=True)
        everything.add_widget(title)
        everything.add_widget(Pages())
        everything.add_widget(ViewScreenInfo())

        self.add_widget(everything)


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
        if name == None: return self.currentScreen
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
            self.permission = win32api.MessageBox(0, 'Do you have legal permission to execute scans on this network?', 'Confirm permission', 0x00000004) == 6
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
        Config.set('input', 'mouse', 'mouse,multitouch_on_demand')  # disable multi-touch emulation
        MyApp().run()
    except Exception as e:
        traceback.print_exc()
        print(f"{type(e).__name__} at {__file__}:{e.__traceback__.tb_lineno}: {e}", file=sys.stderr)
    finally:
        is_kivy_running = False
        assert diagram is not None
        diagram.show()
        diagram.root.after(1, diagram.root.destroy)
        terminator.set()
        import threading
        print('\n'.join([str(thread) for thread in threading.enumerate()]))
        # sys.exit()


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
