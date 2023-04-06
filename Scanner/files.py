from import_handler import ImportDefence
with ImportDefence():
    import tkinter.filedialog as dialogs
    from call_function_with_timeout import SetTimeout
    from tkinter.simpledialog import askstring

import files_cryptography


def get_password():
    from PyQt5.QtWidgets import QApplication, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget

    app = QApplication([])
    widget = QWidget()
    layout = QVBoxLayout()

    label = QLabel("Enter password:")
    text_box = QLineEdit()
    button = QPushButton("Submit")

    def submit():
        password = text_box.text()
        widget.close()
        app.quit()
        return password

    button.clicked.connect(submit)
    layout.addWidget(label)
    layout.addWidget(text_box)
    layout.addWidget(button)
    widget.setLayout(layout)

    widget.show()
    app.exec_()

    password = submit()
    print(password)
    return password


def exporter():
    filename = dialogs.asksaveasfilename(
        title="Save As",
        defaultextension=".scan",
        filetypes=(("Scan files", "*.scan"), ("All files", "*.*")),
    )
    print("Exporting to", filename)
    if filename == "": return
    builder = ScanFileBuilder()

    from main import get_scan_id
    scan_id = get_scan_id().encode()
    builder.add(scan_id)

    from NetworkStorage import NetworkStorage
    data = [str(x).encode() for x in NetworkStorage()]
    builder.add_many(data)

    # TODO: add scans history
    
    builder.set_password(get_password())
    builder.write_to(filename)
    print("Done writing")
    return filename
    

def importer():
    filename = dialogs.askopenfilename(
        title="Open",
        filetypes=(("Scan files", "*.scan"), ("All files", "*.*")),
    )
    print("Importing from", filename)

    builder = ScanFileBuilder()
    builder.set_password(get_password())
    result = builder.parse(filename)
    # print(result)
    scan_id = result["scan_id"]
    entities = result["network_entities"]
    from main import parse_scan_id, get_scan_id
    same_network = scan_id == get_scan_id()
    same_network_message = "\nYou're currently in the same connection (computer, interface, network) as the scan file!" if same_network else "\n"
    scan_id = parse_scan_id(scan_id)
    entities = '\n'.join(entities)
    return f"""{scan_id}{same_network_message}\n\n{entities}"""


def encrypt(message: bytes, password: str) -> bytes:
    return files_cryptography.password_encrypt(message, password)


def decrypt(token: bytes, password: str) -> bytes:
    # decrypter_with_timeout = SetTimeout(files_cryptography.password_decrypt, timeout=10)
    # is_done, is_timeout, erro_message, results = decrypter_with_timeout(token, password)
    # return results if is_done else ""
    return files_cryptography.password_decrypt(token, password)


class ScanFileBuilder:
    HEADER = b"SHZILSCAN"
    SEP = b"\n"
    COMMA = b","

    def __init__(self):
        self.parts = [self.HEADER]
        self.password = None

    def add(self, part: bytes):
        self.parts.append(part)

    def add_many(self, parts):
        self.parts.append(self.COMMA.join(parts))

    def write_to(self, path: str):
        print("Writing to", path)
        assert self.password is not None
        print("past the assertion")
        with open(path, "xb") as f:
            print("Opened the file")
            content = self.SEP.join(self.parts)
            print("Generating content")
            content = encrypt(content, self.password)
            print("Writing content to file:")
            print(content)
            f.write(content)
    
    def set_password(self, password: str):
        self.password = password

    def parse(self, path: str):
        assert self.password is not None
        self.parts = [b""] * 3
        with open(path, "rb") as f:
            content = f.read()
            try:
                content = decrypt(content, self.password)
            except Exception as e:
                print(e.__class__.__name__, e)
                input()
            if content == b'':
                raise ValueError("Couldn't decrypt the file. The password is wrong")
            content = content.split(self.SEP)
            if content[0] != self.HEADER:
                if not path.endswith('.scan'):
                    raise ValueError("Invalid file format. The extension is also wrong.")
                raise ValueError("Invalid file format, or wrong password.")  # or wrong password

            self.parts = content[1:]

        return {
            "scan_id": self.parts[0].decode(),
            "network_entities": [x.decode() for x in self.parts[1].split(self.COMMA)]
        }

if __name__ == '__main__':
    print("This module is used for saving scans as files,")
    print("and opening previously saved scans.")
