import networkx
from threading import Event

# --- The Graph ---
G = networkx.empty_graph()

# --- Inter-thread Communication ---
terminator = Event()

# --- GUI Global Values ---
is_kivy_running = True


# --- Design Settings ---
bg_color = (0, 0, .01)  # tuple[float]: rgb
fg_color = (0.023, 0.92, 0.125)  # tuple[float]: rgb
fg_highlight = (0.92, 0.823, 0.125)  # tuple[float]: rgb
router_highlight = (0.906, 0.518, 0.98)  # tuple[float]: rgb
here_highlight = (0.392, 1, 0.749)  # tuple[float]: rgb
button_column_background = [0.1, 1, 0.3, 1]  # list[float]: rgba
DIAGRAM_DIMENSIONS = (300, 300)  # tuple[int]: width, height
# float; under `HoverReplace`, `new_text_size = HOVER_REPLACE_FACTOR *
# old_text_size`, e.g. fontsizeof("Information") = 0.75 * fontsizeof("ℹ").
HOVER_REPLACE_FACTOR = 0.75
DIAGRAM_POINT_RADIUS = 5  # int: px
BUTTON_COLUMN_FONT_SIZE = 24  # int: px
# tuple[float]: rgba; used as overlay, do not set alpha=1, because that
# will hide the text.
SCAN_HIGHLIGHT = (0, 1, 0, 0.2)
ANALYSIS_HIGHLIGHT = (0, 0.2, 0.8, 0.2)
OPERATION_BUTTON_FONT_SIZE = 30  # int: px
OPERATION_BUTTON_BACKGROUND = [0.8, 0.8, 0.8, 1]  # list[float]: rgba
# int: px; the padding used by the kivy diagram from the top, to avoid
# hiding the title by overlapping it.
TITLE_HEIGHT = 70
DIAGRAM_SCALE = 1 / 2.3  # float
PAGES_BACKGROUND = [0, 0, 0, 0]  # list[float]: rgba
TITLE_FONT_SIZE = 30  # int: px
GREEN = '00ff00'  # str: hex color
UNDER_DIAGRAM_FONT_SIZE = 30  # int: px
RIGHT_COLUMN_WIDTH = 300  # int: px; in Scan screen.
SAVE_BUTTONS_HOVER_BACKGROUND = [0, 0, 1, 1]  # list[tuple]: rgba
SAVE_BUTTONS_FONT_SIZE = 50  # int: px


if __name__ == '__main__':
    print("This module provides global values to the other modules.")
    print("It does not depend on any other module, but on some libraries.")
    print("Three kinds of global variables:")
    print("    universal values between threads;")
    print("    dynamic information custom objects;")
    print("    hardcoded design settings.")
