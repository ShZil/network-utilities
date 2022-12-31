import kivy
kivy.require('2.1.0')

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.graphics import Color, Ellipse

__author__ = 'Shaked Dan Zilberman'


class MyPaintWidget(Widget):
    def on_touch_down(self, touch):
        print(touch)
        with self.canvas:
            Color(0, 1, 0)
            d = 30.
            Ellipse(pos=(touch.x - d / 2, touch.y - d / 2), size=(d, d))


def callback(instance):
    print("Hello")
    print(instance)


class MyApp(App):
    def build(self):
        layout = GridLayout(cols=2, row_force_default=True, row_default_height=40)
        layout.add_widget(MyPaintWidget())
        btn = Button(text='print out', font_size=14)
        btn.bind(on_press=callback)
        layout.add_widget(btn)
        return layout


if __name__ == '__main__':
    MyApp().run()
