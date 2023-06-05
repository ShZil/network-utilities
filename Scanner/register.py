from time import time as now
from threading import Thread

from gui.dialogs import popup


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
            return lambda: popup("Coming Soon", "This scan is not implemented yet.")
            # raise KeyError(f"Key \"{key}\" not found in register. Try adding it :)")

    def start(self, name: str, action, callback) -> None:
        """
        The start function is used to start a new thread,
        that is running an action, its callback,
        and updating the history.

        Args:
            name (str): the name of the action, used to identify the thread.
            action (callable): the action (scan or analysis) to start.
            callback (callable): the callback to run when the action completes.
        """
        def _add_callback(action, callback):
            entry = [name, int(now()), -1]
            self.history.append(entry)
            action()
            callback()
            if not self.is_infinite_scan(name):
                entry[2] = int(now()) - entry[1]

        from RecommendProbabilities import step
        step(name)
        from gui.Screens.ScanScreen import update_recommendation
        update_recommendation()
        _add_callback.__name__ = action.__name__ + "_with_callback"
        self.threads[name] = t = Thread(target=_add_callback, args=(action, callback))
        t.start()

    def is_running(self, name: str) -> bool:
        """
        The is_running function checks if a thread is running.

        Args:
            name (str): Specify the name of the thread

        Returns:
            bool: True if the thread is alive, false if it is not
        """
        if name not in self.threads:
            return False
        if self.threads[name].is_alive():
            return True
        self.threads.pop(name)
        return

    def is_infinite_scan(self, name: str):
        """
        The is_infinite_scan function checks if the name of a scan is in the list of infinite scans.

        Args:
            name (str): Pass the name of the scan to be checked

        Returns:
            bool: whether the scan is infinite.
        """
        # `name` may contain '...' in the end.
        return name in self.infinites or name[:-3] in self.infinites

    def get_history(self):
        """Gets the history as a list of tuples.

        Returns:
            list[Tuple]: the history data.
        """
        return [tuple(item) for item in self.history]
