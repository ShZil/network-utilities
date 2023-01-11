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


def callback(instance):
    print("Hello")
    print(instance)


class MyPaintWidget(Widget):

    def on_touch_down(self, touch):
        update_rect(self, 0)


def update_rect(self, value):
    x, y = self.pos
    w, h = self.size
    G = nx.hypercube_graph(5)
    pos = nx.spiral_layout(G, center=(x + w/2, y + h/2), scale=80)
    print(pos.values())
    with self.canvas:
        Color(0, 1, 0)
        Rectangle(pos=self.pos, size=self.size)
        Color(0, 0, 0)
        
        for node in G:
            x0, y0 = pos[node]
            Ellipse(pos=(x0 - 5, y0 - 5), size=(10, 10))
        
        for edge in G.edges:
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            Line(points=(x0, y0, x1, y1), width=2)
    


class ButtonColumn(GridLayout):
    def __init__(self, width: int):
        super().__init__(cols=1, width=width, size_hint=(None, 1))
        self.buttons = []
    
    def add(self, btn: Button):
        super().add_widget(btn)
        self.buttons.append(btn)


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
