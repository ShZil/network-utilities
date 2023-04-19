from globalstuff import *
from CacheDecorators import one_cache


class Hover:
    """Enables hovering cursor and behaviours. Uses singleton structure (because it accesses a system function of changing cursor).
    Includes two lists: `items`, where each item can change the cursor to `pointer` if hovered (`item.collide_point(x, y) -> True`);
    and `behaviors`, where each item is a `HoverBehavior`, and they do more exotic stuff, abstracted by `.show()` and `.hide()`.

    Raises:
        AttributeError: raised when `.add(item)` receives an `item` that has no method `.collide_point(int,int)`.
        TypeError: raised when `.add_behavior(behavior)` receives a `behavior` that is not of type `HoverBehavior`.
    """
    items = {}
    behaviors = {}
    current_screen = ""

    @staticmethod
    @one_cache
    def _bind():
        from kivy.core.window import Window
        from gui.AppState import State
        Window.bind(mouse_pos=Hover.update)
        Window.bind(size=State().resize_callback)
        return 0  # to comply with @one_cache's rule: A @one_cache function cannot return None!

    @staticmethod
    def add(instance):
        Hover._bind()
        if Hover.current_screen == "":
            raise KeyError("Hover cannot add without screen")
        try:
            instance.collide_point(0, 0)
        except AttributeError:
            raise AttributeError(
                "The instance passed to `Hover.add` doesn't support `.collide_point(int,int)`.")
        Hover.items[Hover.current_screen].append(instance)

    @staticmethod
    def add_behavior(behavior):
        Hover._bind()
        if Hover.current_screen == "":
            raise KeyError("Hover cannot add without screen")
        if not isinstance(behavior, HoverBehavior):
            raise TypeError(
                "The behavior passed to `Hover.add_behavior` isn't a `HoverBehavior`.")
        Hover.behaviors[Hover.current_screen].append(behavior)
        # A behaviour should support 3 methods: `collide_point(int,int)`,
        # `show()`, and `hide()`, and that's enforced by the HoverBehaviour
        # interface.

    def update(window, pos):
        if any([item.collide_point(*pos)
               for item in Hover.items[Hover.current_screen]]):
            window.set_system_cursor("hand")
        else:
            window.set_system_cursor("arrow")

        for behavior in Hover.behaviors[Hover.current_screen]:
            if behavior.collide_point(*pos):
                behavior.show()
            else:
                behavior.hide()

    def enter(screen: str):
        Hover.current_screen = screen
        if screen not in Hover.items:
            Hover.items[screen] = []
        if screen not in Hover.behaviors:
            Hover.behaviors[screen] = []

    @staticmethod
    def start():
        # Hide everything when the screen loads. Kinda misleading name -- this
        # function is called last in initalisation -- it marks the start of the
        # UI.
        for screen in Hover.behaviors.keys():
            for behavior in Hover.behaviors[screen]:
                behavior.hide()


class HoverBehavior:
    """
    Inherit from this class to create behaviours,
    and pass the instances to `Hover.add_behavior(...)`.
    """

    def show(self):
        raise NotImplementedError()

    def hide(self):
        raise NotImplementedError()

    def collide_point(self, x, y):
        raise NotImplementedError()


class HoverReplace(HoverBehavior):
    """A `HoverBehavior` that replaces the text shown on a label.
    When hovered, it displays the string in `text`,
    otherwise, it displays the initial string.
    """

    def __init__(self, widget, text, font_size, font="Arial"):
        self.widget = widget
        self.text = text
        self.save = self.widget.text
        self.font_size = font_size
        self.save_font = self.widget.font_name
        self.font = font
        Hover.add_behavior(self)

    def show(self):
        self.widget.text = self.text
        self.widget.font_name = self.font
        self.widget.font_size = self.font_size * HOVER_REPLACE_FACTOR

    def hide(self):
        self.widget.text = self.save
        self.widget.font_name = self.save_font
        self.widget.font_size = self.font_size

    def collide_point(self, x, y):
        return self.widget.collide_point(x, y)


class HoverReplaceBackground(HoverReplace):
    """A `HoverBehavior` that replaces the text shown on a label.
    When hovered, it displays the string in `text` (AND a different background colour),
    otherwise, it displays the initial string.
    """

    def __init__(self, widget, text, font_size, new_bg, font="Arial"):
        super().__init__(widget, text, font_size, font)
        self.save_bg = self.widget.background_color
        self.bg = new_bg

    def show(self):
        super().show()
        self.widget.background_color = self.bg

    def hide(self):
        super().hide()
        self.widget.background_color = self.save_bg


if __name__ == '__main__':
    print("This module creates the Hovering mechanism for the kivy gui.")
