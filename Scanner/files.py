import tkinter.filedialog as dialogs
from tkinter.simpledialog import askstring


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
    
    password = askstring("Encrypt file with a password", "Insert password:")
    print(f"The password is \"{password}\"")  # check this. What happens when you click on Cancel? What about empty passwords? ************
    builder.set_password(password)
    builder.write_to(filename)
    return filename
    

def importer():
    filename = dialogs.askopenfilename(
        title="Open",
        filetypes=(("Scan files", "*.scan"), ("All files", "*.*")),
    )
    print("Importing from", filename)

    builder = ScanFileBuilder()
    password = askstring("Decrypt file with a password", "Insert password:")
    builder.set_password(password)
    result = builder.parse(filename)
    print(result)
    scan_id = result["scan_id"]
    entities = result["network_entities"]
    from main import parse_scan_id, get_scan_id
    same_network = scan_id == get_scan_id()
    same_network_message = "\nYou're currently in the same connection (computer, interface, network) as the scan file!" if same_network else "\n"
    scan_id = parse_scan_id(scan_id)
    entities = '\n'.join(entities)
    return f"""{scan_id}{same_network_message}\n\n{entities}"""


def ask_for_password():
    pass


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
        assert self.password is not None
        with open(path, "xb") as f:
            content = self.SEP.join(self.parts)
            # TODO: encode content with password **********
            f.write(content)
    
    def set_password(self, password: str):
        self.password = password

    def parse(self, path: str):
        assert self.password is not None
        self.parts = [b""] * 3
        with open(path, "rb") as f:
            content = f.read()
            # TODO: decode content with password **********
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
