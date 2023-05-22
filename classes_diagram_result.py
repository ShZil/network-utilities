
class Colors:
    """
    ANSI color codes 
    """

    
    # Fields:
BLACK
RED
GREEN
BROWN
BLUE
PURPLE
CYAN
LIGHT_GRAY
DARK_GRAY
LIGHT_RED
LIGHT_GREEN
YELLOW
LIGHT_BLUE
LIGHT_PURPLE
LIGHT_CYAN
LIGHT_WHITE
BOLD
FAINT
ITALIC
UNDERLINE
BLINK
NEGATIVE
CROSSED
END





class ScanFileBuilder:
    """
    
    """

    # Methods:
__init__
add
add_many
write_to
set_password
parse
    # Fields:
HEADER
SEP
COMMA





class Cipher_CBC:
    """
    
    """

    # Methods:
__init__
encrypt
decrypt
    





class ImportDefence:
    """
    This context manager ensures all `import` statements were successful,
and if some weren't, it attempts a `pip install`.

Source: https://raw.githubusercontent.com/ShZil/network-utilities/main/Scanner/import_handler.py

This function handles a ModuleNotFoundError,
attempting to install the not-found module using `pip install`,
and restarting the script / instructing the user.

Line-by-line breakdown of the ModuleNotFoundError handler:
- necessary imports: sys, os, subprocess

```py
import sys
from subprocess import check_call as do_command, CalledProcessError
import os
```

- print the failure

```py
print(f"Module `{err.name}` was not found. Attempting `pip install {err.name}`...
")
```

- try to pip install it

```py
try:
    do_command([sys.executable, "-m", "pip", "install", err.name])
```

- if failed, request manual installation

```py
except CalledProcessError:
    print(f"\nModule `{err.name}` could not be pip-installed. Please install manually.")
    sys.exit(1)
```

- if succeeded, restart the script

```py
argv = ['"' + sys.argv[0] + '"'] + sys.argv[1:]
os.execv(sys.executable, ['python'] + argv)
```

**Usage:**
```py
from import_handler import ImportDefence

with ImportDefence():
    import module1
    from module2 import some_function
```

    """

    # Methods:
__init__
__enter__
__exit__
    





class NetworkEntity:
    """
    
    """

    # Methods:
__init__
equals
__getitem__
__setitem__
__str__
to_string
to_dict
compare
merge
__hash__
__eq__
tablestring
    





class LockedNetworkEntity(NetworkEntity):
    """
    
    """

    # Methods:
__setitem__
merge
    





class NetworkStorage:
    """
    
    """

    # Methods:
__new__
_give_names
add
special_add
connect
_resolve
sort
organise
__iter__
__len__
__getitem__
print
tablestring
    # Fields:
data
waiting
connections





class LAN:
    """
    
    """

    # Methods:
__contains__
    





class SpecialInformation(dict):
    """
    
    """

    # Methods:
__new__
__init__
__setitem__
__getitem__
__contains__
    # Fields:
_instance





class ListWithSQL:
    """
    
    """

    # Methods:
__init__
copy
append
_flush_to_sql
extend
pop
index
count
insert
remove
sort
__len__
__iter__
__getitem__
__setitem__
__delitem__
__contains__
__reversed__
    # Fields:
CREATE
INSERT
CLEAR
RESET_AUTOINCREMENT





class ObserverPublisher:
    """
    This is the implementation of the Observer Behavioural Design Pattern,
which is used when a centralised source of data (the publisher) needs to send out updates (notifications)
to many code pieces (observers).

This specific implementation, being focused on not blocking the `add_datum` calls too much,
uses a separate thread to notify observers, and an internal queue to save the data in the meantime.

Just extend this class, make sure to call `.add_datum` when new data arrives,
and you can use `add_observer` to attach observers!
    """

    # Methods:
__init__
notify_all
add_observer
add_datum
    





class PacketSniffer(ObserverPublisher):
    """
    
    """

    # Methods:
__new__
__init__
stop
get_packet
_packet_handler
__len__
_flush_packets
_ip_filter
__iter__
    # Fields:
_instance
DB_PATH
SQL_CREATE_TABLE
INSERT_STATEMENT
CLEAR_TABLE





