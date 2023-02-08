from kivy.core.window import Window
from util import one_cache


class Hover:
    """Enables hovering cursor and behaviours. Uses singleton structure (because it accesses a system function of changing cursor).
    Includes two lists: `items`, where each item can change the cursor to `pointer` if hovered (`item.collide_point(x, y) -> True`);
    and `behaviors`, where each item is a `HoverBehavior`, and they do more exotic stuff, abstracted by `.show()` and `.hide()`.

    Raises:
        AttributeError: raised when `.add(item)` receives an `item` that has no method `.collide_point(int,int)`.
        TypeError: raised when `.add_behavior(behavior)` receives a `behavior` that is not of type `HoverBehavior`.
    """
    print("Hover")
    items = []
    behaviors = []


    @staticmethod
    @one_cache
    def _bind():
        Window.bind(mouse_pos=Hover.update)

    
    @staticmethod
    def add(instance):
        Hover._bind()
        try:
            instance.collide_point(0, 0)
        except AttributeError:
            raise AttributeError("The instance passed to `Hover.add` doesn't support `.collide_point(int,int)`.")
        Hover.items.append(instance)
        print("Hover", instance)


    @staticmethod
    def add_behavior(behavior):
        Hover._bind()
        if not isinstance(behavior, HoverBehavior):
            raise TypeError("The behavior passed to `Hover.add_behavior` isn't a `HoverBehavior`.")
        Hover.behaviors.append(behavior)
        print("Hover behave", behavior)
        # A behaviour should support 3 methods: `collide_point(int,int)`, `show()`, and `hide()`.
    

    def update(window, pos):
        if any([item.collide_point(*pos) for item in Hover.items]):
            window.set_system_cursor("hand")
        else:
            window.set_system_cursor("arrow")

        for behavior in Hover.behaviors:
            if behavior.collide_point(*pos):
                behavior.show()
            else:
                behavior.hide()
    

    @staticmethod
    def hide_all():
        # Hide everything when the screen loads.
        for behavior in Hover.behaviors:
            behavior.hide()


class HoverBehavior:
    """
    Inherit from this class to create behaviours,
    and pass the instances to `Hover.add_behavior(...)`.
    """
    print("HoverBehavior")
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
    print("HoverReplace")
    FACTOR = 0.75  # new_text_size = FACTOR * old_text_size

    def __init__(self, widget, text, font_size):
        self.widget = widget
        self.text = text
        self.save = self.widget.text
        self.font_size = font_size
        Hover.add_behavior(self)
    

    def show(self):
        self.widget.text = self.text
        self.widget.font_size = self.font_size * HoverReplace.FACTOR
    

    def hide(self):
        self.widget.text = self.save
        self.widget.font_size = self.font_size


    def collide_point(self, x, y):
        return self.widget.collide_point(x, y)

