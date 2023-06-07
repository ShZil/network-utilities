import math
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
        """The add function adds a diagram to the list of diagrams."""
        if isinstance(diagram, Diagram) \
                and isinstance(diagram, ContextManager):
            self.diagrams.append(diagram)

    def update(self):
        """The update function is called by the main loop to update all of the diagrams.
        It iterates through each diagram in self.diagrams and calls its update function.
        """
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
        """
        The update function is called every time the size changes.
        """
        pass

    @abstractmethod
    def color(self, r, g, b):
        """
        The color function takes three arguments, r, g and b. (Using RGB01)
        The function sets the color of the drawer to the RGB value.
        """
        pass

    @abstractmethod
    def rectangle(self, x, y, w, h):
        """
        The rectangle function draws a rectangle with the upper left corner at (x, y) and the lower right corner at (x + w, y + h) onto the diagram.
        """
        pass

    @abstractmethod
    def circle(self, x, y, node):
        """
        The circle function takes in the x and y coordinates of a node, as well as the node itself (NetworkEntity).
        It then draws a circle on the diagram at those coordinates with a specific radius.
        """
        pass

    @abstractmethod
    def line(self, x0, y0, x1, y1, stroke):
        """
        The line function draws a line from (x0, y0) to (x1, y1) on the diagram.
        The stroke parameter is the width of the line.
        """
        pass

    @abstractmethod
    def __contains__(self, pos):
        """This allows to use the syntax `if (x0, y0) in draw:`.
        It determines whether a point is contained within the boundary box of the diagram.

        Args:
            pos (tuple[int, int]): the point.
        """
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
        """
        The color function takes in three parameters, r, g and b.
        The function then converts the rgb values to hexadecimal format and stores it in a variable called color_cache.
        """
        self.color_cache = color_to_hex((r, g, b))

    def rectangle(self, x, y, w, h):
        """
        The rectangle function draws a rectangle on the canvas.
        The function takes in four arguments: x, y, w and h.
        The first two arguments are the coordinates of the top left corner of 
        where you want to start drawing your rectangle from.
        The last two arguments are width and height respectively.
        """
        self.canvas.create_rectangle(x, y, w, h, fill=self.color_cache)

    def circle(self, x, y, node):
        """
        The circle function draws a circle on the canvas (both fill and outline).
        It retreives the opacity level of the entity (node) from `SpecialStorage`
        (only the fill is affected by the opacity).
        It also renders the textual description of the entity above the circle.
        """
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
        """
        The line function draws a line from (x0, y0) to (x2, y2).
        The line is drawn using the current stroke color and width.
        """
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
        """
        The hide function hides the root window.
        This is useful for when you want to hide the main window, but still have it open in the background;
        which is any time the user clicks the X button on the TK window but not the Kivy window.
        """
        self.root.withdraw()

    def show(self):
        """
        The show function is used to display the GUI.
        It takes no arguments and returns nothing.
        It displays or refocuses the TK window.
        """
        self.root.update()
        self.root.deiconify()

    def resize(self, event):
        """
        The resize function is called when the window is resized.
        It updates the width and height of the diagram, which are used to draw
        the image on it. It also calls update() to redraw everything.
        """
        # `geomery` is of the form "{width}x{height}+{x}+{y}"
        geometry = self.root.geometry().replace('+', 'x')
        self.width, self.height, *_ = map(int, geometry.split('x'))
        self.update()

    def update(self):
        """
        The update function is called by the mainloop of tkinter.
        It calls render_diagram, which renders the diagram to the canvas window.
        """
        try:
            self.root.after(0, lambda *_: render_diagram(self, 0, 0, self.width, self.height, bg_color, fg_color, -50))
        except RuntimeError:
            pass  # raised when terminating because tkinter cannot find its main thread.


"""
class PlotDiagram(Diagram, ContextManager):
    \"\"\"A diagram in a `matplotlib.pyplot` window.
    Uses the Singleton pattern.

    Extends:
        Diagram (abstract class): allows for this class to be used as a diagram.
        ContextManager (type): allows for this class to be used as a context manager (for rendering).
    \"\"\"

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
"""


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
        """
        Binds a widget to the diagram.
        This is one-time only (on each run of the programme).
        """
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
        """
        The color function takes three arguments, r, g and b.
        The function then sets the color of the drawer ("brush") to a 
        shade of red, green and blue that is scaled to be between 0 and 1.
        Using RGB01.
        """
        Color(r, g, b)

    def rectangle(self, x, y, w, h):
        """The rectangle function draws a rectangle on the diagram."""
        Rectangle(pos=(x, y), size=(w, h))

    def circle(self, x, y, node):
        """The circle function draws a circle centered at the given x and y coordinates, with self.radius."""
        r = self.radius
        Ellipse(pos=(x - r, y - r), size=(2 * r, 2 * r))

    def line(self, x0, y0, x1, y1, stroke):
        """
        The line function takes in four arguments, x0 and y0 are the starting coordinates of the line,
        x1 and y1 are the ending coordinates of the line. The stroke argument is used to determine how thick
        the line will be drawn on the diagram.
        """
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
        """
        The update function is called whenever the widget's size or position changes.
        It schedules a call to render_diagram, which will draw the diagram on the widget.
        The diagram is drawn in a separate thread so that it doesn't block and gets timed correctly.
        """
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
    from NetworkStorage import here, router, PublicAddressNetworkEntity
    scale = min(w, h + dh) * DIAGRAM_SCALE
    stroke = 1
    H = G.copy()

    pos = nx.kamada_kawai_layout(H, center=(x + w / 2, y + h / 2), scale=scale)
    from globalstuff import diagram_tilt
    theta = diagram_tilt[0]  # angle to rotate by
    ox, oy = x + w / 2, y + h / 2  # centre point
    sin, cos = math.sin, math.cos  # trig functions
    for node, position in pos.items():
        px, py = position
        new_x = cos(theta) * (px-ox) - sin(theta) * (py-oy) + ox
        new_y = sin(theta) * (px-ox) + cos(theta) * (py-oy) + oy
        pos[node] = (new_x, new_y)

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
                if node is router or isinstance(node, PublicAddressNetworkEntity):
                    draw.color(*router_highlight)
                if node is here:
                    draw.color(*here_highlight)
                draw.circle(x0, y0, node)



if __name__ == '__main__':
    print("This file handles Diagrams that present the network graph.")
    print("Currently two types: KivyDiagram and TKDiagram.")
    print("To create a new diagram, simply inherit Diagram and typing.ContextManager,")
    print("and implement all the methods.")