class _Printing:
    """
    This context manager delays and stores all outputs via `print`s.
It is not meant to be used directly, but other classes can inherit it.
    """

    # Methods:
__init__
__enter__
__exit__
    





class InstantPrinting(_Printing):
    """
    This context manager delays and stores all outputs via `print`s, and prints everything when closed.
Usage:
```py
with InstantPrinting():
# do some stuff here including printing
# Here, exiting the context, the printing will all happen immediately.
```
    """

    # Methods:
__init__
__enter__
__exit__
    





class NoPrinting(_Printing):
    """
    This context manager prevents all output (through `sys.stdout`, e.g. normal `print` statements) from showing.
Usage:
```py
with NoPrinting():
# do some stuff here including printing
# Nothing will actually display
```

Technical note: this just inherits `_Printing` with no additional behaviour.
    """

    
    





class _SplitStringIO:
    """
    This class is like the io.StringIO, but it splits different `write` statements.
Internally, this is a `list` of `StringIO`s.
Not meant for use outside the `util` module.

Implements:
`__init__`: initialises an empty list.
`write`: adds a StringIO to the list, and writes the data into it.
`getvalue`: returns a list of all the `.getvalue`s of the `StringIO`s.
`flush`: does nothing.
    """

    # Methods:
__init__
write
getvalue
flush
    





class JustifyPrinting(InstantPrinting):
    """
    This context manager delays and stores all outputs via `print`s, and prints everything when closed,
justifying every print statement to form a nice-looking block of text, where each line is centred and as widespread as is allowed.

Note: Messing with `print`'s default values (`sep=' ', end='\n'`) is not recommended,
since this context manager treats space-separated strings as belonging to the same statement,
and newline-separated string as belonging to different statements.

Usage:
```py
with JustifyPrinting():
# do some stuff here including printing
# Here, exiting the context, the printing will all happen immediately and (hopefully) nicely.
```
    """

    # Methods:
__init__
__exit__
    





class TablePrinting(InstantPrinting):
    """
    This context manager delays and stores all outputs via `print`s, and prints everything when closed,
justifying every print statement to form a nice-looking table.

Note: Messing with `print`'s default values (`sep=' ', end='\n'`) is not recommended,
since this context manager treats space-separated strings as belonging to the same statement,
and newline-separated string as belonging to different statements.

Usage:
```py
with TablePrinting():
# do some stuff here including printing
# Here, exiting the context, the printing will all happen immediately and (hopefully) nicely.
```
    """

    # Methods:
__init__
__exit__
    # Fields:
aligns





class AutoLinebreaks(InstantPrinting):
    """
    This context manager delays and stores all outputs via `print`s, and prints everything when closed,
wrapping lines only when nessessary to maintain integrity.
In short: Applies CSS's `word-wrap: normal;` (whereas the console is usually `word-wrap: break-word;`).

Note: Messing with `print`'s default values (`sep=' ', end='\n'`) is not recommended,
since this context manager treats space-separated strings as belonging to the same statement,
and newline-separated string as belonging to different statements.
You may do so after familiarising yourself with the code, in order to not induce annoying bugs.

Usage:
```py
with AutoLinebreaks():
# do some stuff here including printing
# Here, exiting the context, the printing will all happen immediately and (hopefully) nicely.
```
    """

    # Methods:
__init__
__exit__
    





class Register(dict):
    """
    This class managers the connection between names (strings)* and python methods (or lambdas; any callables) that execute these scans.
Usage (i.e. this is a dictionary):
```
Set: Register()["Scan Name"] = lambda: ...
Set: Register()["Scan Name"] = execute_scan  # no parentheses
Set: Register()["Scan Name"] = execute_infinite_scan, True
Get: x = Register()["Scan Name"]
```

This class implements the singleton pattern.

* formerly GUI Buttons, abstracted by `class Scan`.
    """

    # Methods:
__new__
__setitem__
__getitem__
start
is_running
is_infinite_scan
get_history
    # Fields:
_instance
infinites
history





class Sniffer(AsyncSniffer):
    """
    
    """

    # Methods:
__init__
stopall
    # Fields:
references





class MACVendorDict:
    """
    
    """

    # Methods:
__new__
__contains__
__setitem__
__getitem__
get
    # Fields:
