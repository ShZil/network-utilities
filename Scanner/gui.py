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

from util import nameof


__author__ = 'Shaked Dan Zilberman'

hyperness = 1
G = nx.hypercube_graph(1)
diagram = None
is_kivy_running = True


class Diagram:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Network Diagram")
        self.width = 300
        self.height = 300

        self.canvas = tk.Canvas(self.root, bg="white", height=self.height, width=self.width)
        self.canvas.pack(expand=True, fill='both')

        self.graph = G

        self.canvas.bind('<Configure>', self.resize)
        self.update()

        self.hide()
        self.root.protocol("WM_DELETE_WINDOW", self.try_close)
    


    def try_close(self):
        if is_kivy_running:
            self.hide()
        else:
            self.root.destroy()

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
        geometry = self.root.geometry().replace('+', 'x')
        # Uses this property of the `map` function: "Stops when the shortest iterable is exhausted."
        self.width, self.height = map(int, geometry.split('x'), [10, 10])  # Convert to `int` with base 10, but only twice.
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
        Hover.add(btn)
        self.buttons.append((btn, callback))
    

    def log_all(self):
        print(self.buttons)
        for button, action in self.buttons:
            print(nameof(action))


class Hover:
    items = []
    bubbles = []

    @staticmethod
    def add(instance):
        try:
            instance.collide_point(0, 0)
        except AttributeError:
            raise AttributeError("The instance passed to `Hover.add` doesn't support `.collide_point(int,int)`.")
        if len(Hover.items) == 0:
            from kivy.core.window import Window
            Window.bind(mouse_pos=Hover.update)
        Hover.items.append(instance)
    

    @staticmethod
    def add_bubble(bubble):
        try:
            bubble.widget.collide_point(0, 0)
        except AttributeError:
            raise AttributeError("The bubble passed to `Hover.add_bubble` doesn't support `.widget.collide_point(int,int)`.")
        Hover.bubbles.append(bubble)
    

    def update(window, pos):
        import os
        os.system('cls')
        for item in Hover.items: 
            print([*item.pos, item.width, item.height], "<------" if item.collide_point(*pos) else "")
        if any([item.collide_point(*pos) for item in Hover.items]):
            window.set_system_cursor("hand")
        else:
            window.set_system_cursor("arrow")
        print()
        for bubble in Hover.bubbles:
            if bubble.widget.collide_point(*pos):
                bubble.show()
                print([*bubble.widget.pos, bubble.widget.width, bubble.widget.height])
            else:
                bubble.hide()


class HoverReplace:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.save = self.widget.text
        Hover.add_behavior(self)
    

    def show(self):
        self.widget.text = self.text
    

    def hide(self):
        self.widget.text = self.save


    def collide_point(self, x, y):
        return self.widget.collide_point(x, y)



class BlackButton(Button):
    def __init__(self, text, **kwargs):
        super().__init__(text='[color=000000]' + escape_markup(text) + '[/color]', markup=True, **kwargs)
        Hover.add(self)


class MyApp(App):
    def build(self):
        self.title = 'Local Network Scanner'
        everything = BoxLayout(orientation='horizontal')

        # Create the middle diagram
        layout = RelativeLayout()


        # Page frippery (top left corner) -- Objects #4, #5, #6
        pages = BoxLayout(orientation='vertical', size_hint=(.15, .15), pos_hint={'x': 0, 'top': 1})
        for label, action in zip(['Save.', 'Scan.', 'Know.'], [lambda _: print("Save"), lambda _: print("Scan"), lambda _: print("Know")]):
            change_page = BlackButton(text=label, font_size=20, background_color=[0, 0, 0, 0], font_name="Arial")
            change_page.bind(on_press=action)
            pages.add_widget(change_page)

        # Object #15
        play_button = BlackButton(text='▶', font_size=30, background_color=[0, 0, 0, 0], size_hint=(.1, .1), pos_hint={'x': 0, 'y': 0}, font_name="Symbols")
        play_button.bind(on_press=callback2)

        # Object #16
        open_diagram = BlackButton(text='⛶', font_size=30, background_color=[0, 0, 0, 0], size_hint=(.1, .1), pos_hint={'right': 1, 'y': 0}, font_name="Symbols")
        open_diagram.bind(on_press=callback0)

        # Object #9
        paint = MyPaintWidget(size_hint=(1, 1), pos_hint={'center_x': .5, 'center_y': .5})
        paint.bind(pos=update_rect, size=update_rect)
        
        # Object 1
        title = Label(text="[color=000000]Local Network Scanner[/color]", size=(0, 70), size_hint=(1, None), font_size=30, underline=True, pos_hint={'center_x': .5, 'top': 1}, markup=True)

        layout.add_widget(paint)
        layout.add_widget(pages)
        layout.add_widget(open_diagram)
        layout.add_widget(play_button)
        layout.add_widget(title)



        # Create the right column
        right_menu = ButtonColumn(width=300)

        # 2 operations on each scan
        operations = BoxLayout(orientation='horizontal')
        # Object #2
        configure = Button(text='⚙', font_size=30, background_color=[0.8, 0.8, 0.8, 1], font_name="Symbols")  # Perhaps use this font instead for this button: https://www.fontspace.com/bainsley-font-f59538
        # Object #3
        info = Button(text='ℹ', font_size=30, background_color=[0.8, 0.8, 0.8, 1], font_name="Symbols")  # Consider a '?' instead
        operations.add_widget(configure)
        Hover.add(configure)
        operations.add_widget(info)
        Hover.add(info)
        right_menu.add_widget(operations)

        # Objects #7 - #14
        for i in range(10):
            right_menu.add(f"scan {i}", callback1 if i < 4 else callback2)
        right_menu.add(f'woo!', callback3)

        # Add all widgets to `everything`
        # AttachedBubble(configure, "Configure", 'top_mid')
        # AttachedBubble(info, "Information", 'top_mid')
        everything.add_widget(layout)
        everything.add_widget(right_menu)

        return everything


def start_kivy():
    global is_kivy_running, diagram
    is_kivy_running = True
    MyApp().run()
    is_kivy_running = False
    
    diagram.show()
    diagram.root.quit()
    sys.exit()


def start_tk():
    global diagram
    diagram = Diagram()
    diagram.root.mainloop()


def add_font():
    LabelBase.register(name='Symbols', fn_regular='Segoe UI Symbol.ttf')

if __name__ == '__main__':
    add_font()
    runner = Thread(target=start_kivy)
    runner.start()
    start_tk()


# The Window (Unicode Box Art):
# ┌────────────────────────────────────────────╥───────────────────────────┐
# │                  [#1 Title]                ║   [#2 Conf]   [#3 Info]   │
# │  #4 Save.                                  ╟───────────────────────────┤
# │  #5 Scan.                                  ║        [#7 ScanA]         │
# │  #6 Know.                                  ║        [#8 ScanB]         │
# │           #9 D                             ║        [#10 ScanC]        │
# │                I                           ║        [#11 ScanD]        │
# │                  A                         ║        [#12 ScanE]        │
# │                    G                       ║        [#13 ScanF]        │
# │                      R                     ║        [#14 ScanG]        │
# │                        A                   ║                           │
# │                          M                 ║                           │
# │    [#15 Play]            [#16 Fullscreen]  ║                           │
# └────────────────────────────────────────────╨───────────────────────────┘
