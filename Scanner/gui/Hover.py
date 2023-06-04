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
        """The add function adds an instance to the list of items that will be checked for hover events."""
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
        """
        The add_behavior function is used to add a HoverBehavior to the current screen.
        The behavior will be added to the list of behaviors for that screen, and it will
        be shown when the mouse hovers over it. The behavior should support 3 methods: 
        `collide_point(int,int)`, `show()`, and `hide()`. These are enforced by the 
        HoverBehavior interface.
        """
        Hover._bind()
        if Hover.current_screen == "":
            raise KeyError("Hover cannot add without screen")
        if not isinstance(behavior, HoverBehavior):
            raise TypeError(
                "The behavior passed to `Hover.add_behavior` isn't a `HoverBehavior`.")
        Hover.behaviors[Hover.current_screen].append(behavior)

    def update(window, pos):
        """
        It checks if any of the items on screen are being hovered over, and changes
        the cursor to a hand if so. It also calls show() or hide() for each behavior 
        object depending on whether it's being hovered over.
        """
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
        """
        The enter function is used to enter a screen, before adding behaviours and hoverable widgets to it.
        It takes in the name of the screen as an argument, and sets that as the current_screen.
        If there are no items or behaviors for that particular screen, it creates empty lists for them,
        waiting to populate them through the `add` and `add_behavior` methods..
        """
        
        Hover.current_screen = screen
        if screen not in Hover.items:
            Hover.items[screen] = []
        if screen not in Hover.behaviors:
            Hover.behaviors[screen] = []

    @staticmethod
    def start():
        """
        The start function is called last in the initialization process.
        Calls `hide` on all the behaviours in all the screens.
        It marks the start of the UI, and hides everything on screen.
        """
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
    This is (like) an abstract class, so make sure you override the methods.
    """

    def show(self):
        """The mouse is hovering - what should change?"""
        raise NotImplementedError()

    def hide(self):
        """The mouse is not hovering - what should it display?"""
        raise NotImplementedError()

    def collide_point(self, x, y):
        """Does the behaviour collide with a point (where the cursor is)?

        Args:
            x (int): the x-coordinate.
            y (int): the y-coordinate.
        """
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
        """
        The show function is called when the mouse hovers over a word.
        It changes the font size and color of that word to make it stand out.
        """
        self.widget.text = self.text
        self.widget.font_name = self.font
        self.widget.font_size = self.font_size * HOVER_REPLACE_FACTOR

    def hide(self):
        """
        This behaviour takes the text from the widget and saves it in a variable.
        The original text is saved so that it can be restored later. This function restores it,
        as well as the original font_name and font_size.
        """
        self.widget.text = self.save
        self.widget.font_name = self.save_font
        self.widget.font_size = self.font_size

    def collide_point(self, x, y):
        """
        The collide_point function is used to determine if a point is inside the widget's area.
        It returns True if the point (x, y) is inside the widget's axis aligned bounding box.
        Forwards the call to Kivy's built-in `collide_point`.
        This is technically some design pattern, probably Mediator or Interface.
        """
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
        """
        The show function is called when the widget is hovered.
        It sets the background colour of the widget to be equal to 
        the value stored in `self.bg`.
        """
        super().show()
        self.widget.background_color = self.bg

    def hide(self):
        """
        The hide function is called when the widget is no longer hovered.
        It restores the background colour to the original:
        It sets the background colour of the widget to be equal to 
        the value stored in `self.save_bg`.
        """
        super().hide()
        self.widget.background_color = self.save_bg


if __name__ == '__main__':
    print("This module creates the Hovering mechanism for the kivy gui.")
