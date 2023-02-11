import sys
from import_handler import ImportDefence
with ImportDefence():
    import kivy
    import networkx as nx
    import tkinter as tk
    from threading import Thread
    import numpy, scipy  # for networkx
kivy.require('2.1.0')

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.bubble import Bubble
from kivy.graphics import Color, Ellipse, Rectangle, Line
from kivy.core.text import LabelBase
from kivy.utils import escape_markup

from util import nameof, one_cache


__author__ = 'Shaked Dan Zilberman'

hyperness = 1
G = nx.hypercube_graph(1)
diagram = None
is_kivy_running = True
bg_color = (0, 0, .01)
fg_color = (0.023, 0.92, 0.125)



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
        self.width = 300
        self.height = 300

        self.canvas = tk.Canvas(self.root, bg="white", height=self.height, width=self.width)
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
        if not nx.utils.graphs_equal(G, self.graph):
            self.graph = G.copy()
            self.update()


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
            self.diagram_cache = TKDiagram(self, 5)
        background = (0, 0, 0)
        foreground = (0, 255, 0)
        render_diagram(self.diagram_cache, 0, 0, self.width, self.height, background, foreground)
        self.changed = False


def callback1(x):
    print('Hello1')


def callback2(x):
    print('Hello2')


def activate(x):
    print("Play!")


def temp_increase_graph_degree(x):
    """Adds one dimension to the hypercube graph. Temporary -- until real info is fed into this."""
    global hyperness, G
    hyperness += 1
    if hyperness > 6: hyperness = 6
    G = nx.hypercube_graph(hyperness)
    update_kivy_diagram(0, 0)
    if diagram is not None: diagram.renew(G)


class MyPaintWidget(Widget):
    """Responsible for the middle diagram (object #9).
    Args:
        Widget (tkinter widget): the superclass.
    """
    def init(self):
        update_kivy_diagram(self, 0)

    def on_touch_down(self, touch):
        update_kivy_diagram(self, 0)


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
        x = lambda h: hex(h)[2:4].zfill(2)
        self.color_cache = f'#{x(r)}{x(g)}{x(b)}'


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


def update_kivy_diagram(painter, _):
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
        update_kivy_diagram.diagram_cache = KivyDiagram(painter, 5)
    
    render_diagram(update_kivy_diagram.diagram_cache, *painter.pos, *painter.size, bg_color, fg_color, -70)


def render_diagram(draw, x, y, w, h, bg, fg, dh=0):
    """An abstract representation of the algorithm used to render the diagram.
    To interface with ~reality~ the screen, it uses the `draw` argument,
    which is a context manager supporting various methods.
    Currently, there are two implementations: `KivyDiagram` and `TKDiagram`.
    """
    scale = min(w, h + dh) / 2.3
    stroke = 1

    pos = nx.kamada_kawai_layout(G, center=(x + w/2, y + h/2), scale=scale)
    
    with draw:
        draw.color(*bg)
        draw.rectangle(x, y, w, h)
        draw.color(*fg)
        
        for node in G:
            x0, y0 = pos[node]
            if (x0, y0) in draw:
                draw.circle(x0, y0)
        
        for edge in G.edges:
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            if (x0, y0) in draw and (x1, y1) in draw:
                draw.line(x0, y0, x1, y1, stroke)


class ButtonColumn(GridLayout):
    """Organises buttons in a column
    Args:
        GridLayout (tk): the superclass.
    """
    def __init__(self, width: int):
        super().__init__(cols=1, width=width, size_hint=(None, 1), spacing=[-3], padding=[-1, -3, -1, -3])
        self.buttons = []  # list of tuples `(button, callback)`
        self.background_color = [0.1, 1, 0.3, 1]  # rgba values, range 0 to 1, in 4-item list
        self.font_size = 24
    

    def add(self, text: str, callback=None):
        btn = Button(text=text, font_size=self.font_size, background_color=self.background_color, font_name="Roboto")
        if callback is not None:
            btn.bind(on_press=callback)
        super().add_widget(btn)
        Hover.add(btn)
        self.buttons.append((btn, callback))
    

    def log_all(self):
        print(self.buttons)
        for button, action in self.buttons:
            print(nameof(action))


