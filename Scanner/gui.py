import kivy
kivy.require('2.1.0')

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, Ellipse

__author__ = 'Shaked Dan Zilberman'


def callback(instance):
    print("Hello")
    print(instance)


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
        everything.add_widget(Label(text="Local Network Scanner", size=(0, 70), size_hint=(1, None), font_size=30))
        layout = GridLayout(cols=3)

        left_menu = ButtonColumn(width=150)
        btn = Button(text='print out', font_size=14)
        btn.bind(on_press=callback)
        left_menu.add(btn)
        for i in range(5):
            left_menu.add(Button(text='btn' + str(i), font_size=14))
        layout.add_widget(left_menu)

        layout.add_widget(Label(text='hi'))

        right_menu = ButtonColumn(width=300)
        for i in range(7):
            right_menu.add(Button(text='scan' + str(i), font_size=14))
        layout.add_widget(right_menu)
        everything.add_widget(layout)
        return everything


if __name__ == '__main__':
    MyApp().run()
