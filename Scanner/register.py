from time import time as now
import win32api
from threading import Thread


class Register(dict):
    """This class managers the connection between names (strings)* and python methods (or lambdas; any callables) that execute these scans.
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
    _instance = None
    threads: dict[str, Thread] = {}
    infinites = set()
    history = []  # list[list[str, int, int]]: [name, start time [unix timestamp], duration [seconds]]

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __setitem__(self, key, value):
        if not isinstance(key, str):
            raise TypeError(f"Key must be of type str")
        if isinstance(value, tuple):
            value, is_infinite = value
            if is_infinite:
                self.infinites.add(key)
        if not callable(value):
            raise TypeError(f"Value must be callable")
        super().__setitem__(key, value)

    def __getitem__(self, key: str):
        try:
            return super().__getitem__(key)
        except KeyError:
            return lambda: win32api.MessageBox(0,
                                               "This scan is not implemented yet.",
                                               "Coming Soon",
                                               0x00000000)
            # raise KeyError(f"Key \"{key}\" not found in register. Try adding it :)")

    def start(self, name: str, action, callback) -> None:
        def _add_callback(action, callback):
            entry = [name, int(now()), -1]
            self.history.append(entry)
            action()
            callback()
            if not self.is_infinite_scan(name):
                entry[2] = int(now()) - entry[1]

        _add_callback.__name__ = action.__name__ + "_with_callback"
        self.threads[name] = t = Thread(target=_add_callback, args=(action, callback))
        t.start()

    def is_running(self, name: str) -> bool:
        if name not in self.threads:
            return False
        if self.threads[name].is_alive():
            return True
        self.threads.pop(name)
        return
    
    def is_infinite_scan(self, name: str):
        # `name` may contain '...' in the end.
        return name in self.infinites or name[:-3] in self.infinites
    
    def get_history(self):
        return [tuple(item) for item in self.history]
