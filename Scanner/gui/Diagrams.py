from import_handler import ImportDefence
with ImportDefence():
    import networkx as nx
    import tkinter as tk
    from kivy.graphics import Color, Ellipse, Rectangle, Line
    from kivy.clock import Clock
    from matplotlib import pyplot as plt

from globalstuff import *
from util import color_to_hex, hex_to_rgb01
from CacheDecorators import one_cache
from NetworkStorage import SpecialInformation

from abc import ABC, abstractmethod
from typing import ContextManager


class Diagrams:
    """This class handles all the Diagrams that present the network graph (`G`).
    To use, simply create an instance (uses Singleton), and do `.add` to your diagram.
    """
    _instance = None

    def __new__(cls):
        """Override the __new__ method to create only one instance of the class -- Singleton pattern."""
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.diagrams = []
        return cls._instance

    def add(self, diagram):
        if isinstance(diagram, Diagram) \
                and isinstance(diagram, ContextManager):
            self.diagrams.append(diagram)

    def update(self):
        for diagram in self.diagrams:
            diagram.update()


class Diagram(ABC):
    """This is an abstarct base class for diagrams that render the network.
    """
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def color(self, r, g, b):
        pass

    @abstractmethod
    def rectangle(self, x, y, w, h):
        pass

    @abstractmethod
    def circle(self, x, y, node):
        pass

    @abstractmethod
    def line(self, x0, y0, x1, y1, stroke):
        pass

    @abstractmethod
    def __contains__(self, pos):
        pass


class TKDiagram(Diagram, ContextManager):
    """A diagram under `tkinter` window.
    Uses tk.Canvas.
    Doesn't actually close until `is_kivy_running` is set to False, and another closing is attempted.
    Uses the Singleton pattern.

    Extends:
        Diagram (abstract class): allows for this class to be used as a diagram.
        ContextManager (type): allows for this class to be used as a context manager (for rendering).
    """
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.root = tk.Tk()
            cls._instance.root.title("Network Diagram")
            cls._instance.width, cls._instance.height = DIAGRAM_DIMENSIONS

            cls._instance.canvas = tk.Canvas(
                cls._instance.root,
                bg=color_to_hex(bg_color),
                height=cls._instance.height,
                width=cls._instance.width,
                borderwidth=0,
                highlightthickness=0
            )
            cls._instance.canvas.pack(expand=True, fill='both')

            cls._instance.radius = DIAGRAM_POINT_RADIUS
            cls._instance.color_cache = '#000000'

            cls._instance.canvas.bind('<Configure>', cls._instance.resize)
            cls._instance.update()

            cls._instance.hide()
            cls._instance.root.protocol("WM_DELETE_WINDOW", cls._instance.try_close)
        return cls._instance

    def __init__(self):
        pass

    def __exit__(self, exception_type, exception_value, exception_traceback):
        pass

    def color(self, r, g, b):
        self.color_cache = color_to_hex((r, g, b))

    def rectangle(self, x, y, w, h):
        self.canvas.create_rectangle(x, y, w, h, fill=self.color_cache)

    def circle(self, x, y, node):
        from NetworkStorage import here, router, SpecialInformation
        try:
            opacity = SpecialInformation()[node, 'opacity']
        except KeyError:
            opacity = 1
        if node is here or node is router:
            opacity = 1
        r = self.radius
        x0 = x - r
        y0 = y - r
        x1 = x + r
        y1 = y + r
        self.canvas.create_text(
            x0,
            y0 - 30,
            text=node.to_string('\n'),
            fill=self.color_cache,
            font=("Consolas", 10),
            justify=tk.CENTER
        )
        transparent = tuple(c * opacity for c in hex_to_rgb01(self.color_cache))
        self.canvas.create_oval(x0, y0, x1, y1, fill=color_to_hex(transparent))
        self.canvas.create_oval(x0, y0, x1, y1, outline=self.color_cache)

    def line(self, x0, y0, x1, y1, stroke):
        self.canvas.create_line(
            x0, y0, x1, y1, width=stroke, fill=self.color_cache)

    def __contains__(self, pos):
        return True

    # Window management -- closing, hiding, showing, resizing.
    def try_close(self):
        """To prevent the user from really closing this window if the source (kivy) is still open."""
        from globalstuff import is_kivy_running
        if is_kivy_running:
            self.hide()
        else:
            self.root.destroy()

    def hide(self):
        self.root.withdraw()

    def show(self):
        self.root.update()
        self.root.deiconify()

    def resize(self, event):
        # `geomery` is of the form "{width}x{height}+{x}+{y}"
        geometry = self.root.geometry().replace('+', 'x')
        self.width, self.height, *_ = map(int, geometry.split('x'))
        self.update()

    def update(self):
        try:
            self.root.after(0, lambda *_: render_diagram(self, 0, 0, self.width, self.height, bg_color, fg_color, -50))
        except RuntimeError:
            pass  # raised when terminating because tkinter cannot find its main thread.