_instance
path
CREATE_QUERY
SELECT_QUERY
INSERT_QUERY





class MyApp(App):
    """
    The main application, using `kivy`.
Includes five screens:
1. ScanScreen
2. SaveScreen
3. KnowScreen
4. StartScreen
5. ViewScreen (only accessible through `SaveScreen.ImportButton`)


Args:
App (tk): the tkinter base app.
    """

    # Methods:
build
    





class State:
    """
    
    """

    # Methods:
__new__
setScreenManager
screen
resize_callback
scan
ask_for_permission
    # Fields:
_instance





class Diagrams:
    """
    This class handles all the Diagrams that present the network graph (`G`).
To use, simply create an instance (uses Singleton), and do `.add` to your diagram.
    """

    # Methods:
__new__
add
update
    # Fields:
_instance





class Diagram(ABC):
    """
    This is an abstarct base class for diagrams that render the network.

    """

    # Methods:
__init__
update
color
rectangle
circle
line
__contains__
    





class TKDiagram(Diagram):
    """
    A diagram under `tkinter` window.
Uses tk.Canvas.
Doesn't actually close until `is_kivy_running` is set to False, and another closing is attempted.
Uses the Singleton pattern.

Extends:
Diagram (abstract class): allows for this class to be used as a diagram.
ContextManager (type): allows for this class to be used as a context manager (for rendering).
    """

    # Methods:
__new__
__init__
__exit__
color
rectangle
circle
line
__contains__
try_close
hide
show
resize
update
    # Fields:
_instance





class PlotDiagram(Diagram):
    """
    A diagram in a `matplotlib.pyplot` window.
Uses the Singleton pattern.

Extends:
Diagram (abstract class): allows for this class to be used as a diagram.
ContextManager (type): allows for this class to be used as a context manager (for rendering).
    """

    # Methods:
__new__
__init__
__enter__
__exit__
color
rectangle
circle
line
__contains__
update
show
hide
    # Fields:
_instance





class KivyDiagram(Diagram):
    """
    A diagram under `kivy` window, specifically the `Scan` screen, more specifically the `ScanScreenMiddleDiagram` widget.
Uses kivy's widget.canvas.
Linked to a kivy widget with `self.widget` and `.set_widget(widget)`.
There has to be a widget set before rendering (entering the context manager)!
You cannot change the widget once you set it.
Uses the Singleton pattern.

Extends:
Diagram (abstract class): allows for this class to be used as a diagram.
ContextManager (type): allows for this class to be used as a context manager (for rendering).
    """

    # Methods:
__new__
__init__
set_widget
__enter__
__exit__
color
rectangle
circle
line
__contains__
update
    # Fields:
_instance





class IconType(Enum):
    """
    
    """

    
    # Fields:
INPUT
ERROR
WARNING
QUESTION
INFO
NOTHING





class PopupManager:
    """
    
    """

    # Methods:
__new__
add
render_popup
_get_input
_show_text
stop
_popup_loop
    # Fields:
_instance





class Hover:
    """
    Enables hovering cursor and behaviours. Uses singleton structure (because it accesses a system function of changing cursor).
Includes two lists: `items`, where each item can change the cursor to `pointer` if hovered (`item.collide_point(x, y) -> True`);
and `behaviors`, where each item is a `HoverBehavior`, and they do more exotic stuff, abstracted by `.show()` and `.hide()`.

Raises:
AttributeError: raised when `.add(item)` receives an `item` that has no method `.collide_point(int,int)`.
TypeError: raised when `.add_behavior(behavior)` receives a `behavior` that is not of type `HoverBehavior`.
    """

    # Methods:
_bind
add
add_behavior
update
enter
start
    # Fields:
items
behaviors
current_screen





class HoverBehavior:
    """
    Inherit from this class to create behaviours,
and pass the instances to `Hover.add_behavior(...)`.
    """

    # Methods:
show
hide
collide_point
    





class HoverReplace(HoverBehavior):
    """
    A `HoverBehavior` that replaces the text shown on a label.
When hovered, it displays the string in `text`,
otherwise, it displays the initial string.
    """

    # Methods:
__init__
show
hide
collide_point
    





class HoverReplaceBackground(HoverReplace):
    """
    A `HoverBehavior` that replaces the text shown on a label.
When hovered, it displays the string in `text` (AND a different background colour),
otherwise, it displays the initial string.
    """

    # Methods:
