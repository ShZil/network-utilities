from typing import Any, Callable
from gui.AppState import State
from gui.ScanClasses import DummyScan
from gui.dialogs import popup, get_string


def display_configuration(*_):
    """
    The display_configuration function is a callback function that will be called when the user clicks on the "Configuration" button.
    
    Args:
        *_ (list[Any]): Ignore the parameters passed to this function
    """
    if State().highlighted_scan is None:
        name = "scans"
    elif State().highlighted_scan is DummyScan():
        name = "scans"
    else:
        name = State().highlighted_scan.name
    
    def _construct_content(info: dict) -> str:
        def _transform_item(item: tuple[str, Any]) -> tuple[str, Any]:
            key, value = item
            # title case, but doesn't affect acronyms.
            key = ' '.join([word if word.isupper() else word.capitalize() for word in key.split(' ')])
            return key, value

        if len(info) == 0:
            return "## No configurable customisable properties!"

        info = dict(map(_transform_item, info.items()))
        markdowned = [
            f"### {key}:\n`{value}`"
            for key, value in info.items()
            if key != ''
        ]
        return '\n\n'.join(markdowned)

    title = f"Configuration of {name}"
    do_edit = popup(title, "Configure the scan (OK) or view the current configuration (Cancel)?", cancel=True)
    if do_edit:
        if len(Configuration()[name]) == 0:
            popup(title, "## No configurable customisable properties.", warning=True)
        for key, value in Configuration()[name]:
            result = get_string(title, f"Enter new value for '{key}' [currently '{value}']:")
            if result.strip() == '':
                continue
            Configuration()[name, key] = result
    else:
        if len(Configuration()[name]) == 0:
            popup(title, "## No configurable customisable properties.", warning=True)
        popup(title, _construct_content(Configuration()[name]), info=True)


class Configuration(dict):
    _instance = None
    data = {}  # dict[scan: str, config: dict[property: Any, value: Any]]
    validity_checks = {}  # dict[property: str, validity: callable[Any -> bool]]

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __setitem__(self, key, value):
        if not isinstance(key, str):
            raise TypeError(f"Key must be of type str")
        if isinstance(value, tuple):
            value = {value[0]: value[1]}
        if not isinstance(value, dict):
            raise TypeError(f"Value must be dictionary or tuple")
        super().__setitem__(key, value)

    def __getitem__(self, key: str) -> dict:
        if not isinstance(key, str):
            raise TypeError(f"Key must be of type str")
        try:
            return super().__getitem__(key)
        except KeyError:
            return {}
    
    def get(self, name: str) -> dict:
        if not isinstance(name, str):
            raise TypeError(f"Key must be of type str")
        
        for key, value in Configuration()[name]:
            if value != None:
                continue
            result = None
            while not self.is_valid(key, result):
                result = get_string(f"Configuration of {name}", f"Enter value for '{key}':")
            Configuration()[name, key] = result
        return Configuration()[name]
    
    def is_valid(self, key: str, value) -> bool:
        if value is None:
            return False
        try:
            return bool(self.validity_checks[key](value))
        except KeyError:
            return True
        except ValueError:
            return False
    
    def add_validity_check(self, key: str, validity_check: Callable):
        if not callable(validity_check):
            raise TypeError(f"Validity Check must be callable")
        if not isinstance(key, str):
            raise TypeError(f"Key must be of type str")
        self.validity_checks[key] = validity_check


if __name__ == '__main__':
    print("This file is responsible for any methods called by the Configuration Button (⚙) in Scan Screen and Know Screen.")
