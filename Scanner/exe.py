__author__ = 'Shaked Dan Zilberman'

from import_handler import ImportDefence
from main import *
from util import *
from gui import *
from NetworkStorage import *
with ImportDefence():
    import requests
    import ipaddress
    import scapy
    import kivy
    import networkx
    import tkinter
    from threading import Thread
    import numpy, scipy
    import pywin32
    import PyQt5
    import markdown

lookup = None


def main():
    print("Loading...")
    with NoPrinting():
        remove_scapy_warnings()
    print("Attempting to connect to an network-card interface...")
    ipconfig()
    cmdtitle("ShZil Network Scanner - ", ipconfig()["Interface"], " at ", ipconfig()["IPv4 Address"])
    cmdcolor("0A")
    from testing.tests import test
    test()
    cmdcolor("00")
    
    global lookup
    lookup = NetworkStorage()
    ipconfig.cache["All Possible Addresses"] = get_all_possible_addresses()
    lookup.add(ip="255.255.255.255")
    lookup.add(router, here)


if __name__ == '__main__':
    main()