__init__
show
hide
    





class ButtonColumn(GridLayout):
    """
    Organises buttons in a column

Args:
GridLayout (tk): the superclass.
    """

    # Methods:
__init__
add
add_raw
    





class MyPaintWidget(Widget):
    """
    Responsible for the middle diagram (object #9).
It is the caller's responsibility to set this as the `KivyDiagram()`'s widget.

Args:
Widget (tkinter widget): the superclass.
    """

    # Methods:
init
on_touch_down
    





class GreenButton(Button):
    """
    A button that has green background, and also adds itself to `Hover`.
    """

    # Methods:
__init__
    





class OperationButton(Button):
    """
    A button that has grey background, adds itself to `Hover`, defines a `HoverReplace` on itself, and uses font `Symbols`.
    """

    # Methods:
__init__
    





class Scan:
    """
    
    """

    # Methods:
__init__
select
paint_highligh
deselect
act
finished
    # Fields:
font_size
background_color





class DummyScan(Scan):
    """
    
    """

    # Methods:
__new__
__init__
select
deselect
act
finished
    # Fields:
_instance





class Analysis(Scan):
    """
    This is identical to a scan, except for cosmetic changes.
It's intended to be used under Know Screen.

Another difference, present in `Activation.py`, is that Analyses do not require confirmation popup;
just permission, which is half what other Scans need (permission + confirmation).

Changes:
- background colour is more blue.
- highlight colour is ANALYSIS_HIGHLIGHT.
    """

    # Methods:
__init__
paint_highligh
    





class KnowScreen(Screen):
    """
    Builds an interface that looks like this:

```md
The Window (Unicode Box Art):
┌────────────────────────────────────────────┐
│                  [#1 Title]                │
│  #4 Save.                                  │
│  #5 Scan.                                  │
│  #6 Know.                                  │
│             #3 Device Profile              │
│              #2 Data                       │
│     [_______________________]              │
│     [_______________________]              │
│     [_______________________]              │
│     [_______________________]              │
│                                            │
│                                            │
└────────────────────────────────────────────┘
```

Args:
Screen (kivy): the base class for a screen.
    """

    # Methods:
__init__
    





class KnowScreenRightColumn(ButtonColumn):
    """
    Builds the right column used in the screen 'Know'.

```md
Know Screen
. . . ─╥───────────────────────────┐
        ║   [#2 Conf]   [#3 Info]   │
        ╟───────────────────────────┤
        ║        [#7 KnowA]         │
        ║                           │
        ║        [#8 KnowB]         │
        ║                           │
        ║        [#9 KnowC]         │
        ║                           │
        ║        [#10 KnowD]        │
        ║                           │
        ║           . . .           │
        ║                           │
. . . ─╨───────────────────────────┘
```

Args:
ButtonColumn (GridLayout): this inherits from ButtonColumn.
    """

    # Methods:
__init__
    





class KnowScreenInfoLabel(ScrollView):
    """
    Holds the requested data in string format, displayed to the user.
Has a scrolling mechanic.

Args:
Label (kivy): the base class from kivy.
    """

    # Methods:
__init__
data
    





class Pages(BoxLayout):
    """
    
    """

    # Methods:
__init__
    





class SaveScreenExportButton(GreenButton):
    """
    
    """

    # Methods:
__init__
export
    





class SaveScreenImportButton(GreenButton):
    """
    
    """

    # Methods:
__init__
do_import
    





class SaveScreen(Screen):
    """
    Builds an interface that looks like this:

```md
The Window (Unicode Box Art):
┌────────────────────────────────────────────┐
│                  [#1 Title]                │
│  #4 Save.                                  │
│  #5 Scan.                                  │
│  #6 Know.                                  │
│                                            │
│       #2 Export            #3 Import       │
│                                            │
│                                            │
│                                            │
│                                            │
│                                            │
│                                            │
└────────────────────────────────────────────┘
```

Args:
Screen (kivy): the base class for a screen.
    """

    # Methods:
__init__
    





