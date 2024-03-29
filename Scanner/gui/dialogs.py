from time import sleep
from typing import Callable
from import_handler import ImportDefence
from globalstuff import terminator
with ImportDefence():
    import win32api
    import win32con
    import markdown2
    import PySimpleGUIQt as sg
    import threading
    import time
    from enum import Enum
    import queue


class IconType(Enum):
    INPUT = 5
    ERROR = 4
    WARNING = 3
    QUESTION = 2
    INFO = 1
    NOTHING = 0

POPUP_WINDOW_SIZE = (1000, 600)
def get_CSS():
    """
    The get_CSS function is used to retrieve the CSS code from a file.
    The result will then be inserted into the HTML code.
    This allows for dynamic debugging of the style --
    not having to close and reopen the software makes designing much faster.
    """
    try:
        return f"<style>{open('./gui/popup_style.css', 'r').read()}</style>"
    except OSError:
        return f"<style></style>"
POPUP_WINDOW_LOOP_TIMEOUT_MS = 500

def get_icon_html(icon: IconType):
    """
    The get_icon_html function takes an IconType number and returns the HTML code for that icon.
    If no such file exists, it returns an empty string.
    This allows for dynamic debugging of the style --
    not having to close and reopen the software makes designing much faster.
    The icon is displayed as a header to the rest of the HTML.
    """
    try:
        return open(f'./gui/{icon.name}.html', 'r', encoding="utf-8").read()
    except OSError:
        return ""


class PopupManager:
    _instance = None  # Private class variable to store the singleton instance

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            sg.theme('DarkGreen5')
            cls._instance.waiting = queue.Queue()
            cls._instance.popup_thread = threading.Thread(target=cls._instance._popup_loop, name="PopupThread")
            cls._instance._stop_thread = threading.Event()
            cls._instance.popup_thread.start()
        return cls._instance

    def add(self, popup):
        """The add function adds a waiting popup to the queue."""
        self.waiting.put(popup)

    def render_popup(self, popup):
        """
        The render_popup function is called by the main loop when a popup needs to be displayed.
        It takes a tuple of (title, message, icon_type) and displays it in the appropriate way.
        The title and message are strings that will be displayed on screen.
        The icon_type is an integer value that determines what kind of popup this is (see IconType).
        """

        title, message, icon, *_ = popup
        icon = IconType(int(icon))
        if icon == IconType.INPUT:
            callback = popup[3]
            callback(self._get_input(title, message))
        else:
            self._show_text(title, message, icon)

    def _get_input(self, title: str, message: str):
        """Render a popup using `PySimpleGUIQt`, that has a textual user input."""
        layout = [[sg.Text(message)],
              [sg.Input(key='-IN-')],
              [sg.Button('Submit')]]

        window = sg.Window(title, layout)

        while not terminator.is_set():
            event, values = window.read()
            if event == sg.WINDOW_CLOSED:
                return ''
            elif event == 'Submit':
                result = values['-IN-']
                window.close()
                return result

    def _show_text(self, title: str, message: str, icon: IconType):
        """Shows a popup using `PySimpleGUIQt`,
        that displays markdown and CSS (combined via HTML),
        onto the popup.
        Also, trims lines on `. ` and `, ` if they are too long.

        Args:
            title (str): the title of the window.
            message (str): the contents of the popup (markdown syntax).
            icon (IconType): the icon type to use.

        Returns:
            Literal[-1]: terminates and returns -1 when the popup is closed.
        """
        lines = message.split('\n')
        lines = [
            item for line in lines
            for item in (
            line.split('. ') if len(line) > 200 else [line]
            )
        ]
        lines = [
            item for line in lines
            for item in (
            line.split(', ') if len(line) > 150 else [line]
            )
        ]
        lines = [line.strip() for line in lines]
        message = '\n\n'.join(lines)
        # message = message.replace('\n', '\n\n')
        markdown_text = markdown2.markdown(message)
        icon_html = get_icon_html(icon)
        html_text = f"{get_CSS()}{icon_html}<div class=\"limit-width\">{markdown_text}</div>"

        layout = [[
            sg.Column(
                [[sg.Text('', key='_HTML_')]],
                size=POPUP_WINDOW_SIZE,
                scrollable=(False, True)
            )
        ]]
        window = sg.Window(title, layout, finalize=True, resizable=False)
        window['_HTML_'].update(html_text.replace('\x00', '\\0'))  # remove null characters
        # window['_HTML_'].Widget.setOpenExternalLinks(True) # Allow links to be clicked

        while not terminator.is_set():
            event, values = window.read(timeout=POPUP_WINDOW_LOOP_TIMEOUT_MS)
            if event == sg.WIN_CLOSED:
                break

        window.close()
        return -1
    
    def stop(self):
        """
        The stop function sets the stop_thread event to true, which will cause the _popup_loop function to exit.
        """
        self._stop_thread.set()

    def _popup_loop(self):
        """
        Private method that runs continuously as the popup thread.
        Waits for popups to arrive and displays them when available.
        """
        while not self._stop_thread.is_set():
            try:
                popup = self.waiting.get(block=False)
                self.render_popup(popup)
            except queue.Empty:
                time.sleep(0.1)


