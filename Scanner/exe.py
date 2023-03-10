__author__ = 'Shaked Dan Zilberman'

from import_handler import ImportDefence
from main import *
from util import *
from gui import *
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


def main():
    print("Loading...")
    with NoPrinting():
        remove_scapy_warnings()
    print("Attempting to connect to an network-card interface...")
    ipconfig()
    cmdtitle("ShZil Network Scanner - ", ipconfig()["Interface"], " at ", ipconfig()["IPv4 Address"])
    cmdcolor(0)
    


if __name__ == '__main__':
    main()