class ScanScreenMiddleDiagram(RelativeLayout):
    """
    Builds the middle diagram used in the screen 'Scan'.

```md
Scan Screen
┌────────────────────────────────────────────╥─ . . .
│                  [#1 Title]                ║
│  #4 Save.                                  ║
│  #5 Scan.                                  ║
│  #6 Know.                                  ║
│           #9 D                             ║
│                I                           ║
│                  A                         ║
│                    G                       ║
│                      R                     ║
│                        A                   ║
│                          M                 ║
│    [#15 Play]            [#16 Fullscreen]  ║
└────────────────────────────────────────────╨─ . . .
```

Args:
RelativeLayout (kivy): the diagram is a type of a Relative Layout, since widgets are placed sporadically.
    """

    # Methods:
__init__
    





class ScanScreenRightColumn(ButtonColumn):
    """
    Builds the right column used in the screen 'Scan'.

```md
Scan Screen
. . . ─╥───────────────────────────┐
        ║   [#2 Conf]   [#3 Info]   │
        ╟───────────────────────────┤
        ║        [#7 ScanA]         │
        ║                           │
        ║        [#8 ScanB]         │
        ║                           │
        ║        [#9 ScanC]         │
        ║                           │
        ║        [#10 ScanD]        │
        ║                           │
        ║           . . .           │
        ║                           │
. . . ─╨───────────────────────────┘
```

Args:
ButtonColumn (GridLayout): this inherits from ButtonColumn.
    """

    # Methods:
__init__
    





class ScanScreen(Screen):
    """
    Builds an interface that looks like this:

```md
The Window (Unicode Box Art):
┌────────────────────────────────────────────╥───────────────────────────┐
│                  [#1 Title]                ║   [#2 Conf]   [#3 Info]   │
│  #4 Save.                                  ╟───────────────────────────┤
│  #5 Scan.                                  ║        [#7 ScanA]         │
│  #6 Know.                                  ║                           │
│           #9 D                             ║        [#8 ScanB]         │
│                I                           ║                           │
│                  A                         ║        [#9 ScanC]         │
│                    G                       ║                           │
│                      R                     ║        [#10 ScanD]        │
│                        A                   ║                           │
│                          M                 ║           . . .           │
│    [#15 Play]            [#16 Fullscreen]  ║                           │
└────────────────────────────────────────────╨───────────────────────────┘
```

Args:
Screen (kivy): the base class for a screen.
    """

    # Methods:
__init__
    





class StartScreen(Screen):
    """
    Builds an interface that looks like this:

```md
The Window (Unicode Box Art):
┌────────────────────────────────────────────╥───────────────────────────┐
│                  [#1 Title]                ║   [#2 Conf]   [#3 Info]   │
│  #4 Save.                                  ╟───────────────────────────┤
│  #5 Scan.                                  ║        [#7 ScanA]         │
│  #6 Know.                                  ║                           │
│           #9 D                             ║        [#8 ScanB]         │
│                I                           ║                           │
│                  A                         ║        [#9 ScanC]         │
│                    G                       ║                           │
│                      R                     ║        [#10 ScanD]        │
│                        A                   ║                           │
│                          M                 ║           . . .           │
│    [#15 Play]            [#16 Fullscreen]  ║                           │
└────────────────────────────────────────────╨───────────────────────────┘
```

Args:
Screen (kivy): the base class for a screen.
    """

    # Methods:
__init__
    





class ViewScreenInfo(ScrollView):
    """
    Holds the requested data in string format, displayed to the user.
Has a scrolling mechanic.

Args:
Label (kivy): the base class from kivy.
    """

    # Methods:
__init__
data
    





class ViewScreen(Screen):
    """
    Builds an interface that looks like this:

```md
The Window (Unicode Box Art):
┌────────────────────────────────────────────┐
│                  [#1 Title]                │
│  #3 Know.                                  │
│  #4 Scan.                                  │
│  #5 Know.                                  │
│                                            │
│                   #2 Data                  │
│          [_______________________]         │
│          [_______________________]         │
│          [_______________________]         │
│          [_______________________]         │
│                                            │
│                                            │
└────────────────────────────────────────────┘
```

Args:
Screen (kivy): the base class for a screen.
    """

    # Methods:
__init__
    





class DeviceDiscoveryListener:
    """
    
    """

    # Methods:
__new__
__init__
check_packet
    # Fields:
_instance




