import tkinter.filedialog as dialogs

def exporter():
    filename = dialogs.asksaveasfilename(
        title="Save As",
        defaultextension=".scan",
        filetypes=(("Scan files", "*.scan"), ("All files", "*.*")),
    )
    print(filename)
    builder = ScanFileBuilder()

    from NetworkStorage import NetworkStorage
    data = [str(x).encode() for x in NetworkStorage()]
    builder.add_parts(data)

    from main import get_scan_id
    scan_id = get_scan_id().encode()
    builder.add_part(scan_id)

    # TODO: add scans history

    builder.write_to(filename)
        

def importer():
    filename = dialogs.askopenfilename(
        title="Open",
        filetypes=(("Scan files", "*.scan"), ("All files", "*.*")),
    )
    print(filename)

    builder = ScanFileBuilder()
    builder.parse(filename)


def ask_for_password():
    pass


class ScanFileBuilder:
    HEADER = b"SHZILSCAN"
    SEP = b"\n"
    COMMA = b","

    def __init__(self):
        self.parts = [self.HEADER]

    def add(self, part: bytes):
        self.parts.append(part)

    def add_many(self, parts):
        self.parts.append(self.COMMA.join(parts))

    def write_to(self, path: str):
        with open(path, "xb") as f:
            content = self.SEP.join(self.parts)
            # TODO: encode content with password **********
            f.write(content)

    def parse(self, path: str):
        with open(path, "rb") as f:
            content = f.read()
            # TODO: decode content with password **********
            content = content.split(self.SEP)
            if content[0] != self.HEADER:
                raise ValueError("Invalid file format")   # or wrong password

            self.parts = content[1:]

        return {
            "scan_id": self.parts[0].decode(),
            "network_entities": [x.decode() for x in self.parts[1:]]
        }

if __name__ == '__main__':
    print("This module is used for saving scans as files,")
    print("and opening previously saved scans.")
