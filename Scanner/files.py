from import_handler import ImportDefence
with ImportDefence():
    import tkinter.filedialog as dialogs

import files_cryptography


def get_password():
    from gui import get_string
    return get_string("Enter password:")


def exporter():
    filename = dialogs.asksaveasfilename(
        title="Save As",
        defaultextension=".scan",
        filetypes=(("Scan files", "*.scan"), ("All files", "*.*")),
    )
    print("Exporting to", filename)
    if filename == "":
        return
    builder = ScanFileBuilder()

    from ScanID import get_scan_id
    scan_id = get_scan_id().encode()
    builder.add(scan_id)

    from NetworkStorage import NetworkStorage
    network_entities = [str(x).encode() for x in NetworkStorage()]  # ********* change this to `entity.encode()` and implement that method
    builder.add_many(network_entities)

    from register import Register
    scan_history = [
        int(timestamp).to_bytes(4, byteorder='big') +
        str(name).encode() +
        int(duration).to_bytes(3, byteorder='big')
        for (name, timestamp, duration) in Register().get_history()
    ]
    builder.add_many(scan_history)

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

    from ScanID import parse_scan_id, get_scan_id
    same_network = scan_id == get_scan_id()
    same_network_message = "\nYou're currently in the same connection (computer, interface, network) as the scan file!" if same_network else "\n"

    scan_id = result["scan_id"]
    scan_id = parse_scan_id(scan_id)

    entities = result["network_entities"]
    entities = '\n'.join(entities)

    history = result["scan_history"]
    from datetime import datetime
    def format_timestamp(t: int) -> str:
        return datetime.fromtimestamp(t).strftime('%Y-%m-%d %H:%M:%S')
    def format_duration(t: int) -> str:
        return f'for {t}[s]' if t > -1 else f'indefinitely'
    history = [format_timestamp(timestamp) + f' {name} {format_duration(duration)}.' for (timestamp, name, duration) in history]
    history = '\n'.join(history)

    return f"""{scan_id}{same_network_message}\n\n{entities}\n\n{history}"""


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
        assert self.password is not None
        with open(path, "xb") as f:
            content = self.SEP.join(self.parts)
            content = encrypt(content, self.password) if self.password != '' else content
            f.write(content)

    def set_password(self, password: str):
        self.password = password

    def parse(self, path: str):
        assert self.password is not None
        self.parts = [b""] * 3
        with open(path, "rb") as f:
            content = f.read()
            content = decrypt(content, self.password) if self.password != '' else content
            if content == b'':
                raise ValueError(
                    "Couldn't decrypt the file. The password is wrong"
                )
            content = content.split(self.SEP)
            if content[0] != self.HEADER:
                if not path.endswith('.scan'):
                    raise ValueError(
                        "Invalid file format. The extension is also wrong."
                    )
                # or wrong password
                raise ValueError("Invalid file format, or wrong password.")

            self.parts = content[1:]
        scan_id, entities, history, *rest = self.parts
        if len(rest) > 0:
            def _decode_bytes(b):
                try:
                    return b.decode('utf-8')
                except UnicodeDecodeError:
                    return b.hex()
            raise ValueError("The file has more content than expected: " + _decode_bytes(rest))

        return {
            "scan_id": scan_id.decode(),
            "network_entities": [x.decode() for x in entities.split(self.COMMA)],  # ******* change this to NetworkEntity.decode(x) and implement that method
            "scan_history": [(x[:4], x[4:-3].decode(), x[:-3]) for x in history.split(self.COMMA)]
        }


if __name__ == '__main__':
    print("This module is used for saving scans as files,")
    print("and opening previously saved scans.")
