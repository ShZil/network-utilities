import kivy
kivy.require('2.1.0')

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.graphics import Color, Ellipse

__author__ = 'Shaked Dan Zilberman'


def callback(instance):
    print("Hello")
    print(instance)


class ButtonColumn(GridLayout):
    def __init__(self, width: int):
        super().__init__(cols=1, width=width, size_hint=(None, 1))
        self.buttons = []
    
    def add_button(self, btn: Button):
        super().add_widget(btn)
        self.buttons.append(btn)


class MyApp(App):
    def build(self):
        layout = GridLayout(cols=3)

        left_menu = ButtonColumn(width=150)
        for i in range(5):
            left_menu.add_button(Button(text='btn' + str(i), font_size=14))
        layout.add_widget(left_menu)

        btn = Button(text='print out', font_size=54)
        btn.bind(on_press=callback)
        layout.add_widget(btn)

        right_menu = ButtonColumn(width=350)
        for i in range(7):
            right_menu.add_button(Button(text='scan' + str(i), font_size=14))
        layout.add_widget(right_menu)
        return layout


if __name__ == '__main__':
    MyApp().run()
