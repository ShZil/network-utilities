from import_handler import ImportDefence
with ImportDefence():
    import tkinter.filedialog as dialogs
    from call_function_with_timeout import SetTimeout

import files_cryptography


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
    
    builder.set_password(input("Password: "))
    builder.write_to(filename)
    return filename
    

def importer():
    filename = dialogs.askopenfilename(
        title="Open",
        filetypes=(("Scan files", "*.scan"), ("All files", "*.*")),
    )
    print("Importing from", filename)

    builder = ScanFileBuilder()
    builder.set_password(input("Password: "))
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
    decrypter_with_timeout = SetTimeout(files_cryptography.password_decrypt, timeout=5)
    is_done, is_timeout, erro_message, results = decrypter_with_timeout(token, password)
    return results if is_done else ""


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
            content = encrypt(content, self.password)
            f.write(content)
    
    def set_password(self, password: str):
        self.password = password

    def parse(self, path: str):
        assert self.password is not None
        self.parts = [b""] * 3
        with open(path, "rb") as f:
            content = f.read()
            print("Read the file")
            content = decrypt(content, self.password)
            if content == '':
                raise ValueError("Couldn't decrypt the file. The password is wrong")
            print("Decrypted the file")
            content = content.split(self.SEP)
            print("Checking the file")
            if content[0] != self.HEADER:
                print("Bad file", content[0], self.HEADER)
                if not path.endswith('.scan'):
                    raise ValueError("Invalid file format. The extension is also wrong.")
                raise ValueError("Invalid file format, or wrong password.")  # or wrong password

            print("Good file", content[1:])
            self.parts = content[1:]

        return {
            "scan_id": self.parts[0].decode(),
            "network_entities": [x.decode() for x in self.parts[1].split(self.COMMA)]
        }

if __name__ == '__main__':
    print("This module is used for saving scans as files,")
    print("and opening previously saved scans.")
