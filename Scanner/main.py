from import_handler import ImportDefence
with ImportDefence():
    import os
    from subprocess import CalledProcessError, check_output as read_command
    from typing import Callable

    from util import *
    from ip_handler import *
    from NetworkStorage import NetworkStorage
    from colors import Colors
    from ipconfig import ipconfig

    from scapy.sendrecv import sr1, sendp, AsyncSniffer
    from scapy.layers.inet import IP, ICMP
    from scapy.layers.l2 import Ether, ARP
    from scapy.config import conf

    from socket import gethostbyaddr as hostify_base
    from socket import herror as hostify_error1
    from socket import gaierror as hostify_error2


os.system('cls')
print("All imports were successful.")

__author__ = 'Shaked Dan Zilberman'

# A range for the scanned ports.
PORT_RANGE = range(0, 1024)
lookup = None


# ************ The subprocess windows open and disturb users (aka me) / Prints the errors into the console which is annoying.
# Potential fix: https://stackoverflow.com/questions/1813872/running-a-process-in-pythonw-with-popen-without-a-console
# or https://stackoverflow.com/a/55758810
@memorise
def hostify(address: str):
    """This function turns an IPv4 address to a host name using one of these methods:
    1. Calling `>nslookup` with that address. If that fails,
    2. Using `socket.gethostbyaddr` function. If that fails,
    3. Returns "Unknown" since all the methods failed.

    Args:
        address (str): the IPv4 address to turn into a host.

    Returns:
        str: the host name.
    """
    host = "Unknown"

    def use_hostify_base(address):
        try:
            return hostify_base(address)[0]
        except (hostify_error1, hostify_error2):
            return "Unknown"

    # First method -> nslookup
    # If first method failed, second method -> socket.gethostbyaddr
    try:
        with NoPrinting():
            lines = read_command(['nslookup', address]).decode(encoding='utf-8', errors='ignore').split('\n')
        for line in lines:
            if line.strip().startswith('Name:'):
                host = line[len("Name:"):].strip()
                break
        else:
            host = use_hostify_base(address)
    except CalledProcessError:
        host = use_hostify_base(address)
    return host


hostify_sync = threadify(hostify)


def get_all_possible_addresses() -> list[str]:
    """This method calculates all the possible IPv4 addresses in the current subnet,
    according to this device's IP address and the Subnet Mask, both from `ipconfig()`.

    Returns:
        list[str]: a list of IPv4 addresses, that are all the possible ones in the current network.
    """    
    this_device_ip = ipconfig()["IPv4 Address"]
    subnet_mask = ipconfig()["Subnet Mask"]

    this_device_ip, subnet_mask = bitify(this_device_ip), bitify(subnet_mask)
    unique, mutual = subnet_mask.count('0'), subnet_mask.count('1')

    base = this_device_ip[:mutual]
    binary = lambda number: bin(number)[2:].zfill(unique)

    # All possible addresses in binary look like `[mutual part to all in network][special identifier]`,
    # i.e. base + binary representation of i (where i ranges from (0) to (2 ^ unique))
    return [unbitify(base + binary(i)) for i in range(2 ** unique)]


def can_connect_ICMP_base(address: str) -> bool:
    """This function tests whether it's possible to connect to another IPv4 address `address`,
    using an Internet Control Message Protocol (ICMP) ping request.
    If the address given is localhost, `return False`.

    Args:
        address (str): the IPv4 address to try pinging.

    Returns:
        bool: a boolean indicating whether the echo ping had been successfully sent, and a response was received.
    """
    if (address == ipconfig()["IPv4 Address"]): return False
    packet = IP(dst=address) / ICMP()
    response = sr1(packet, verbose=0, timeout=1)
    if response is not None:
        # print(response[IP].show())
        if response[ICMP].type == 0:
            lookup.add(ip=response[IP].src)
            return True
    return False

can_connect_ICMP_silent = threadify(can_connect_ICMP_base, silent=True)
can_connect_ICMP_base.options = {"format": barstyle("Dot Fill")}
can_connect_ICMP = threadify(can_connect_ICMP_base)


