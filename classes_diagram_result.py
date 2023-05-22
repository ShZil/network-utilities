class Colors:
    """
    ANSI color codes 
    """
    BLACK = ...

    RED = ...

    GREEN = ...

    BROWN = ...

    BLUE = ...

    PURPLE = ...

    CYAN = ...

    LIGHT_GRAY = ...

    DARK_GRAY = ...

    LIGHT_RED = ...

    LIGHT_GREEN = ...

    YELLOW = ...

    LIGHT_BLUE = ...

    LIGHT_PURPLE = ...

    LIGHT_CYAN = ...

    LIGHT_WHITE = ...

    BOLD = ...

    FAINT = ...

    ITALIC = ...

    UNDERLINE = ...

    BLINK = ...

    NEGATIVE = ...

    CROSSED = ...

    END = ...


class ScanFileBuilder:
    """
    
    """
    def __init__(self):
        """
        
        """
        pass

    def add(self, part) -> part: bytes:
        """
        
        """
        pass

    def add_many(self, parts):
        """
        
        """
        pass

    def write_to(self, path) -> path: str:
        """
        
        """
        pass

    def set_password(self, password) -> password: str:
        """
        
        """
        pass

    def parse(self, path) -> path: str:
        """
        
        """
        pass

    HEADER = ...

    SEP = ...

    COMMA = ...


class Cipher_CBC:
    """
    
    """
    def __init__(self, password) -> password: str:
        """
        This function initializes the cipherer.

Args:
    password (str): The password used to encrypt and decrypt the data.
        """
        pass

    def encrypt(self, msg) -> msg: bytes:
        """
        This function encrypts the message.

Args:
    msg (bytes): The message to encrypt.

Returns:
    bytes: The encrypted message.
        """
        pass

    def decrypt(self, ciphertext) -> ciphertext: bytes:
        """
        This function decrypts the message.

Args:
    ciphertext (bytes): The ciphertext to decrypt.

Returns:
    bytes: The decrypted message.
        """
        pass


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
    def __init__(self):
        """
        
        """
        pass

    def __enter__(self):
        """
        
        """
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        
        """
        pass


class NetworkEntity:
    """
    
    """
    def __init__(self, mac, ip, ipv6, name):
        """
        
        """
        pass

    def equals(self, other) -> other: object:
        """
        This method checks equality between `self` and `other`.

Note: Transitive Property of Equality (A=B and B=C => A=C) doesn't necessarily apply here.
There can be cases where A = B and B = C but A != C.
This is because this method is based on (possibly) incomplete information in NetworkEntity-ies.

