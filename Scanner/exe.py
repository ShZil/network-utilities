__author__ = 'Shaked Dan Zilberman'

from import_handler import ImportDefence
with ImportDefence():
    import requests
    import ipaddress
    import scapy
    import networkx
    import numpy
    import scipy
    import PyQt5
    import kivy
    import tkinter
    import markdown

from main import *
from util import *
from gui import *
from NetworkStorage import *
from register import Register
from PacketSniffer import PacketSniffer
from globalstuff import *
from threading import Thread, enumerate as enumerate_threads
from SimpleScan import simple_scan
from CommandLineStyle import cmdcolor, cmdtitle
from scans.PublicAddress import public_address_action
from scans.OS_ID import operating_system_fingerprinting
from scans.ARP import scan_ARP, scan_ARP_continuous
from scans.ICMP import scan_ICMP, scan_ICMP_continuous
from scans.TCP import scan_TCP


def keep_resolving_storage():
    def _resolver():
        from gui import terminator
        sleep(7)
        while not terminator.is_set():
            sleep(5)
            NetworkStorage()._resolve()
            # print(len(NetworkStorage()), G.copy())
            from gui import update_know_screen, diagram
            update_know_screen(NetworkStorage())
            diagram.renew(G)

    _resolver.__name__ = '5-second interval repeat'
    Thread(target=_resolver).start()


def register_scans():
    """Registers the scans into `Register()` dictionary."""
    r = Register()
    r["ICMP Sweep"] = simple_scan(scan_ICMP, 3)
    r["ARP Sweep"] = simple_scan(scan_ARP, 3)
    r["Live ICMP"] = lambda: scan_ICMP_continuous(
        NetworkStorage()['ip'],
        ipconfig()["All Possible Addresses"],
        compactness=2
    ), True
    r["Live ARP"] = scan_ARP_continuous, True
    r["OS-ID"] = operating_system_fingerprinting, True
    r["Public Address"] = public_address_action


def main():
    print("Loading...")
    remove_scapy_warnings()
    os.system('cls')
    cmdcolor("0A")
    print("Attempting to connect to an network-card interface...")
    ipconfig()
    cmdtitle(
        "ShZil Network Scanner - ",
        ipconfig()["Interface"],
        " at ",
        ipconfig()["IPv4 Address"]
    )
    from testing.tests import test
    test()

    NetworkStorage()
    ipconfig.cache["All Possible Addresses"] = get_all_possible_addresses()
    from NetworkStorage import router, here
    NetworkStorage().add(router, here)

    register_scans()

    # GUI initialisation
    add_font()
    prestart()

    # Start tk (on main thread) and kivy (on different thread) and
    # `NetworkStorage()._resolve` (on a third thread)
    PacketSniffer()
    keep_resolving_storage()
    Thread(target=start_kivy).start()
    start_tk()


if __name__ == '__main__':
    # sys.stdout = sys.stderr = open(os.devnull, "w")
    try:
        main()
    except Exception as err:
        from datetime import datetime
        with open('error log.txt', 'w') as f:
            f.write(f'An exception occurred - {err}\n{datetime.now()}')
        raise