def can_connect_ARP(addresses: list[str]) -> list[str]:
    """This function tests whether it's possible to connect to other IPv4 addresses `addresses`,
    using Address Resolution Protocol (ARP) who-has requests.

    Args:
        addresses (list[str]): the IPv4 addresses to try connecting to.

    Returns:
        list[str]: the addresses that sent an is-at response.
    """
    results = []
    appender = lambda x: results.append((x[ARP].hwsrc, x[ARP].psrc))
    filter_is_at_ARP = lambda x: ARP in x and x[ARP].op == 2 and x[ARP].psrc != ipconfig()["IPv4 Address"]
    sniffer = AsyncSniffer(prn=appender, lfilter=filter_is_at_ARP, store=False)
    sniffer.start()

    send_ARP = lambda packet: sendp(packet, verbose=0)
    send_ARP.__name__ = "can_connect_ARP_base"
    packets = [Ether() / ARP(pdst=address) for address in addresses]
    threadify(send_ARP)(packets)

    from scapy.error import Scapy_Exception as NoNpcap
    try:
        sniffer.stop()
    except NoNpcap as e:
        if e.args[0] == "Unsupported (offline or unsupported socket)":
            print("Npcap / WinPcap aren't installed. Please install either one lol")
            sys.exit(1)
        else:
            raise
    for result in results:
        lookup.add(mac=result[0], ip=result[1])
    return [result[1] for result in results]


def calculate_opacity(connections: list[bool]) -> float:
    """This function calculates the opacity of a given connection list (a list of booleans indicating some contacting attempts' successes),
    according to a probabilistic formula derived in an attached TXT file.

    Args:
        connections (list[bool]): a list of contact attempts' successes, taking the form of `[...True, True, False, True, False]`

    Returns:
        float: a value between `0.0` (disconnected) and `1.0` (connected) representing certainty that the device is still connected (a.k.a its opacity).
    """
    
    # #   │++                             │+++++++++ 
    # #   │  ++                           │         +++++  
    # #   │    ++                         │              ++
    # #   │      ++                       │                ++ 
    # #   │        ++                =>   │                  + 
    # #   │          ++                   │                   + 
    # #   │            ++                 │                    +
    # #   │              ++               │                    + 
    # #   │                ++             │                     +
    # #   │                  ++           │                     + 
    # # ──┼─────────────────────────    ──┼────────────────────────
    # #   │                               │

    # GONE_AFTER: int = 11

    # if len(connections) == 0: return 0.0
    # if not any(connections): return 0.0
    # distance_to_last = list(reversed(connections)).index(True)
    # # Change this function? (see art above)
    # opacity = 1.0 - distance_to_last / GONE_AFTER
    # if opacity < 0: return 0.0
    # # Maybe calculate the average amount of disconnected time for devices? And not just choose some random numbers?
    # return opacity
    if len(connections) == 0: return 1.0
    if not any(connections): return 0.0
    n = list(reversed(connections)).index(True)
    a = connections.count(True) / len(connections)
    return a ** n