Examples:
```
    | MAC               | IPv4        | IPv6                                   |
|---|-------------------|-------------|----------------------------------------|
| A | 00:00:5E:00:53:AF | 192.168.0.5 | 2001:db8:3333:4444:CCCC:DDDD:EEEE:FFFF |
| B |                   | 192.168.0.5 | 2001:db8:3333:4444:CCCC:DDDD:EEEE:FFFF |
| C | 00:00:5E:11:90:B1 | 192.168.0.5 |                                        |
| D |                   |             | 2001:db8:3333:4444:CCCC:DDDD:EEEE:FFFF |
```
Here, for example, `A` contains the full information,
`B` contains only IPv4 and IPv6 addresses,
`C` contains the true IPv4, a false MAC (maybe from an ARP poisoning attack), and no IPv6;
and `D` contains only an IPv6 address.
- Comparing `A == B` will compare the IPv4 and IPv6, and return `True`.
- Comparing `B == C` will compare only the IPv4, and return `True`.
- Comparing `A == C` will compare the MAC (doesn't match) and IPv4 (does match), and return `False`.
- Comparing `D == C` will find no intersection between the address data, and return `False`.
- Comparing `E == nothing` will return `False` for every `NetworkEntity E` (including `E = nothing`!).

Args:
    other (object): the object to compare to.

Returns:
    bool: whether the NetworkEntity-ies are equal.
        """
        pass

    def __getitem__(self, key):
        """
        
        """
        pass

    def __setitem__(self, key, value):
        """
        
        """
        pass

    def __str__(self):
        """
        
        """
        pass

    def to_string(self, sep):
        """
        
        """
        pass

    def to_dict(self):
        """
        
        """
        pass

    def compare(self):
        """
        Turns the values of the Entity's fields into integers to be used in a comparison.

Returns:
    dict: field names as the keys, integers as the values.
        """
        pass

    def merge(self, other):
        """
        Merges the information from two equal NetworkEntity-ies.
This method fills in any missing information in `self` with the information from `other`.
Note: they must be equal.
Note: merges right-into-left -- in `A.merge(B)`, A is full with information, and B is unchanged.

Args:
    other (NetworkEntity): the entity to be merged with.
        """
        pass

    def __hash__(self):
        """
        
        """
        pass

    def __eq__(self, other):
        """
        
        """
        pass

    def tablestring(self, lengths):
        """
        
        """
        pass


class LockedNetworkEntity(NetworkEntity):
    """
    
    """
    def __setitem__(self, key, value):
        """
        
        """
        pass

    def merge(self, other):
        """
        
        """
        pass


class NetworkStorage:
    """
    
    """
    def __new__(cls):
        """
        
        """
        pass

    def _give_names(self):
        """
        
        """
        pass

    def add(self):
        """
        
        """
        pass

    def special_add(self):
        """
        Adds a special LockedNetworkEntity to the `specials` list.
NOT THREAD-SAFE. Only use in non-parellel code.
Intended for LockedNetworkEntities but regular NetworkEntities are allowed too.

Args:
    entities (list[NetworkEntity]): the special entities to be added.
        """
        pass

    def connect(self, ip1, ip2):
        """
        
        """
        pass

    def _resolve(self):
        """
        
        """
        pass

    def sort(self, key):
        """
        
        """
        pass

    def organise(self, key):
        """
        Converts the storage into a dictionary, with the key being one of the fields, and the values -- the whole entity.
Example:
```
data = [networkEntity1, networkEntity2, networkEntity3]
organise('ip') = {
    "1.1.1.1": networkEntity1,
    "2.2.2.2": networkEntity2,
    "1.0.0.3": networkEntity3
}
```

Args:
    key (str, optional): the key for the dictionary. Must be `mac`, `ip`, `ipv6`, or `name`. Defaults to `ip`.

Returns:
    dict: the dictionary as described above.

Raises:
    TypeError: if the key is invalid.
        """
        pass

    def __iter__(self):
        """
        
        """
        pass

    def __len__(self):
        """
        
        """
        pass

    def __getitem__(self, key):
        """
        Gets a single "column" (key, property, field) as a list from all the NetworkEntity-ies stored.
Note: this will not include empty values. E.g., asking for `lookup['ipv6']` will not return any data from entities without an IPv6 datum.

Args:
    key (str): the key to select from all the entities. Must be 'mac', 'ip', 'ipv6', or 'name'.

Raises:
    TypeError: if the key is invalid.

Returns:
    list: a list containing all the requested data.
        """
        pass

    def print(self):
        """
        
        """
        pass

    def tablestring(self):
        """
        
        """
        pass

    data = ...

    waiting = ...

    connections = ...


class LAN:
    """
    
    """
    def __contains__(self, entity):
        """
        
        """
        pass


class SpecialInformation(dict):
    """
    
    """
    def __new__(cls):
        """
        
        """
        pass

    def __init__(self):
        """
        
        """
        pass

    def __setitem__(self, keys, value) -> keys: tuple[NetworkEntity, str]:
        """
        
        """
        pass

    def __getitem__(self, key):
        """
        
        """
        pass

    def __contains__(self, item):
        """
        
        """
        pass

    _instance = ...


class ListWithSQL:
    """
    
    """
    def __init__(self, path, maxram) -> path: str, maxram: int:
        """
        
        """
        pass

    def copy(self):
        """
        
        """
        pass

    def append(self, __object) -> __object: _T:
        """
        
        """
        pass

    def _flush_to_sql(self):
        """
        
        """
        pass

    def extend(self, __iterable) -> __iterable: Iterable[_T]:
        """
        
        """
        pass

    def pop(self, __index) -> __index: SupportsIndex:
        """
        
        """
        pass

    def index(self, __value, __start, __stop) -> __value: _T, __start: SupportsIndex, __stop: SupportsIndex:
        """
        
        """
        pass

    def count(self, __value) -> __value: _T:
        """
        
        """
        pass

    def insert(self, __index, __object) -> __index: SupportsIndex, __object: _T:
        """
        
        """
        pass

    def remove(self, __value) -> __value: _T:
        """
        
        """
        pass

    def sort(self) -> self: list:
        """
        
        """
        pass

    def __len__(self):
        """
        
        """
        pass

    def __iter__(self):
        """
        
        """
        pass

    def __getitem__(self, __i) -> __i: SupportsIndex | slice:
        """
        
        """
        pass

    def __setitem__(self, __key, __value) -> __key: SupportsIndex, __value: _T:
        """
        
        """
        pass

    def __delitem__(self, __key) -> __key: SupportsIndex | slice:
        """
        
        """
        pass

    def __contains__(self, __key) -> __key: object:
        """
        
        """
        pass

    def __reversed__(self):
        """
        
        """
        pass

    CREATE = ...

    INSERT = ...

    CLEAR = ...

    RESET_AUTOINCREMENT = ...


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
    def __init__(self):
        """
        
        """
        pass

    def notify_all(self):
        """
        
        """
        pass

    def add_observer(self, observer) -> observer: Callable:
        """
        
        """
        pass

    def add_datum(self, datum):
        """
        
        """
        pass


class PacketSniffer(ObserverPublisher):
    """
    
    """
    def __new__(cls, max_packets):
        """
        
        """
        pass

    def __init__(self, max_packets):
        """
        
        """
        pass

    def stop(self):
        """
        
        """
        pass

    def get_packet(self, i) -> i: int:
        """
        
        """
        pass

    def _packet_handler(self, packet):
        """
        
        """
        pass

    def __len__(self):
        """
        
        """
        pass

    def _flush_packets(self):
        """
        
        """
        pass

    def _ip_filter(self, packet):
        """
        
        """
        pass

    def __iter__(self):
        """
        
        """
        pass

    _instance = ...

    DB_PATH = ...

    SQL_CREATE_TABLE = ...

    INSERT_STATEMENT = ...

    CLEAR_TABLE = ...


class _Printing:
    """
    This context manager delays and stores all outputs via `print`s.
It is not meant to be used directly, but other classes can inherit it.
    """
    def __init__(self):
        """
        
        """
        pass

    def __enter__(self):
        """
        
        """
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        
        """
        pass


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
    def __init__(self):
        """
        
        """
        pass

    def __enter__(self):
        """
        
        """
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        
        """
        pass


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
    def __init__(self):
        """
        
        """
        pass

    def write(self, data):
        """
        
        """
        pass

    def getvalue(self):
        """
        
        """
        pass

    def flush():
        """
        
        """
        pass


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
    def __init__(self):
        """
        
        """
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        
        """
        pass


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
    def __init__(self, align):
        """
        
        """
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        
        """
        pass

    aligns = ...


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
    def __init__(self):
        """
        
        """
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        
        """
        pass


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
    def __new__(cls):
        """
        
        """
        pass

    def __setitem__(self, key, value):
        """
        
        """
        pass

    def __getitem__(self, key) -> key: str:
        """
        
        """
        pass

    def start(self, name, action, callback) -> name: str:
        """
        
        """
        pass

    def is_running(self, name) -> name: str:
        """
        
        """
        pass

    def is_infinite_scan(self, name) -> name: str:
        """
        
        """
        pass

    def get_history(self):
        """
        
        """
        pass

    _instance = ...

    infinites = ...

    history = ...


class Sniffer(AsyncSniffer):
    """
    
    """
    def __init__(self):
        """
        
        """
        pass

    def stopall():
        """
        
        """
        pass

    references = ...


class MACVendorDict:
    """
    
    """
    def __new__(cls):
        """
        
        """
        pass

    def __contains__(self, mac):
        """
        
        """
        pass

    def __setitem__(self, mac, text):
        """
        
        """
        pass

    def __getitem__(self, mac):
        """
        
        """
        pass

    def get(self, mac, default):
        """
        
        """
        pass

    _instance = ...

    path = ...

    CREATE_QUERY = ...

    SELECT_QUERY = ...

    INSERT_QUERY = ...


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
    def build(self):
        """
        
        """
        pass


class State:
    """
    
    """
    def __new__(cls):
        """
        
        """
        pass

    def setScreenManager(self, screens):
        """
        
        """
        pass

    def screen(self, name):
        """
        
        """
        pass

    def resize_callback(self):
        """
        
        """
        pass

    def scan(self, scan):
        """
        
        """
        pass

    def ask_for_permission(self):
        """
        
        """
        pass

    _instance = ...


class Diagrams:
    """
    This class handles all the Diagrams that present the network graph (`G`).
To use, simply create an instance (uses Singleton), and do `.add` to your diagram.
    """
    def __new__(cls):
        """
        Override the __new__ method to create only one instance of the class -- Singleton pattern.
        """
        pass

    def add(self, diagram):
        """
        
        """
        pass

    def update(self):
        """
        
        """
        pass

    _instance = ...


class Diagram(ABC):
    """
    This is an abstarct base class for diagrams that render the network.
    
    """
    def __init__(self):
        """
        
        """
        pass

    def update(self):
        """
        
        """
        pass

    def color(self, r, g, b):
        """
        
        """
        pass

    def rectangle(self, x, y, w, h):
        """
        
        """
        pass

    def circle(self, x, y, node):
        """
        
        """
        pass

    def line(self, x0, y0, x1, y1, stroke):
        """
        
        """
        pass

    def __contains__(self, pos):
        """
        
        """
        pass


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
    def __new__(cls):
        """
        
        """
        pass

    def __init__(self):
        """
        
        """
        pass

    def __exit__(self, exception_type, exception_value, exception_traceback):
        """
        
        """
        pass

    def color(self, r, g, b):
        """
        
        """
        pass

    def rectangle(self, x, y, w, h):
        """
        
        """
        pass

    def circle(self, x, y, node):
        """
        
        """
        pass

    def line(self, x0, y0, x1, y1, stroke):
        """
        
        """
        pass

    def __contains__(self, pos):
        """
        
        """
        pass

    def try_close(self):
        """
        To prevent the user from really closing this window if the source (kivy) is still open.
        """
        pass

    def hide(self):
        """
        
        """
        pass

    def show(self):
        """
        
        """
        pass

    def resize(self, event):
        """
        
        """
        pass

    def update(self):
        """
        
        """
        pass

    _instance = ...


class PlotDiagram(Diagram):
    """
    A diagram in a `matplotlib.pyplot` window.
Uses the Singleton pattern.

Extends:
    Diagram (abstract class): allows for this class to be used as a diagram.
    ContextManager (type): allows for this class to be used as a context manager (for rendering).
    """
    def __new__(cls):
        """
        
        """
        pass

    def __init__(self):
        """
        
        """
        pass

    def __enter__(self):
        """
        
        """
        pass

    def __exit__(self, exception_type, exception_value, exception_traceback):
        """
        
        """
        pass

    def color(self, r, g, b):
        """
        
        """
        pass

    def rectangle(self, x, y, w, h):
        """
        
        """
        pass

    def circle(self, x, y, node):
        """
        
        """
        pass

    def line(self, x0, y0, x1, y1, stroke):
        """
        
        """
        pass

    def __contains__(self, pos):
        """
        
        """
        pass

    def update(self):
        """
        
        """
        pass

    def show(self):
        """
        
        """
        pass

    def hide(self):
        """
        
        """
        pass

    _instance = ...


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
    def __new__(cls):
        """
        
        """
        pass

    def __init__(self):
        """
        
        """
        pass

    def set_widget(self, widget):
        """
        
        """
        pass

    def __enter__(self):
        """
        
        """
        pass

    def __exit__(self, exception_type, exception_value, exception_traceback):
        """
        
        """
        pass

    def color(self, r, g, b):
        """
        
        """
        pass

    def rectangle(self, x, y, w, h):
        """
        
        """
        pass

    def circle(self, x, y, node):
        """
        
        """
        pass

    def line(self, x0, y0, x1, y1, stroke):
        """
        
        """
        pass

    def __contains__(self, pos):
        """
        
        """
        pass

    def update(self):
        """
        
        """
        pass

    _instance = ...


class IconType(Enum):
    """
    
    """
    INPUT = ...

    ERROR = ...

    WARNING = ...

    QUESTION = ...

    INFO = ...

    NOTHING = ...


class PopupManager:
    """
    
    """
    def __new__(cls):
        """
        
        """
        pass

    def add(self, popup):
        """
        
        """
        pass

    def render_popup(self, popup):
        """
        
        """
        pass

    def _get_input(self, title, message) -> title: str, message: str:
        """
        
        """
        pass

    def _show_text(self, title, message, icon) -> title: str, message: str, icon: IconType:
        """
        
        """
        pass

    def stop(self):
        """
        
        """
        pass

    def _popup_loop(self):
        """
        Private method that runs continuously as the popup thread.
Waits for popups to arrive and displays them when available.
        """
        pass

    _instance = ...


class Hover:
    """
    Enables hovering cursor and behaviours. Uses singleton structure (because it accesses a system function of changing cursor).
Includes two lists: `items`, where each item can change the cursor to `pointer` if hovered (`item.collide_point(x, y) -> True`);
and `behaviors`, where each item is a `HoverBehavior`, and they do more exotic stuff, abstracted by `.show()` and `.hide()`.

Raises:
    AttributeError: raised when `.add(item)` receives an `item` that has no method `.collide_point(int,int)`.
    TypeError: raised when `.add_behavior(behavior)` receives a `behavior` that is not of type `HoverBehavior`.
    """
    def _bind():
        """
        
        """
        pass

    def add(instance):
        """
        
        """
        pass

    def add_behavior(behavior):
        """
        
        """
        pass

    def update(window, pos):
        """
        
        """
        pass

    def enter(screen) -> screen: str:
        """
        
        """
        pass

    def start():
        """
        
        """
        pass

    items = ...

    behaviors = ...

    current_screen = ...


class HoverBehavior:
    """
    Inherit from this class to create behaviours,
and pass the instances to `Hover.add_behavior(...)`.
    """
    def show(self):
        """
        
        """
        pass

    def hide(self):
        """
        
        """
        pass

    def collide_point(self, x, y):
        """
        
        """
        pass


class HoverReplace(HoverBehavior):
    """
    A `HoverBehavior` that replaces the text shown on a label.
When hovered, it displays the string in `text`,
otherwise, it displays the initial string.
    """
    def __init__(self, widget, text, font_size, font):
        """
        
        """
        pass

    def show(self):
        """
        
        """
        pass

    def hide(self):
        """
        
        """
        pass

    def collide_point(self, x, y):
        """
        
        """
        pass


class HoverReplaceBackground(HoverReplace):
    """
    A `HoverBehavior` that replaces the text shown on a label.
When hovered, it displays the string in `text` (AND a different background colour),
otherwise, it displays the initial string.
    """
    def __init__(self, widget, text, font_size, new_bg, font):
        """
        
        """
        pass

    def show(self):
        """
        
        """
        pass

    def hide(self):
        """
        
        """
        pass


class ButtonColumn(GridLayout):
    """
    Organises buttons in a column

Args:
    GridLayout (tk): the superclass.
    """
    def __init__(self, width) -> width: int:
        """
        
        """
        pass

    def add(self, text, callback) -> text: str:
        """
        
        """
        pass

    def add_raw(self, button):
        """
        
        """
        pass


class MyPaintWidget(Widget):
    """
    Responsible for the middle diagram (object #9).
It is the caller's responsibility to set this as the `KivyDiagram()`'s widget.

Args:
    Widget (tkinter widget): the superclass.
    """
    def init(self):
        """
        
        """
        pass

    def on_touch_down(self, touch):
        """
        
        """
        pass


class GreenButton(Button):
    """
    A button that has green background, and also adds itself to `Hover`.
    """
    def __init__(self, text):
        """
        
        """
        pass


class OperationButton(Button):
    """
    A button that has grey background, adds itself to `Hover`, defines a `HoverReplace` on itself, and uses font `Symbols`.
    """
    def __init__(self, text, long_text, onclick):
        """
        
        """
        pass


class Scan:
    """
    
    """
    def __init__(self, name, action, parent):
        """
        
        """
        pass

    def select(self, x):
        """
        
        """
        pass

    def paint_highligh(self):
        """
        
        """
        pass

    def deselect(self):
        """
        
        """
        pass

    def act(self):
        """
        
        """
        pass

    def finished(self):
        """
        
        """
        pass

    font_size = ...

    background_color = ...


class DummyScan(Scan):
    """
    
    """
    def __new__(cls):
        """
        
        """
        pass

    def __init__(self):
        """
        
        """
        pass

    def select(self, x):
        """
        
        """
        pass

    def deselect(self):
        """
        
        """
        pass

    def act(self):
        """
        
        """
        pass

    def finished(self):
        """
        
        """
        pass

    _instance = ...


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
    def __init__(self, name, action, parent):
        """
        
        """
        pass

    def paint_highligh(self):
        """
        
        """
        pass


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
    def __init__(self):
        """
        
        """
        pass


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
    def __init__(self):
        """
        
        """
        pass


class KnowScreenInfoLabel(ScrollView):
    """
    Holds the requested data in string format, displayed to the user.
Has a scrolling mechanic.

Args:
    Label (kivy): the base class from kivy.
    """
    def __init__(self):
        """
        
        """
        pass

    def data(self, text):
        """
        
        """
        pass


class Pages(BoxLayout):
    """
    
    """
    def __init__(self):
        """
        
        """
        pass


class SaveScreenExportButton(GreenButton):
    """
    
    """
    def __init__(self):
        """
        
        """
        pass

    def export(self, _):
        """
        
        """
        pass


class SaveScreenImportButton(GreenButton):
    """
    
    """
    def __init__(self):
        """
        
        """
        pass

    def do_import(self, _):
        """
        
        """
        pass


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
    def __init__(self):
        """
        
        """
        pass


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
    def __init__(self):
        """
        
        """
        pass


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
    def __init__(self):
        """
        
        """
        pass


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
    def __init__(self):
        """
        
        """
        pass


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
    def __init__(self):
        """
        
        """
        pass


class ViewScreenInfo(ScrollView):
    """
    Holds the requested data in string format, displayed to the user.
Has a scrolling mechanic.

Args:
    Label (kivy): the base class from kivy.
    """
    def __init__(self):
        """
        
        """
        pass

    def data(self, text):
        """
        
        """
        pass


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
    def __init__(self):
        """
        
        """
        pass


class DeviceDiscoveryListener:
    """
    
    """
    def __new__(cls):
        """
        
        """
        pass

    def __init__(self):
        """
        
        """
        pass

    def check_packet(self, packet):
        """
        
        """
        pass

    _instance = ...