class Hover:
    """Enables hovering cursor and behaviours. Uses singleton structure (because it accesses a system function of changing cursor).
    Includes two lists: `items`, where each item can change the cursor to `pointer` if hovered (`item.collide_point(x, y) -> True`);
    and `behaviors`, where each item is a `HoverBehavior`, and they do more exotic stuff, abstracted by `.show()` and `.hide()`.
    Raises:
        AttributeError: raised when `.add(item)` receives an `item` that has no method `.collide_point(int,int)`.
        TypeError: raised when `.add_behavior(behavior)` receives a `behavior` that is not of type `HoverBehavior`.
    """
    items = []
    behaviors = []


    @staticmethod
    @one_cache
    def _bind():
        from kivy.core.window import Window
        Window.bind(mouse_pos=Hover.update)

    
    @staticmethod
    def add(instance):
        Hover._bind()
        try:
            instance.collide_point(0, 0)
        except AttributeError:
            raise AttributeError("The instance passed to `Hover.add` doesn't support `.collide_point(int,int)`.")
        Hover.items.append(instance)


    @staticmethod
    def add_behavior(behavior):
        Hover._bind()
        if not isinstance(behavior, HoverBehavior):
            raise TypeError("The behavior passed to `Hover.add_behavior` isn't a `HoverBehavior`.")
        Hover.behaviors.append(behavior)
        # A behaviour should support 3 methods: `collide_point(int,int)`, `show()`, and `hide()`.
    

    def update(window, pos):
        if any([item.collide_point(*pos) for item in Hover.items]):
            window.set_system_cursor("hand")
        else:
            window.set_system_cursor("arrow")

        for behavior in Hover.behaviors:
            if behavior.collide_point(*pos):
                behavior.show()
            else:
                behavior.hide()
    

    @staticmethod
    def start():
        # Hide everything when the screen loads. Misleading name -- this function is called last in initalisation -- it marks the start of the UI.
        for behavior in Hover.behaviors:
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
    FACTOR = 0.75  # new_text_size = FACTOR * old_text_size

    def __init__(self, widget, text, font_size):
        self.widget = widget
        self.text = text
        self.save = self.widget.text
        self.font_size = font_size
        Hover.add_behavior(self)
    

    def show(self):
        self.widget.text = self.text
        self.widget.font_size = self.font_size * HoverReplace.FACTOR
    

    def hide(self):
        self.widget.text = self.save
        self.widget.font_size = self.font_size


    def collide_point(self, x, y):
        return self.widget.collide_point(x, y)



class BlackButton(Button):
    """A button that has black background, and also adds itself to `Hover`."""
    def __init__(self, text, **kwargs):
        super().__init__(text='[color=000000]' + escape_markup(text) + '[/color]', markup=True, **kwargs)
        Hover.add(self)


class GreenButton(Button):
    """A button that has green background, and also adds itself to `Hover`."""
    def __init__(self, text, **kwargs):
        super().__init__(text='[color=00ff00]' + escape_markup(text) + '[/color]', markup=True, **kwargs)
        Hover.add(self)



