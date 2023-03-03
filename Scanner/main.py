from import_handler import ImportDefence
with ImportDefence():
    import os
    from typing import Callable
    import requests
    import ipaddress

    from util import *
    from ip_handler import *
    from NetworkStorage import NetworkStorage
    from ipconfig import ipconfig
    
    from scans.ARP import scan_ARP
    from scans.ICMP import scan_ICMP, scan_ICMP_continuous
    from scans.TCP import scan_TCP

    from scapy.config import conf
    from scapy.sendrecv import sr1
    from scapy.all import IP


os.system('cls')
print("All imports were successful.")

__author__ = 'Shaked Dan Zilberman'

lookup = None


def do_simple_scan(scan, all_possible_addresses, *, results=True, repeats=3):
    """This is a wrapper for simple* scans, like ARP or ICMP.

    (*) Simple means they are standardised:
    [X] Have been @threadify-ied.
    [X] Get list[str] of IPv4 addresses as input (post-threadify).
    [X] Output list[bool] indicating online-ness of the addresses (index-correlated) (post-threadify).

    Note: index-correlatedness, lists as input, and lists as output are handled by @threadify.
    The requirements for the base function are just that it's of the form: `scan: str (IPv4 address) -> bool (connectivity)`.


    Args:
        scan (function): a @threadify-ied method from list[str] all_possible_addresses -> list[bool] online.
        all_possible_addresses (list[str]): a list of IPv4 to test connectivity to.
        results (bool, optional): Decides whether to print the results. Defaults to True.
        repeats (int, optional): How many times should the full-range of addresses be scanned? Defaults to 3.

    Returns:
        list[str]: the addresses which replied, at least once, to the scan.
    """
    if repeats < 1: return []

    # Parsing the title & protocol.
    title = scan.__name__
    protocol = "".join(char for char in title if char.isupper())

    # Define a <lambda> that returns a list[str] of connectable addresses.
    get_new = lambda: [address for address, online in zip(all_possible_addresses, scan(all_possible_addresses)) if online]

    # Call it `repeats` times and unite all results.
    connectable_addresses = set()
    for _ in range(repeats):
        connectable_addresses = connectable_addresses.union(get_new())

    # Turn it into a sorted list (just for convenience, order doesn't matter).
    connectable_addresses = sorted(connectable_addresses, key=lambda x: int(''.join(x.split('.'))))

    # Print if asked
    if results:
        print("There are", len(connectable_addresses), protocol, "connectable addresses in this subnet:")
        print('    ' + '\n    '.join(connectable_addresses))
    
    return connectable_addresses


def standardise_simple_scans(scans: list[tuple[Callable, int]]) -> list[Callable]:
    scans = [scan if isinstance(scan, tuple) else (scan, 1) for scan in scans]
    scans = [scan for scan in scans if scan[1] > 0]
    
    def does_simple_scan(scan):
        scan, repeats = scan
        return (lambda: do_simple_scan(scan, ipconfig()["All Possible Addresses"], repeats=repeats))
    lambdas = [does_simple_scan(scan) for scan in scans]

    for scan, method in zip(scans, lambdas):
        prefix = f"{scan[1]} × " if scan[1] > 1 else ""
        method.__name__, method.__doc__ = prefix + scan[0].__name__, prefix + scan[0].__doc__
    return lambdas


def title(*s, sep=''):
    os.system(f'title {sep.join(s)}')


@one_cache
def get_public_ip():
    from NetworkStorage import nothing, NetworkStorage, LockedNetworkEntity
    ip = requests.get('https://api.ipify.org').text
    ipv6 = requests.get('https://api64.ipify.org').text
    ipv6 = ipv6 if ipv6 != ip else nothing.ipv6
    try:
        outside = LockedNetworkEntity(mac=nothing.mac, ip=ip, ipv6=ipv6, name="Public Address")
    except ValueError:  # api64.ipify.org might not return the IPv6, and instead say "gateway timeout"
        outside = LockedNetworkEntity(mac=nothing.mac, ip=ip, ipv6=nothing.ipv6, name="Public Address")
    NetworkStorage().special_add(outside)


def remove_scapy_warnings():
    """Removes the "MAC address not found, using broadcast" warnings thrown by scapy.
    These warnings occur when a packet is sent to an IP (layer 3) address, without an Ethernet (layer 2) MAC address,
    and such an address cannot be found using ARP. Scapy thus uses the broadcast MAC instead.
    """
    conf.warning_threshold = 1_000_000  # Time between warnings of the same source should be infinite (many seconds).
    for _ in range(3):
        sr1(IP(dst="255.255.255.255"), verbose=0, timeout=0.001)
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
    mask = sum(bin(int(x)).count('1') for x in mask.split('.')).to_bytes(1, 'big')

    physical = here.mac
    physical = int(physical.replace('-', ''), 16).to_bytes(6, 'big')

    return base64.b64encode(host + b'\x40' + iface + b'\x40' + gateway + mask + physical).decode()


def parse_scan_id():
    # Reverse the logic from `get_scan_id`
    pass


def main():
    remove_scapy_warnings()

    ipconfig()
    title("ShZil Network Scanner - ", ipconfig()["Interface"], " at ", ipconfig()["IPv4 Address"])

    from testing.tests import test
    test()

    print_dict(ipconfig())
    
    global lookup
    lookup = NetworkStorage()

    ipconfig.cache["All Possible Addresses"] = all_possible_addresses = get_all_possible_addresses()
    print("Subnet Size:", len(all_possible_addresses), "possible addresses.")
    
    simple_scans = standardise_simple_scans([
        (scan_ICMP, 0),
        (scan_ARP, 0)
    ])


    def add_to_lookup():
        lookup.add(ip="255.255.255.255")
        from NetworkStorage import router, here
        lookup.add(router, here)
    

    def do_TCP():
        from NetworkStorage import router
        print(f"Open TCP ports in {router}:")
        with JustifyPrinting():
            for port, res in scan_TCP(router.ip, repeats=3).items():
                if res: print(port)
    

    def user_confirmation(): input("Commencing next scan. Press [Enter] to continue . . .")
    def continuous_ICMP(): scan_ICMP_continuous(lookup['ip'], ipconfig()["All Possible Addresses"], compactness=2)
    def print_scanID(): print("ScanID:", get_scan_id())

    actions = [
        add_to_lookup,
        *simple_scans,
        print_scanID,
        get_public_ip,
        lookup.print,
        # user_confirmation,
        # do_TCP,
        user_confirmation,
        continuous_ICMP
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
