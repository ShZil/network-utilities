from import_handler import ImportDefence
with ImportDefence():
    import requests
    import ipaddress

    from scapy.config import conf
    from scapy.sendrecv import sr1
    from scapy.all import IP


from util import *
from ip_handler import *
from NetworkStorage import NetworkStorage
from ipconfig import ipconfig

from scans.ARP import scan_ARP, scan_ARP_continuous
from scans.ICMP import scan_ICMP, scan_ICMP_continuous
from scans.TCP import scan_TCP

import os

# os.system('cls')
# print("All imports were successful.")

__author__ = 'Shaked Dan Zilberman'


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


def main():
    raise NotImplementedError("Use `exe.py` instead.")
    remove_scapy_warnings()

    ipconfig()
    cmdtitle(
        "ShZil Network Scanner - ",
        ipconfig()["Interface"],
        " at ",
        ipconfig()["IPv4 Address"]
    )

    from testing.tests import test
    test()

    print_dict(ipconfig())

    # global lookup
    NetworkStorage()

    ipconfig.cache["All Possible Addresses"] = all_possible_addresses = get_all_possible_addresses()
    print("Subnet Size:", len(all_possible_addresses), "possible addresses.")

    simple_scans = standardise_simple_scans([
        (scan_ICMP, 20),
        (scan_ARP, 20)
    ])

    def add_to_lookup():
        NetworkStorage().add(ip="255.255.255.255")
        from NetworkStorage import router, here
        NetworkStorage().add(router, here)

    def do_TCP():
        from NetworkStorage import router
        print(f"Open TCP ports in {router}:")
        with JustifyPrinting():
            for port, res in scan_TCP(router.ip, repeats=20).items():
                if res:
                    print(port)

    def user_confirmation():
        input("Commencing next scan. Press [Enter] to continue . . .")

    def continuous_ICMP():
        scan_ICMP_continuous(
            NetworkStorage()['ip'],
            ipconfig()["All Possible Addresses"],
            compactness=2
        )

    def print_scanID(): print("ScanID:", get_scan_id())

    actions = [
        add_to_lookup,
        *simple_scans,
        print_scanID,
        get_public_ip,
        NetworkStorage().print,
        # user_confirmation,
        do_TCP,
        user_confirmation,
        # continuous_ICMP
    ]

    with InstantPrinting():
        print("The following actions are queued:")
        for action in actions:
            print("    -", nameof(action))

    for action in actions:
        # print("\n" + nameof(action))
        from time import perf_counter as now
        start = now()
        action()
        end = now()
        with open('times.txt', 'a') as f:
            print(action.__name__, end - start, file=f)


if __name__ == '__main__':
    try:
        main()
    except Exception as err:
        from datetime import datetime
        with open('error log.txt', 'w') as f:
            f.write(f'An exception occurred - {err}\n{datetime.now()}')
        raise