def continuous_ICMP_scan(addresses, all_possible_addresses, parallel_device_discovery=True, compactness=0):
    # compactness=0 -> "255.255.255.255 (Smartphone-Galaxy-S90-5G) █████ █    ███████ █  ███ ████┅  [█]".
    # compactness=1 -> "255.255.255.255 (Smartphone-Galaxy-S90-5G) [█]".
    # compactness=2 -> "<ff:ff:ff:ff:ff:ff | 255.255.255.255 | Smartphone-Galaxy-S90-5G>" (text colour changes depending on opacity).
    # otherwise -> "255.255.255.255 (Smartphone-Galaxy-S90-5G)" (text colour changes depending on opacity).
    if not isinstance(addresses, list): addresses = list(addresses)
    table = {address: [] for address in addresses}
    waiting = Queue()

    if parallel_device_discovery:
        # How many threads should be dedicated to the detection of new devices?
        # The iteration shifts in different threads by `shifting = thread_index * 71 mod 255`, to ensure efficiency.
        # Range of values: 1 to 18 (inclusive).
        # Optimal values: 18, 6, 3, 2, 1
        SCANNER_THREADS = 18

        def new_devices(order: int):
            all_addresses = shift(all_possible_addresses, 71*order)
            while True:
                for address in all_addresses:
                    if address in table.keys(): continue
                    if address in waiting.queue: continue
                    if can_connect_ICMP_base(address):
                        waiting.put(address)

        for i in range(SCANNER_THREADS):
            Thread(target=new_devices, args=(i, )).start()
    
    while True:
        sleep(1.1)  # Change this to global setting
        while not waiting.empty():
            address = waiting.get()
            if address not in addresses:
                addresses.append(address)
                print("Adding address", address)
        for address, online in zip(addresses, can_connect_ICMP(addresses)):
            if address not in table:
                table[address] = []
            table[address].append(online)
            if len(table[address]) > 60:
                table[address] = table[address][-60:]
        hostify_sync(list(table.keys()))
        os.system("cls")
        print("Connection testing (ICMP ping) to", subnet_address_range(ipconfig()["Subnet Mask"], ipconfig()["IPv4 Address"]) + "\n")
        
        sorted_table = sorted(table.keys(), key=lambda x: int(''.join(x.split('.'))))
        if compactness == 0:

            with InstantPrinting():
                example_length = len("255.255.255.255 (Smartphone-Galaxy-S90-5G)")
                bar_length = os.get_terminal_size().columns - example_length - len(":  ") - len("┅  [ ]")
                for address in sorted_table:
                    print(
                        f"{address} ({hostify(address)}): ".rjust(example_length),
                        (''.join(['█' if x else ' ' for x in table[address][-bar_length:]]) + "┅ ").rjust(bar_length),
                        f"[{render_opacity(100 * calculate_opacity(table[address]))}]"
                    )
            print()

        elif compactness == 1:

            with TablePrinting():
                for address in sorted_table:
                    print(
                        address,
                        f"({hostify(address)})",
                        f"[{render_opacity(100 * calculate_opacity(table[address]))}]"
                    )
        
        elif compactness == 2:
            with JustifyPrinting():
                opacities = [Colors.BLACK, Colors.DARK_GRAY, Colors.LIGHT_GRAY, Colors.LIGHT_WHITE]
                data = lookup.organise('ip')
                for address in sorted_table:
                    opacity = calculate_opacity(table[address])
                    index = floor(opacity * (len(opacities) - 1))
                    if index == 0: continue
                    color = opacities[index]
                    try:
                        print(f"{color}{data[address]}{Colors.END}  ")
                    except KeyError:
                        print(f"{color}{address} ({hostify(address)}){Colors.END}  ")
            
        else:

            with AutoLinebreaks():
                opacities = [Colors.BLACK, Colors.DARK_GRAY, Colors.LIGHT_GRAY, Colors.LIGHT_WHITE]
                for address in sorted_table:
                    opacity = calculate_opacity(table[address])
                    index = floor(opacity * (len(opacities) - 1))
                    if index == 0: continue
                    color = opacities[index]
                    print(f"{color}{address} ({hostify(address)}){Colors.END}  ")


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


def main():
    ipconfig()

    from testing.tests import test
    test()

    # print_dict(ipconfig())
    
    global lookup
    lookup = NetworkStorage()

    ipconfig.cache["All Possible Addresses"] = all_possible_addresses = get_all_possible_addresses()
    print("Subnet Size:", len(all_possible_addresses), "possible addresses.")

    conf.warning_threshold = 100000  # Time between warnings of the same source should be infinite (100000 seconds).
    
    simple_scans = standardise_simple_scans([
        (can_connect_ICMP, 0),
        (can_connect_ARP, 1)
    ])

    lookup.print.__func__.__name__ = "print_lookup"
    def add_broadcast_to_lookup(): lookup.add(ip="255.255.255.255")
    def user_confirmation(): input("Commencing continuous ICMP scan. Press [Enter] to continue . . .")
    def continuous_ICMP(): continuous_ICMP_scan(lookup['ip'], ipconfig()["All Possible Addresses"], compactness=2)

    nameof = lambda action: action.__doc__ if action.__doc__ and len(action.__doc__) < 100 else action.__name__

    actions = [
        add_broadcast_to_lookup,
        *simple_scans,
        lookup.print,
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
