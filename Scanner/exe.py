__author__ = 'Shaked Dan Zilberman'

from import_handler import ImportDefence
with ImportDefence():
    import requests
    import ipaddress
    import scapy
    import networkx, numpy, scipy
    import PyQt5, kivy, tkinter
    import markdown

from main import *
from util import *
from gui import *
from NetworkStorage import *
from register import Register
from globalstuff import *
from threading import Thread


def update_diagrams():
    update_kivy_diagram(0, 0)
    if diagram is not None: diagram.renew(G)


def keep_resolving_storage():
    from gui import terminator
    def _resolver():
        sleep(7)
        while not terminator.is_set():
            sleep(5)
            NetworkStorage()._resolve()
            from gui import diagram
            if diagram is not None:
                if diagram.renew(G):
                    update_kivy_diagram()
    
    Thread(target=_resolver).start()


def register_scans():
    """Registers the scans into `Register()` dictionary."""
    r = Register()
    r["ICMP Sweep"] = simple_scan(scan_ICMP, 3)
    r["ARP Sweep"] = simple_scan(scan_ARP, 3)
    r["Live ICMP"] = lambda: scan_ICMP_continuous(lookup['ip'], ipconfig()["All Possible Addresses"], compactness=2)


def main():
    global lookup
    print("Loading...")
    with NoPrinting():
        remove_scapy_warnings()
    os.system('cls')
    cmdcolor("0A")
    print("Attempting to connect to an network-card interface...")
    ipconfig()
    cmdtitle("ShZil Network Scanner - ", ipconfig()["Interface"], " at ", ipconfig()["IPv4 Address"])
    from testing.tests import test
    test()
    cmdcolor("00")
    
    lookup = NetworkStorage()
    ipconfig.cache["All Possible Addresses"] = get_all_possible_addresses()
    lookup.add(ip="255.255.255.255")
    lookup.add(router, here)

    register_scans()

    # GUI initialisation
    add_font()
    prestart()

    # Start tk (on main thread) and kivy (on different thread) and `NetworkStorage()._resolve` (on a third thread)
    keep_resolving_storage()
    Thread(target=start_kivy).start()
    start_tk()


if __name__ == '__main__':
    try:
        main()
    except Exception as err:
        with open('error log.txt', 'w') as f:
            f.write(f'An exception occurred - {err}')
        raise