class MyApp(App):
    """The main application, using `kivy`.
    Builds an interface that looks like this:
    
    ```md
    The Window (Unicode Box Art):
        ┌────────────────────────────────────────────╥───────────────────────────┐
        │                  [#1 Title]                ║   [#2 Conf]   [#3 Info]   │
        │  #4 Save.                                  ╟───────────────────────────┤
        │  #5 Scan.                                  ║        [#7 ScanA]         │
        │  #6 Know.                                  ║        [#8 ScanB]         │
        │           #9 D                             ║        [#10 ScanC]        │
        │                I                           ║        [#11 ScanD]        │
        │                  A                         ║        [#12 ScanE]        │
        │                    G                       ║        [#13 ScanF]        │
        │                      R                     ║        [#14 ScanG]        │
        │                        A                   ║                           │
        │                          M                 ║                           │
        │    [#15 Play]            [#16 Fullscreen]  ║                           │
        └────────────────────────────────────────────╨───────────────────────────┘
    ```
    Args:
        App (tk): the tkinter base app.
    """


    def build(self):
        self.title = 'Local Network Scanner'
        everything = BoxLayout(orientation='horizontal')

        # Create the middle diagram
        layout = RelativeLayout()


        # Page frippery (top left corner) -- Objects #4, #5, #6
        pages = BoxLayout(orientation='vertical', size_hint=(.15, .15), pos_hint={'x': 0, 'top': 1})
        for label, action in zip(['Save.', 'Scan.', 'Know.'], [lambda _: print("Save"), lambda _: print("Scan"), lambda _: print("Know")]):
            change_page = GreenButton(text=label, font_size=20, background_color=[0, 0, 0, 0], font_name="Arial")
            change_page.bind(on_press=action)
            pages.add_widget(change_page)

        # Object #15
        play_button = GreenButton(text='▶', font_size=30, background_color=[0, 0, 0, 0], size_hint=(.1, .1), pos_hint={'x': 0, 'y': 0}, font_name="Symbols")
        play_button.bind(on_press=activate)

        # Object #16    # Previous icon: ⛶
        open_diagram = GreenButton(text='🔍', font_size=30, background_color=[0, 0, 0, 0], size_hint=(.1, .1), pos_hint={'right': 1, 'y': 0}, font_name="Symbols")
        open_diagram.bind(on_press=lambda _: diagram.show())

        # Object #9
        paint = MyPaintWidget(size_hint=(1, 1), pos_hint={'center_x': .5, 'center_y': .5})
        paint.bind(pos=update_kivy_diagram, size=update_kivy_diagram)
        
        # Object 1
        title = Label(text="[color=00ff00]Local Network Scanner[/color]", size=(0, 70), size_hint=(1, None), font_size=30, underline=True, pos_hint={'center_x': .5, 'top': 1}, markup=True)

        layout.add_widget(paint)
        layout.add_widget(pages)
        layout.add_widget(open_diagram)
        layout.add_widget(play_button)
        layout.add_widget(title)



        # Create the right column
        right_menu = ButtonColumn(width=300)

        # 2 operations on each scan
        operations = BoxLayout(orientation='horizontal', spacing=-3)
        # Object #2
        configure = Button(text='⚙', background_color=[0.8, 0.8, 0.8, 1], font_name="Symbols")  # Perhaps use this font instead for this button: https://www.fontspace.com/bainsley-font-f59538
        # Object #3
        info = Button(text='ℹ', background_color=[0.8, 0.8, 0.8, 1], font_name="Symbols")  # Consider a '?' instead
        operations.add_widget(configure)
        Hover.add(configure)
        operations.add_widget(info)
        Hover.add(info)
        right_menu.add_widget(operations)

        # Objects #7 - #14
        for i in range(10):
            right_menu.add(f"scan {i}", callback1 if i < 4 else callback2)
        right_menu.add(f'woo!', temp_increase_graph_degree)

        # Add all widgets to `everything`
        HoverReplace(configure, "Configure", 30)
        HoverReplace(info, "Information", 30)
        everything.add_widget(layout)
        everything.add_widget(right_menu)

        Hover.start()

        return everything


def start_kivy():
    """Starts the `kivy` app, and handles the `tkinter` diagram's closing.
    """
    try:
        global is_kivy_running, diagram
        is_kivy_running = True
        MyApp().run()
        is_kivy_running = False
        
        diagram.show()
        diagram.root.quit()
    finally:
        sys.exit()


def start_tk():
    """Starts the `tkinter` diagram in the background.
    This has to be on the main thread (because `tkinter` said so).
    """
    global diagram
    diagram = Diagram()
    diagram.root.mainloop()


def add_font():
    """Loads a font (`kivy`'s)."""
    LabelBase.register(name='Symbols', fn_regular='Segoe UI Symbol.ttf')


if __name__ == '__main__':
    add_font()
    runner = Thread(target=start_kivy)
    runner.start()
    start_tk()
