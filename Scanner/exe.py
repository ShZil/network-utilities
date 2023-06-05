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
from scans.Discovery import DeviceDiscoveryListener, reveal_myself, show_all_revealed
from analyses.OS_ID import operating_system_fingerprinting
from analyses.DeviceProfile import device_profile
from analyses.LogPackets import log_packets
from analyses.VendorMapping import vendor_mapping
from RecommendProbabilities import construct_graph, render_graph
from time import sleep
import os
import sys
from gui.KivyFonts import add_fonts
from gui.StartApp import start_tk, start_kivy
from gui.dialogs import PopupManager, get_string


def keep_resolving_storage():
    """This function allocates a thread for `IntervalThread`,
    which executes a few essential actions in a set time interval, repeating.
    """
    def _resolver():
        """This function maintains a while loop,
        that executes the following tasks in the background every 5 seconds:
        * Resolving `NetworkStorage` (i.e. putting everything from the internal queue into internal `data`)
        * Updates the Know Screen with data from `NetworkStorage`.
        * Updates the diagrams.

        Also, after `terminator` is set, it calls `sys.exit()` to attempt to force closing.
        """
        from globalstuff import terminator
        sleep(7)
        from gui.ScanClasses import update_recommendation
        update_recommendation()
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
    """Registers the scans & analyses into `Register()` dictionary."""
    r = Register()
    r["ICMP Sweep"] = simple_scan(scan_ICMP, 3)
    r["ARP Sweep"] = simple_scan(scan_ARP, 3)
    r["Live ICMP"] = lambda: scan_ICMP_continuous(
        NetworkStorage()['ip'],
        ipconfig()["All Possible Addresses"],
        compactness=0
    ), True
    r["Live ARP"] = scan_ARP_continuous, True
    r["TCP Ports"] = port_scan_TCP
    r["OS-ID"] = operating_system_fingerprinting, True
    r["Public Address"] = public_address_action
    r["Trace Route"] = lambda: traceroute(get_string("IP Destination", "Select the IP address:"))
    r["Log Packets"] = log_packets
    r["Device Profile"] = device_profile
    r["Reveal Myself"] = reveal_myself
    r["Vendor Mapping"] = vendor_mapping
    r["All Revealed"] = show_all_revealed
    r["Recommended Scan Algorithm"] = render_graph


def main():
    """The entry point of the software.

    Setup and execution:
    - removes scapy warnings
    - clears the console
    - sets console color to green with black background. Programming-y
    - connects to a network-card interface and caches `ipconfig` results
    - changes the console title
    - runs unit tests
    - initialises `NetworkStorage`
    - caches all possible network addresses
    - adds the `router` and `here` entities to the NetworkStorage (which is why you see a line between two points before running a scan)
    - adds the `router` entity to the G (Graph) (which is why, before updating, you see a single dot)
    - registers the scans
    - uploads the fonts to the GUI
    - initialises `PopupManager`
    - initialises the Disocvery Listener thread
    - initialises the `PacketSniffer` thread
    - initialises the `IntervalThread`
    - starts the Kivy GUI
    - starts the TK diagram (blocking)
    """
    print("Loading...")
    remove_scapy_warnings()
    os.system('cls')
    cmdcolor("0A")
    print("Attempting to connect to a network-card interface...")
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

    # Recommend Probabilities
    construct_graph()

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
