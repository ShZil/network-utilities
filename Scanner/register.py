class Register(dict):
    """This class managers the connection between names (strings)* and python methods (or lambdas; any callables) that execute these scans.
    This class implements the singleton pattern.

    * formerly GUI Buttons, abstracted by `class Scan`.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __setitem__(self, key, value):
        if not isinstance(key, str):
            raise TypeError(f"Key must be of type str")
        if not callable(value):
            raise TypeError(f"Value must be callable")
        super().__setitem__(key, value)

