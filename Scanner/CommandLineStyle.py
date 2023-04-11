import os
from import_handler import ImportDefence
from time import sleep
with ImportDefence():
    from scapy.config import conf
    from scapy.sendrecv import sr1
    from scapy.layers.inet import IP


def cmdtitle(*s, sep=''):
    os.system(f'title {sep.join(s)}')


def cmdcolor(c):
    os.system(f'color {str(c).zfill(2)}')


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
    print("And the colour of the text,")
    print("And a logical addition is the remover of scapy warnings, since all they do is clutter the CMD.")
