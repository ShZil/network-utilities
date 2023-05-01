from import_handler import ImportDefence
with ImportDefence():
    import win32api
    from PyQt5.QtCore import Qt
    from PyQt5.QtWidgets import QApplication, QMessageBox
    import markdown2
    import PySimpleGUIQt as sg
    import html


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
    if error or warning or question or info:
        html_text = markdown2.markdown(message)
        layout = [[sg.Column([[sg.Text('', key='_HTML_')]], size=(600, 400), scrollable=True)]]
        window = sg.Window(title, layout, finalize=True)
        unescape_html_text = html.unescape(html_text)
        window['_HTML_'].update(unescape_html_text)

        while True:
            event, values = window.read()
            if event == sg.WIN_CLOSED:
                break

        window.close()
        return -1
    elif cancel:
        return win32api.MessageBox(0, message, title, 0x00000001) != 2
    else:
        win32api.MessageBox(0, message, title, 0x00000000)


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
