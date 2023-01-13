import kivy
kivy.require('2.1.0')

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, Ellipse, Rectangle, Line

import networkx as nx

__author__ = 'Shaked Dan Zilberman'

hyperness = 1
G = nx.hypercube_graph(1)


def callback0(x):
    print("Hello")


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
        everything = BoxLayout(orientation='vertical')

        # Create the left column
        left_menu = ButtonColumn(width=150)
        left_menu.add('print out', callback0)
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
    MyApp().run()