class PlotDiagram(Diagram, ContextManager):
    """A diagram in a `matplotlib.pyplot` window.
    Uses the Singleton pattern.

    Extends:
        Diagram (abstract class): allows for this class to be used as a diagram.
        ContextManager (type): allows for this class to be used as a context manager (for rendering).
    """

    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            fig, ax = plt.subplots()
            cls._instance.fig = fig
            cls._instance.ax = ax
            cls._instance.manager = plt.get_current_fig_manager()
            fig.canvas.mpl_connect('close_event', cls._instance.hide)
        return cls._instance

    def __init__(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, exception_traceback):
        pass

    def color(self, r, g, b):
        pass

    def rectangle(self, x, y, w, h):
        pass

    def circle(self, x, y, node):
        pass

    def line(self, x0, y0, x1, y1, stroke):
        pass

    def __contains__(self, pos):
        return True

    def update(self):
        self.ax.clear()
        H = G.copy()
        pos = nx.kamada_kawai_layout(H)
        nx.draw(H, pos, ax=self.ax)
        
        plt.draw()

    def show(self):
        self.manager.window.show()
    
    def hide(self):
        self.manager.window.hide()


class KivyDiagram(Diagram, ContextManager):
    """A diagram under `kivy` window, specifically the `Scan` screen, more specifically the `ScanScreenMiddleDiagram` widget.
    Uses kivy's widget.canvas.
    Linked to a kivy widget with `self.widget` and `.set_widget(widget)`.
    There has to be a widget set before rendering (entering the context manager)!
    You cannot change the widget once you set it.
    Uses the Singleton pattern.

    Extends:
        Diagram (abstract class): allows for this class to be used as a diagram.
        ContextManager (type): allows for this class to be used as a context manager (for rendering).
    """

    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.widget = None
            cls._instance.radius = DIAGRAM_POINT_RADIUS
        return cls._instance

    def __init__(self):
        pass

    @one_cache
    def set_widget(self, widget):
        self.widget = widget
        return widget

    def __enter__(self):
        assert self.widget is not None
        self.widget.canvas.__enter__()
        return self

    def __exit__(self, exception_type, exception_value, exception_traceback):
        assert self.widget is not None
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
        assert self.widget is not None
        x, y = pos
        r = self.radius
        collides = lambda x0, y0: self.widget.collide_point(x0, y0)
        if r == 0:
            return collides(x, y)
        return collides(x + r, y + r) and collides(x - r, y - r)

    def update(self, *_):
        assert self.widget is not None
        Clock.schedule_once(lambda *_: render_diagram(
            self,
            *self.widget.pos,
            *self.widget.size,
            bg_color,
            fg_color,
            -TITLE_HEIGHT
        )
        )


def render_diagram(draw, x, y, w, h, bg, fg, dh=0):
    """An abstract representation of the algorithm used to render the diagram.
    To interface with ~~reality~~ the screen, it uses the `draw` argument,
    which is a context manager supporting various methods.
    Currently, there are two implementations: `KivyDiagram` and `TKDiagram`.
    """
    from NetworkStorage import here, router
    scale = min(w, h + dh) * DIAGRAM_SCALE
    stroke = 1
    H = G.copy()

    pos = nx.kamada_kawai_layout(H, center=(x + w / 2, y + h / 2), scale=scale)

    discovered = SpecialInformation()['discovery']
    highlights = set()
    for node in pos.keys():
        for entity in discovered:
            if node.equals(entity):
                highlights.add(node)
                discovered.remove(entity)
                break
        if len(discovered) == 0:
            break

    with draw:
        draw.color(*bg)
        draw.rectangle(x, y, w, h)

        draw.color(*fg)
        for edge in H.edges:
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            if (x0, y0) in draw and (x1, y1) in draw:
                draw.line(x0, y0, x1, y1, stroke)

        for node, (x0, y0) in pos.items():
            if (x0, y0) in draw:
                draw.color(*fg)
                if node in highlights:
                    draw.color(*fg_highlight)
                if node is router:
                    draw.color(*router_highlight)
                if node is here:
                    draw.color(*here_highlight)
                draw.circle(x0, y0, node)



if __name__ == '__main__':
    print("This file handles Diagrams that present the network graph.")
    print("Currently two types: KivyDiagram and TKDiagram.")
    print("To create a new diagram, simply inherit Diagram and typing.ContextManager,")
    print("and implement all the methods.")
