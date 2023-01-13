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
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, Ellipse, Rectangle, Line


__author__ = 'Shaked Dan Zilberman'

hyperness = 1
G = nx.hypercube_graph(1)
diagram = None


class Diagram:
    def __init__(self):
        print("Creating Diagram")
        self.root = tk.Tk()
        self.root.title("Network Diagram")

        self.canvas = tk.Canvas(self.root, bg="white", height=300, width=300)
        self.canvas.pack(expand=True, fill='both')

        self.width = 300
        self.height = 300

        self.graph = nx.empty_graph()

        self.canvas.bind('<Configure>', self.resize)
        self.update()

        self.hide()
        print("Created diagram")
    
    def renew(self, G: nx.Graph):
        if not nx.utils.graphs_equal(G, self.graph):
            self.graph = G.copy()
            self.update()

    def hide(self):
        self.root.withdraw()

    def show(self):
        self.root.update()
        self.root.deiconify()
    
    def resize(self, event):
        geometry = self.root.geometry()    
        self.width  = int(geometry[0:geometry.index("x")])
        self.height = int(geometry[geometry.index("x")+1:geometry.index("+")])
        self.update()

    def update(self):
        self.draw_graph(self.graph)
        self.changed = False
    
    def draw_graph(self, G: nx.Graph):
        w, h = self.width, self.height
        x, y = 0, 0
        scale = min(w, h) / 2.3
        r = 5
        stroke = 1
        pos = nx.kamada_kawai_layout(G, center=(x + w/2, y + h/2), scale=scale)

        self.canvas.create_rectangle(0, 0, w, h, fill='white')
            
        for node in G:
            x0, y0 = pos[node]
            self.create_circle(x0, y0, r)
            
        for edge in G.edges:
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            self.create_line(x0, y0, x1, y1, stroke)

    def create_circle(self, x, y, r):
        x0 = x - r
        y0 = y - r
        x1 = x + r
        y1 = y + r
        return self.canvas.create_oval(x0, y0, x1, y1, fill='black')
    
    def create_line(self, x0, y0, x1, y1, stroke):
        self.canvas.create_line(x0, y0, x1, y1, width=stroke)


def callback0(x):
    diagram.show()


def callback1(x):
    print('Hello1')


def callback2(x):
    print('Hello2')


def callback3(x):
    global hyperness, G
    hyperness += 1
    if hyperness > 6: hyperness = 6
    G = nx.hypercube_graph(hyperness)
    update_rect(0, 0)
    if diagram is not None: diagram.renew(G)


class MyPaintWidget(Widget):
    def init(self):
        update_rect(self, 0)

    def on_touch_down(self, touch):
        update_rect(self, 0)


def update_rect(painter, value):
    if hasattr(update_rect, 'cache'):
        painter = update_rect.cache
    else:
        update_rect.cache = painter
    
    x, y = painter.pos
    w, h = painter.size
    scale = min(w, h) / 2.3
    r = 5
    stroke = 1
    pos = nx.kamada_kawai_layout(G, center=(x + w/2, y + h/2), scale=scale)
    # print(pos.values())
    with painter.canvas:
        Color(0, 1, 0)
        Rectangle(pos=painter.pos, size=painter.size)
        Color(0, 0, 0)
        
        for node in G:
            x0, y0 = pos[node]
            if painter.collide_point(x0 - r, y0 - r) and painter.collide_point(x0 + r, y0 + r):
                Ellipse(pos=(x0 - r, y0 - r), size=(2 * r, 2 * r))
        
        for edge in G.edges:
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            if painter.collide_point(x0, y0) and painter.collide_point(x1, y1):
                Line(points=(x0, y0, x1, y1), width=stroke)


class ButtonColumn(GridLayout):
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
        self.buttons.append((btn, callback))


    def do_all(self):
        print(self.buttons)
        for button, action in self.buttons:
            action(None)


class MyApp(App):
    def build(self):
        self.title = 'Local Network Scanner'
        everything = BoxLayout(orientation='vertical')

        # Create the left column
        left_menu = ButtonColumn(width=150)
        left_menu.add('open diagram', callback0)
        for i in range(5):
            left_menu.add('btn' + str(i))

        # Create the middle diagram
        paint = MyPaintWidget()
        paint.bind(pos=update_rect, size=update_rect)

        # Create the right column
        right_menu = ButtonColumn(width=300)
        for i in range(7):
            right_menu.add(f"scan {i}", callback1 if i < 4 else callback2)
        right_menu.add(f'woo', callback3)

        # Add all widgets to `everything`
        title = Label(text="Local Network Scanner", size=(0, 70), size_hint=(1, None), font_size=30, underline=True)
        everything.add_widget(title)

        layout = GridLayout(cols=3)
        layout.add_widget(left_menu)
        layout.add_widget(paint)
        layout.add_widget(right_menu)
        everything.add_widget(layout)

        return everything


if __name__ == '__main__':
    runner = Thread(target=lambda: MyApp().run())
    runner.start()
    diagram = Diagram()
    diagram.root.mainloop()
    # MyApp().run()
