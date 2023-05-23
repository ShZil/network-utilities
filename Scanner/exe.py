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
    import win32api
    import re
kivy.require('2.1.0')

from NetworkStorage import *
from register import Register
from PacketSniffer import PacketSniffer
from threading import Thread, enumerate as enumerate_threads
from SimpleScan import simple_scan
from CommandLineStyle import cmdcolor, cmdtitle, remove_scapy_warnings
from scans.PublicAddress import public_address_action
from scans.ARP import scan_ARP, scan_ARP_continuous
from scans.ICMP import scan_ICMP, scan_ICMP_continuous
from scans.TCP import port_scan_TCP
from scans.TraceRouter import traceroute
from scans.Discovery import DeviceDiscoveryListener, reveal_myself
from analyses.OS_ID import operating_system_fingerprinting
from analyses.DeviceProfile import device_profile
from analyses.LogPackets import log_packets
from analyses.VendorMapping import vendor_mapping
from time import sleep
import os
import sys
from gui.KivyFonts import add_fonts
from gui.StartApp import start_tk, start_kivy
from gui.dialogs import PopupManager, get_string


def keep_resolving_storage():
    def _resolver():
        from globalstuff import terminator
        sleep(7)
        while not terminator.is_set():
            sleep(5)
            NetworkStorage()._resolve()
            # print(len(NetworkStorage()), G.copy())
            from gui.Screens.KnowScreen import update_know_screen
            update_know_screen(NetworkStorage())
            from gui.Diagrams import Diagrams
            Diagrams().update()
        sys.exit()

    _resolver.__name__ = 'IntervalThread'
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
    r["TCP Ports"] = port_scan_TCP
    r["OS-ID"] = operating_system_fingerprinting, True
    r["Public Address"] = public_address_action
    r["Traceroute"] = lambda: traceroute(get_string("IP Destination", "Select the IP address:"))
    r["Log Packets"] = log_packets
    r["Device Profile"] = device_profile
    r["Reveal Myself"] = reveal_myself
    r["Vendor Mapping"] = vendor_mapping


def main():
    print("Loading...")
    remove_scapy_warnings()
    os.system('cls')
    cmdcolor("0A")
    print("Attempting to connect to an network-card interface...")
    ipconfig()
    cmdtitle(
        "Network Scanner - ",
        ipconfig()["Interface"],
        " at ",
        ipconfig()["IPv4 Address"]
    )
    from testing.tests import test
    test()

    NetworkStorage()
    ipconfig.cache["All Possible Addresses"] = get_all_possible_addresses()
    from NetworkStorage import router, here
    from globalstuff import G
    NetworkStorage().add(router, here)
    G.add_node(router)

    register_scans()

    # GUI initialisation
    add_fonts()
    PopupManager()  # starts the popup thread
    DeviceDiscoveryListener()  # starts the discovery thread
    
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
        with open('error log.txt', 'a', encoding='utf-8') as f:
            f.write(f'An exception occurred - {err}\n{datetime.now()}')
        raise
