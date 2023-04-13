import os
from import_handler import ImportDefence
from time import sleep
with ImportDefence():
    from scapy.config import conf
    from scapy.sendrecv import sr1
    from scapy.layers.inet import IP

    from pygments import highlight, lexers, formatters
    from json import dumps

def cmdtitle(*s, sep=''):
    os.system(f'title {sep.join(s)}')


def cmdcolor(c):
    os.system(f'color {str(c).zfill(2)}')


def print_dict(x: dict) -> None:
    """Prints a python dictionary using JSON syntax and console colouring.

    Args:
        x (dict): the dictionary to print.
    """
    formatted_json = dumps(x, sort_keys=False, indent=4)
    colorful_json = highlight(
        formatted_json,
        lexers.JsonLexer(),
        formatters.TerminalFormatter()
    )
    print(colorful_json)


def remove_scapy_warnings():
    """Removes the "MAC address not found, using broadcast" warnings thrown by scapy.
    These warnings occur when a packet is sent to an IP (layer 3) address, without an Ethernet (layer 2) MAC address,
    and such an address cannot be found using ARP. Scapy thus uses the broadcast MAC instead.
    """
    conf.warning_threshold = 1_000_000  # Time between warnings of the same source should be infinite (many seconds).
    for _ in range(3):
        try:
            sr1(IP(dst="255.255.255.255"), verbose=0, timeout=0.001)
        except PermissionError:
            input("Failure to send packets <IP dst=broadcast>.\nIf you're sure you've got everything correct, press any key to continue. . .")
            return
        sleep(0.01)


if __name__ == '__main__':
    print("This module is responsible for styling the CMD or console.")
    print("It can change the title of the CMD window,")
    print("and the colour of the text.")
    print("A logical addition is the remover of scapy warnings, since all they do is clutter the CMD.")
    print("Another logical addition is `print_dict`, that turns a boring dictionary into a colourful JSON on the CMD.")
