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