def popup(title: str, message: str, *, error=False, warning=False, question=False, info=False, cancel=False):
    """This function creates a visual UI popup, with `title` as the window's title, and `message` in the body.
    The popup itself isn't too large.
    You can add `error`, `warning`, `question`, `info`, to set an icon next to the content.
    You can add `cancel` to give the user a choice between "OK" (returns True) and "Cancel" (returns False).

    This function unifys two separate ideas, under an abstracted interface.
    One is icnoned, with markdown support, and slower.
    One is iconless, plaintext, Win API, and faster.

    |     Popup Type     |                          Markdowned                         |               Plaintext              |
    |:------------------:|:-----------------------------------------------------------:|:------------------------------------:|
    | Supports plaintext | Yes                                                         | Yes                                  |
    |  Supports Markdown | Yes                                                         | No                                   |
    |  Supports HTML/CSS | Yes                                                         | No                                   |
    |   Supports Icons   | Yes (soon)                                                  | No                                   |
    |  Graphical Library | PySimpleGUI                                                 | Win32 API                            |
    |  Graphical Object  | `PySimpleGUIQt as sg; sg.Window, sg.Column, sg.Text`        | `win32api.MessageBox`                |
    |    Return Value    | None                                                        | bool or None                         |
    |   Arguments Used   | title, message, error, warning, question, info              | title, message, cancel               |
    |      Immediate     | No, uses a Queue on a separate thread                       | Yes                                  |
    |      Blocking      | No                                                          | Yes, until the user closes the popup |
    |    How to apply    | set either of these to True: error, warning, question, info | Don't apply the other option         |

    Note: if you supply markdown content into `message`, and you wish for it to not display as plaintext,
    set one of the icons, e.g. `info=True`.
    If multiple icons are set, the icon is chosen by this priority list:
    error > warning > question > info
    (`error` overpowers all, `info` gets overpowered by all).
    If no icon is chosen, the text is displayed as plaintext, not markdown.

    The function returns:
    - None for all `PySimpleGUI` dialogs, i.e. anything with an icon.
    - Boolean (True/False) indicating whether the Cancel button wasn't pressed, if `cancel=True`.
    - None if no keyword arguments were set, after displaying a `MessageBox`.
    Notice: the function will return immediately for `Markdowned`, it will be blocking for `Plaintext` (even if the return value will be `None` eventually).

    Args:
        title (str): the title of the window.
        message (str): the content of the window (plaintext or markdown).
        error (bool, optional): whether to display a Critical icon. Defaults to False.
        warning (bool, optional): whether to display a Warning icon. Defaults to False.
        question (bool, optional): whether to display a Question icon. Defaults to False.
        info (bool, optional): whether to display an Information icon. Defaults to False.
        cancel (bool, optional): if no icon is chosen, this determines the type of the MessageBox: whether there'll be a Cancel button. Defaults to False.

    Returns:
        (bool | None): `False` if the Cancel Button was pressed, `True` if not, `None` if irrelevant. See above.
    """
    if not isinstance(message, str):
        raise TypeError("Popup message must be a string.")
    if not isinstance(title, str):
        raise TypeError("Popup title must be a string.")
    if not (error or warning or question or info):
        if cancel:
            return win32api.MessageBox(0, message, title, win32con.MB_OKCANCEL) != win32con.IDCANCEL
        else:
            win32api.MessageBox(0, message, title, win32con.MB_OK)
            return None
    
    icon = IconType.NOTHING
    if error:
        icon = IconType.ERROR
    elif warning:
        icon = IconType.WARNING
    elif question:
        icon = IconType.QUESTION
    elif info:
        icon = IconType.INFO

    PopupManager().add((title, message, icon.value))


def get_string(title: str, prompt: str) -> str:
    """This function prompts the user to give a string input.
    It's basically like `input` in plain Python,
    but with a GUI.
    The window's title will be `title`.
    **Blocking** until user input is given.

    Args:
        title (str): the title of the small window.
        prompt (str): the question to ask the user.
    
    Returns:
        str: the string that the user has entered.
    """
    l = []  # Python has lists as reference type, so they can store data in just the way I need
    def _save(l ,x):  # used as callback, to store the result in the list.
        l.append(x)
    PopupManager().add((title, prompt, IconType.INPUT.value, lambda x: _save(l, x)))
    while len(l) == 0:  # blocking until `l` is given an item with the string.
        sleep(0.1)
    return l[0]


if __name__ == '__main__':
    print("This file gives visual dialog actions,")
    print("that are useful for displaying information to the user")
    print("as well as getting the user's input.")
