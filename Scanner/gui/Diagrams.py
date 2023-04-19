from import_handler import ImportDefence
with ImportDefence():
    import tkinter as tk
    import networkx as nx
    from kivy.graphics import Color, Ellipse, Rectangle, Line

from globalstuff import *
from util import color_to_hex

class Diagram:
    """This is a class responsible for the hovering diagram, that is created in a separate window when the 'Fullscreen' button is pressed.
    Uses `tkinter` (not `kivy`, like the other parts). Black diagram on white background. Can be expanded in both directions.
    """
    _instance = None

    def __new__(cls):
        """Override the __new__ method to create only one instance of the class -- Singleton pattern."""
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

            cls._instance.graph = G
            cls._instance.diagram_cache = None

            cls._instance.canvas.bind('<Configure>', cls._instance.resize)
            cls._instance.update()

            cls._instance.hide()
            cls._instance.root.protocol("WM_DELETE_WINDOW", cls._instance.try_close)
        return cls._instance

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


if __name__ == '__main__':
    print("This file handles the two kinds of diagrams: Kivy diagram and TKinter diagram.")
