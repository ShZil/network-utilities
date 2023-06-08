from time import sleep
from typing import Iterable
from import_handler import ImportDefence
with ImportDefence():
    import tkinter.filedialog as dialogs

import files_cryptography


def get_password():
    """Gets the password for the file from the user.

    Returns:
        str: the password.
    """
    from gui.dialogs import get_string
    return get_string("File Password", "Enter password:")


def exporter():
    """Exports a file.
    - First chooses a path (user)
    - Requests a password (user),
    - Then gets all the information (software),
    - and constructs the file (ScanFileBuilder)
    - Saves the file (OS)

    Returns:
        str: the path to the saved file.
    """
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
    network_entities = [str(x).encode() for x in NetworkStorage()]
    builder.add_many(network_entities)

    from register import Register
    scan_history = [
        int(timestamp).to_bytes(4, byteorder='big') + str(name).encode() + int(duration).to_bytes(3, byteorder='big')
        for (name, timestamp, duration) in Register().get_history()
    ]
    builder.add_many(scan_history)

    builder.set_password(get_password())
    builder.write_to(filename)
    print("Done writing")
    return filename


def importer():
    """Imports a `.scan` file.
    - First selects the path (user)
    - Then gets the password (user)
    - Deconstructs the file (ScanFileBuilder)
    - And parses it into human-readable (code)
    - Finally bundles it all together and returns, to be displayed on the GUI

    Returns:
        str: the textual decoded parsed content of the file.
    """
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
    scan_id = result["scan_id"]
    same_network = scan_id == get_scan_id()
    same_network_message = "\nYou're currently in the same connection (computer, interface, network) as the scan file!" if same_network else "\n"

    scan_id = parse_scan_id(scan_id)

    entities = result["network_entities"]
    entities = '\n'.join(entities)

    history = result["scan_history"]
    from datetime import datetime

    def format_timestamp(t: int) -> str:
        """Formats a timestamp (Unix; seconds since 00:00:00 UTC on 1 January 1970 epoch) to YYYY-MM-DD HH:MM:SS.

        Args:
            t (int): the timestamp.

        Returns:
            str: the formatted date and time.
        """
        return datetime.fromtimestamp(t).strftime('%Y-%m-%d %H:%M:%S')

    def format_duration(t: int) -> str:
        """Formats a duration (seconds) to "34[s]" (example) or "indefinitely" for negative values.

        Args:
            t (int): the duration in seconds.

        Returns:
            str: the human-readable meaning.
        """
        return f'for {t}[s]' if t > -1 else f'indefinitely'
    history = [format_timestamp(timestamp) + f' {name} {format_duration(duration)}.' for (timestamp, name, duration) in history if name != '']
    history = '\n'.join(history)

    return f"""{scan_id}{same_network_message}\n\n{entities}\n\n{history}"""


def encrypt(message: bytes, password: str) -> bytes:
    """Interfaces with the encryption of `files_cryptography`.

    Args:
        message (bytes): the message to encode.
        password (str): the key to use.

    Returns:
        bytes: the encoded message.
    """
    return files_cryptography.password_encrypt(message, password)


def decrypt(token: bytes, password: str) -> bytes:
    """Interfaces with the decryption of `files_cryptograph`.

    Args:
        token (bytes): the message to decode.
        password (str): the key to use.

    Returns:
        bytes: the decoded message.
    """
    return files_cryptography.password_decrypt(token, password)


class ScanFileBuilder:
    HEADER = b"SHZILSCAN"
    SEP = b"\n"
    COMMA = b","

    def __init__(self):
        """Initialises a ScanFileBuilder,
        with just the HEADER in a parts list,
        and the password set to None.
        """
        self.parts = [self.HEADER]
        self.password = None

    def add(self, part: bytes):
        """adds a part to the part list.

        Args:
            part (bytes): the part to add.
        """
        self.parts.append(part)

    def add_many(self, parts: Iterable[bytes]):
        """adds a few parts to the part list.

        Args:
            parts (Iterable[bytes]): the parts to extend.
        """
        self.parts.append(self.COMMA.join(parts))

    def write_to(self, path: str):
        """Writes the file contents to the part, encrypted.

        Args:
            path (str): the path to save the file to.
        """
        assert self.password is not None
        with open(path, "xb") as f:
            content = self.SEP.join(self.parts)
            content = encrypt(content, self.password) if self.password != '' else content
            f.write(content)

    def set_password(self, password: str):
        """sets the password.

        Args:
            password (str): the password.
        """
        self.password = password

    def parse(self, path: str) -> dict[str, str|list]:
        """decrypts and parses a `.scan` file.

        Args:
            path (str): the path from which to read the file.

        Raises:
            ValueError: if the password is wrong.
            ValueError: if the file is invalid and the extension is wrong.
            ValueError: if the file is invalid or the password is wrong.
            ValueError: if the file has more parts then it should.

        Returns:
            dict[str, str|list]: the parsed file.
        """
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
            def _decode_bytes(b: bytes) -> str:
                """Attempts to decode bytes using utf-8,
                and if it fails (UnicodeDecodeError),
                returns them as HEX.

                Args:
                    b (bytes): the bytes to decode.

                Returns:
                    str: the decoded bytes.
                """
                try:
                    return b.decode('utf-8')
                except UnicodeDecodeError:
                    return b.hex()
            raise ValueError("The file has more content than expected: " + _decode_bytes(rest))

        return {
            "scan_id": scan_id.decode(),
            "network_entities": [x.decode() for x in entities.split(self.COMMA)],
            "scan_history": [(x[:4], x[4:-3].decode(), x[:-3]) for x in history.split(self.COMMA)]
        }


if __name__ == '__main__':
    print("This module is used for saving scans as files,")
    print("and opening previously saved scans.")
