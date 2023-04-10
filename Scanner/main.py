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


def cmdtitle(*s, sep=''):
    os.system(f'title {sep.join(s)}')


def cmdcolor(c):
    os.system(f'color {str(c).zfill(2)}')


def public_address_action():
    NetworkStorage().add(get_public_ip())


@one_cache
def get_public_ip():
    from NetworkStorage import nothing, NetworkStorage, LockedNetworkEntity
    ip = requests.get('https://api.ipify.org').text
    ipv6 = requests.get('https://api64.ipify.org').text
    ipv6 = ipv6 if ipv6 != ip else nothing.ipv6
    try:
        outside = LockedNetworkEntity(
            mac=nothing.mac,
            ip=ip,
            ipv6=ipv6,
            name="Public Address"
        )
    except ValueError:  # api64.ipify.org might not return the IPv6, and instead say "gateway timeout"
        outside = LockedNetworkEntity(
            mac=nothing.mac,
            ip=ip,
            ipv6=nothing.ipv6,
            name="Public Address"
        )
    NetworkStorage().special_add(outside)
    return outside


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
        sleep(0.01)


@one_cache
def get_scan_id():
    """Generates the current scan's identifier, based on `ipconfig()` info.
    The format:
    [Host Name]@[Interface]@[Gateway IPv4][Subnet Mask][Physical Address]
    All in Base64, with integer values whenever possible.
    """
    from NetworkStorage import router, here
    import base64

    # '@' == (char)64 == '\x40'

    host = here.name.replace('@', '\x02').encode()
    iface = ipconfig()["Interface"].replace('@', '\x02').encode()

    gateway = int(ipaddress.IPv4Address(router.ip)).to_bytes(4, 'big')

    mask = ipconfig()["Subnet Mask"]
    mask = sum(bin(int(x)).count('1')
               for x in mask.split('.')).to_bytes(1, 'big')

    physical = here.mac
    physical = int(physical.replace('-', ''), 16).to_bytes(6, 'big')

    return base64.b64encode(
        host +
        b'\x40' +
        iface +
        b'\x40' +
        gateway +
        mask +
        physical
    ).decode()


def parse_scan_id(scan_id):
    # Reverse the logic from `get_scan_id`
    import base64
    decoded = base64.b64decode(scan_id)
    host, iface, others = decoded.split(b'\x40')

    host = host.decode().replace('\x02', '@')
    iface = iface.decode().replace('\x02', '@')

    gateway, mask, physical = others[:4], others[4:5], others[5:]
    gateway = int.from_bytes(gateway, 'big')
    gateway = str(ipaddress.ip_address(gateway))
    mask = int.from_bytes(mask, 'big')
    physical = hex(int.from_bytes(physical, 'big'))[2:].upper()
    physical = '-'.join(a + b for a, b in zip(physical[::2], physical[1::2]))

    router = f"{gateway}/{mask}"

    return f"Here: {host}, {physical}, via {iface}\nRouter: {router}"


def operating_system_fingerprinting():
    from NetworkStorage import here, SpecialInformation, NetworkEntity
    from PacketSniffer import PacketSniffer

    def _determine_os(packet):
        # do more testing on this
        return "Linux or Android" if packet.ttl <= 64 else "Windows"

    def _fingerprinter():
        while True:
            for packet in PacketSniffer():
                if packet.src == here.ipv4:
                    continue
                entity = NetworkEntity(ip=packet.src)
                if entity in SpecialInformation():
                    continue
                SpecialInformation()[entity, 'OS'] = _determine_os(packet)
            sleep(10)

    Thread(target=_fingerprinter).start()


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
        with open('error log.txt', 'w') as f:
            f.write('An exception occurred - %s' % err)
        raise
