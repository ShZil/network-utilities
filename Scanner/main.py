from import_handler import ImportDefence
with ImportDefence():
    import os
    from typing import Callable

    from util import *
    from ip_handler import *
    from NetworkStorage import NetworkStorage
    from ipconfig import ipconfig
    
    from scans.ARP import scan_ARP
    from scans.ICMP import scan_ICMP, scan_ICMP_continuous
    from scans.TCP import scan_TCP

    from scapy.config import conf


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


def nameof(action):
    """Returns a short description of a function by the following logic:
    If a docstring exists, and its length is less than 100 characters, return the docstring.
    Otherwise, return the function's name.

    Args:
        action (function): the function to be named. Primarily, functions intended to be used as actions.

    Returns:
        str: the name chosen for the function.
    """
    if action.__doc__ and len(action.__doc__) < 100:
        return action.__doc__ 
    else:
        return action.__name__


def main():
    ipconfig()

    from testing.tests import test
    test()

    print_dict(ipconfig())
    
    global lookup
    lookup = NetworkStorage()

    ipconfig.cache["All Possible Addresses"] = all_possible_addresses = get_all_possible_addresses()
    print("Subnet Size:", len(all_possible_addresses), "possible addresses.")

    conf.warning_threshold = 100000  # Time between warnings of the same source should be infinite (100000 seconds).
    
    simple_scans = standardise_simple_scans([
        (scan_ICMP, 0),
        (scan_ARP, 0)
    ])

    lookup.print.__func__.__name__ = "print_lookup"

    # ******* Why does this not get the "broadcast" name???
    def add_to_lookup():
        # lookup.add(ip="255.255.255.255")
        from NetworkStorage import router
        lookup.add(ip=router.ip)
    def do_TCP():
        for address in lookup['ip']:
            print(f"Open TCP ports in {address}:")
            with JustifyPrinting():
                for port, res in scan_TCP(address, repeats=3).items():
                    if res: print(port)
    
    def user_confirmation(): input("Commencing next scan. Press [Enter] to continue . . .")
    def continuous_ICMP(): scan_ICMP_continuous(lookup['ip'], ipconfig()["All Possible Addresses"], compactness=2)

    actions = [
        add_to_lookup,
        *simple_scans,
        lookup.print,
        user_confirmation,
        do_TCP,
        user_confirmation,
        continuous_ICMP
    ]

    with InstantPrinting():
        print("The following actions are queued:")
        for action in actions:
            print("    -", nameof(action))

    
    for action in actions:
        # print("\n" + nameof(action))
        action()


if __name__ == '__main__':
    try:
        main()
    except Exception as err:
        with open('error log.txt', 'w') as f:
            f.write('An exception occurred - %s' % err)
        raise
