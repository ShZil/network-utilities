from import_handler import ImportDefence
with ImportDefence():
    import win32api
    from PyQt5.QtCore import Qt
    from PyQt5.QtWidgets import QApplication, QMessageBox
    import markdown2
    import PySimpleGUIQt as sg
    import html

class IconType(Enum):
    ERROR = 4
    WARNING = 3
    QUESTION = 2
    INFO = 1
    NOTHING = 0

POPUP_WINDOW_SIZE = (1000, 600)
POPUP_CSS = "<style>table {background-color: black;}</style>"
POPUP_WINDOW_LOOP_TIMEOUT_MS = 500


class PopupManager:
    _instance = None  # Private class variable to store the singleton instance

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.waiting = Queue()
            cls._instance.popup_thread = threading.Thread(target=cls._instance._popup_loop, name="Popup Thread")
            cls._instance._stop_thread = threading.Event()
            cls._instance.popup_thread.start()
        return cls._instance

    def add(self, popup):
        self.waiting.put(popup)

    def render_popup(self, popup):
        title, message, icon = popup
        icon = IconType(int(icon))
        html_text = POPUP_CSS + markdown2.markdown(message)

        layout = [[
            sg.Column(
                [[sg.Text('', key='_HTML_')]],
                size=POPUP_WINDOW_SIZE,
                scrollable=True
            )
        ]]
        window = sg.Window(title, layout, finalize=True)
        window['_HTML_'].update(html_text)

        while True:
            event, values = window.read(timeout=POPUP_WINDOW_LOOP_TIMEOUT_MS)
            if event == sg.WIN_CLOSED:
                break

        window.close()
        return -1
    
    def stop(self):
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
            except QueueEmptyError:
                time.sleep(0.1)


def popup(title: str, message: str, *, error=False, warning=False, question=False, info=False, cancel=False):
    """This function creates a visual UI popup, with `title` as the window's title, and `message` in the body.
    The popup itself isn't too large.
    You can add `error`, `warning`, `question`, `info`, to set an icon next to the content.
    You can add `cancel` to give the user a choice between "OK" (returns True) and "Cancel" (returns False).
    This function uses:
    - `win32api.MessageBox` -- if no icon is chosen. This displays plaintext, and allows for cancelling (if `cancel` is set).
    - `PySimpleGUI` -- if any icon is chosen. This displays markdown content.

    Note: if you supply markdown content into `message`, and you wish for it to not display as plaintext,
    set one of the icons, e.g. `info=True`.
    If multiple icons are set, the icon is chosen by this priority list:
    error > warning > question > info
    (`error` overpowers all, `info` gets overpowered by all).
    If no icon is chosen, the text is displayed as plaintext, not markdown.

    The function returns:
    - The integer -1 for all `PySimpleGUI` dialogs, i.e. anything with an icon.
    - Boolean (True/False) indicating whether the Cancel button wasn't pressed, if `cancel=True`.
    - None if no keyword arguments were set, after displaying a `MessageBox`.

    Args:
        title (str): the title of the window.
        message (str): the content of the window (plaintext or markdown).
        error (bool, optional): whether to display a Critical icon. Defaults to False.
        warning (bool, optional): whether to display a Warning icon. Defaults to False.
        question (bool, optional): whether to display a Question icon. Defaults to False.
        info (bool, optional): whether to display an Information icon. Defaults to False.
        cancel (bool, optional): if no icon is chosen, this determines the type of the MessageBox: whether there'll be a Cancel button. Defaults to False.

    Returns:
        (bool | Literal[-1] | None): return value's meaning depends on the arguments, see above.
    """
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
    It's basially like `input` in plain Python,
    but with a GUI.
    The window's title will be `title`.

    Args:
        title (str): the title of the small window.
        prompt (str): the question to ask the user.

    Returns:
        str: the input the user provided, and then hit `Submit`.
    """
    from PyQt5.QtWidgets import QApplication, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget

    app = QApplication([])
    widget = QWidget()
    layout = QVBoxLayout()

    label = QLabel(prompt)
    text_box = QLineEdit()
    button = QPushButton("Submit")

    def submit():
        result = text_box.text()
        widget.close()
        app.quit()
        return result

    button.clicked.connect(submit)
    layout.addWidget(label)
    layout.addWidget(text_box)
    layout.addWidget(button)
    widget.setWindowTitle(title)
    widget.setLayout(layout)

    widget.show()
    app.exec_()

    return submit()


if __name__ == '__main__':
    print("This file gives visual dialog actions,")
    print("that are useful for displaying information to the user")
    print("as well as getting the user's input.")
