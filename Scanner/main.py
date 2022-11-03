from import_handler import ImportDefence
with ImportDefence():
    import os
    from subprocess import CalledProcessError, check_output as read_command
    from util import *
    from ip_handler import *
    from NetworkStorage import NetworkStorage
    from scapy.sendrecv import sr1, sendp, AsyncSniffer
    from scapy.layers.inet import IP, ICMP
    from scapy.layers.l2 import Ether, ARP
    from scapy.config import conf
    from scapy.interfaces import get_working_ifaces

    from socket import gethostbyaddr as hostify_base
    from socket import herror as hostify_error1
    from socket import gaierror as hostify_error2


os.system('cls')
print("All imports were successful.")

__author__ = 'Shaked Dan Zilberman'

# A range for the scanned ports.
PORT_RANGE = range(0, 1024)
lookup = NetworkStorage()


###### IPCONFIG related functions
def read_ipconfig():
    """Read the command `>ipconfig /all` from console and decode it to UTF-8 text.

    Returns:
        list[str]: the command's output as a list of lines
    
    Raises:
        subprocess.CalledProcessError: if subprocess.check_output fails.
    """
    try:
        return read_command(['ipconfig','/all']).decode(encoding='utf-8', errors='ignore').split('\n')
    except CalledProcessError:
        print(">ipconfig /all raised an error.")
        raise


# ************ The subprocess windows open and disturb users (aka me)
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
        lines = read_command(['nslookup','address']).decode(encoding='utf-8', errors='ignore').split('\n')
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


def dictify(text: list[str] | str) -> dict:
    """Turn `text` to a python dictionary.
    The nested dictionary is created according to the following rules:
    - loop over the lines.
    - if the line isn't indented, inistalise a new subdictionary.
    This is a new network interface, e.g. Ethernet, Wireless LAN, Bluetooth; or general info ("Windows IP Configuration").
    - otherwise,
        - if the line is formatted like "key . . . . : value", add this pair to the current active dictionary.
        - otherwise, convert the pair to a (key, list) pair, and add the line's contents as a new value.
        - if the value is empty, use an empty list to represent it.
    
    Example:
    ```r
    Windows IP Configuration
        Host Name . . . . . . . . . . . . : MyComputer-007
        Primary Dns Suffix  . . . . . . . :
        Node Type . . . . . . . . . . . . : Hybrid
        IP Routing Enabled. . . . . . . . : No
    ```
    &darr;&darr;&darr;
    ```json
    {
        "Windows IP Configuration": {
            "Host Name": "MyComputer-007",
            "Primary Dns Suffix": "",
            "Node Type": "Hybrid",
            "IP Routing Enabled": "No"
        }
    }
    ```
    Another example:
    ```r
    Wireless LAN adapter Wi-Fi:
            Media State . . . . . . . . . . . : Media disconnected
            Connection-specific DNS Suffix  . : local
            Description . . . . . . . . . . . : Wireless-ABCDE
            Physical Addresses. . . . . . . . : AB-CD-EF-01-02-03
                                                AB-CD-EF-01-02-04
                                                AB-CD-EF-01-02-05
            DHCP Enabled. . . . . . . . . . . : Yes
            Autoconfiguration Enabled . . . . : Yes
    ```
    &darr;&darr;&darr;
    ```json
    {
        "Wireless LAN adapter Wi-Fi:": {
            "Media State": "Media disconnected",
            "Connection-specific DNS Suffix": "local",
            "Description": "Wireless-ABCDE",
            "Physical Addresses": [
                "AB-CD-EF-01-02-03",
                "AB-CD-EF-01-02-04",
                "AB-CD-EF-01-02-05"
            ],
            "DHCP Enabled": "Yes",
            "Autoconfiguration Enabled": "Yes"
        }
    }
    ```
        


    Args:
        text (list[str]): the text to be converted. Expected to be from ipconfig or similar.

    Returns:
        dict: the text in dictionary format.

    Raises:
        IndexError: if the format is invalid.
    """
    if isinstance(text, str): text = text.split('\n')
    result = {}  # The dictionary to be returned.
    interface = None  # The current interface whose configuration values are being decoded.
    title = None  # The current title, inside the interface, whose value/s are being decoded.
    for line in text:
        if line.strip() == '': continue

        if line[0].strip() != '':
            # New interface found. Initialise dictionary.
            interface = line.strip(": \r")
            result[interface] = {}

        else:
            # Adding information to current `interface`.
            if '. :' in line or (not line.startswith("     ") and ':' in line):
                # New property (title).
                key, value = line.split(':', 1)
                title, value = key.strip(' .'), value.strip().replace("(Preferred)", "")
                if value.strip() == "": result[interface][title] = []
                else: result[interface][title] = value
            else:
                # Last property is a list, appending item.
                value = line.strip().replace("(Preferred)", "")
                if not isinstance(result[interface][title], list):
                    result[interface][title] = [result[interface][title]]
                result[interface][title].append(value)
                if len(result[interface][title]) == 1:
                    result[interface][title] = result[interface][title][0]
    return result


def get_ip_configuration() -> dict:
    """Get information from `>ipconfig /all`,
    select the first interface with a Default Gateway (i.e. online),
    return its information as a dictionary. Has cache.

    Guaranteed keys:
    ```
    "IPv4 Address"
    "Subnet Mask"
    ```


    Returns:
        dict: containing the following information:
    ```
        {
            **information["Windows IP Configuration"],
            **information["Interface with Gateway"],
            'Interface': interface,
            'Auto-Selected Interface': auto_select_interface(...)
        }
    ```
    
    Raises:
        RuntimeError: if no Default Gateway is found, meaning the computer is disconnected from the Internet.
    """
    if hasattr(get_ip_configuration, 'cache'):
        return get_ip_configuration.cache
    
    information = dictify(read_ipconfig())

    for interface, info in information.items():
        if 'Default Gateway' in info.keys():
            selected = interface
            break
    else:
        raise RuntimeError("Computer is not connected to Internet.")
    
    auto_selected_interface = auto_select_interface(information[selected]["IPv4 Address"])
    data = {**information["Windows IP Configuration"], **information[selected], 'Interface': interface, 'Auto-Selected Interface': auto_selected_interface}
    get_ip_configuration.cache = data
    return data

# Define an alias
ipconfig = get_ip_configuration


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
            return True
    return False

can_connect_ICMP_silent = threadify(can_connect_ICMP_base, silent=True)
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
    send_ARP.__name__ = "can_connect_ARP"
    packets = [Ether() / ARP(pdst=address) for address in addresses]
    threadify(send_ARP)(packets)

    sniffer.stop()
    # ******************* SAVE result[0] (i.e. MAC addresses) in a lookup table!
    return [result[1] for result in results]


def calculate_opcaity(connections: list[bool]) -> float:
    """This function calculates the opacity of a given connection list (a list of booleans indicating some contacting attempts' successes),
    according to a linear interpolation: if the last attempt succeeded, returns `1.0`; if the last `n`* attempts failed, return `0.0`.

    (*) The amount of attempts needed to register a disconnection is set in `GONE_AFTER: int` inside the function.

    Args:
        connections (list[bool]): a list of contact attempts' successes, taking the form of `[...True, True, False, True, False]`

    Returns:
        float: a value between `0.0` (disconnected) and `1.0` (connected) representing certainty that the device is still connected (a.k.a its opacity).
    """
    
    #   │++                             │+++++++++ 
    #   │  ++                           │         +++++  
    #   │    ++                         │              ++
    #   │      ++                       │                ++ 
    #   │        ++                =>   │                  + 
    #   │          ++                   │                   + 
    #   │            ++                 │                    +
    #   │              ++               │                    + 
    #   │                ++             │                     +
    #   │                  ++           │                     + 
    # ──┼─────────────────────────    ──┼────────────────────────
    #   │                               │

    GONE_AFTER: int = 11

    if len(connections) == 0: return 0.0
    if not any(connections): return 0.0
    distance_to_last = list(reversed(connections)).index(True)
    # Change this function? (see art above)
    opacity = 1.0 - distance_to_last / GONE_AFTER
    if opacity < 0: return 0.0
    return opacity


def display_continuous_connections_ICMP(addresses, all_possible_addresses):
    if not isinstance(addresses, list): addresses = list(addresses)
    table = {address: [] for address in addresses}
    waiting = Queue()

    # How many threads should be dedicated to the detection of new devices?
    # The iteration shifts in different threads by `shifting = thread_index * 71 mod 255`, to ensure efficiency.
    # Range of values: 1 to 18 (inclusive).
    # Optimal values: 18, 6, 3, 2, 1
    SCANNER_THREADS = 18


    def new_devices(order: int):
        # ** Maybe weights here? Addresses are more likely to be a low number like 10.0.0.13 and not a large one like 10.0.0.234
        all_addresses = shift(all_possible_addresses, 71*order)
        while True:
            for address in all_addresses:
                if address in table.keys(): continue
                if address in waiting.queue: continue
                if can_connect_ICMP_base(address):
                    waiting.put(address)
            # sleep(5)

    for i in range(SCANNER_THREADS):
        Thread(target=new_devices, args=(i, )).start()
    
    while True:
        sleep(1.1)
        while not waiting.empty():
            address = waiting.get()
            print("Adding address", address)
            if address not in addresses:
                addresses.append(address)
        for address, online in zip(addresses, can_connect_ICMP(addresses)):
            if address not in table: table[address] = []
            table[address].append(online)
        # print(table)
        hostify_sync(list(table.keys()))
        os.system("cls")
        # ** Change this to more dynamic, including the subnet mask...
        print("Connection testing (ICMP ping) to", '.'.join(ipconfig()["IPv4 Address"].split('.')[0:3]) + ".___\n")
        
        with InstantPrinting():
            for address in sorted(table.keys(), key=lambda x: int(''.join(x.split('.')))):
                print(
                    f"{address} ({hostify(address)}):".rjust(len("255.255.255.255 (Smartphone-Galaxy-S90-5G)")),
                    (''.join(['█' if x else ' ' for x in table[address]]) + "┅ ").rjust(63),
                    f"[{render_opacity(100 * calculate_opcaity(table[address]))}]"
                )
                if len(table[address]) > 60:
                    table[address] = table[address][-60:]


def auto_select_interface(ip: str):
    """Automatically selects the interface whose IP matches the given value.
    Uses the list given in `scapy.interfaces.get_working_ifaces()`.
    Sets the `scapy.config.conf.iface` to the correct value.

    Args:
        ip (str): the IPv4 address of the correct interface.

    Returns:
        str: `str(scapy.config.conf.iface)`
    """    
    for iface in get_working_ifaces():
        if iface.ip == ip:
            conf.iface = iface
    return str(conf.iface)


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


def main():
    get_ip_configuration()

    from testing.tests import test
    test()

    print_dict(ipconfig())

    all_possible_addresses = get_all_possible_addresses()
    print("There are", len(all_possible_addresses), "possible addresses in this subnet.")
    # print(all_possible_addresses)

    conf.warning_threshold = 10000  # Disables "MAC address to reach not found" warnings.

    connectable_addresses = set()

    # ICMP scans
    ICMP_inital_check_repeats = 3
    connectable_addresses.update(do_simple_scan(can_connect_ICMP, all_possible_addresses, repeats=ICMP_inital_check_repeats))
    

    # ARP scans
    ARP_inital_check_repeats = 3
    connectable_addresses.update(do_simple_scan(can_connect_ARP, all_possible_addresses, repeats=ARP_inital_check_repeats))
    # connectable_addresses = connectable_addresses + can_connect_ARP(all_possible_addresses)
    # connectable_addresses = list(set(connectable_addresses))
    # print("There are", len(connectable_addresses), "ARP connectable addresses in this subnet:")
    # print('    ' + '\n    '.join(connectable_addresses))

    # Continuous ICMP scans
    input("Commencing continuous ICMP scan. Press [Enter] to continue . . .")
    display_continuous_connections_ICMP(connectable_addresses, all_possible_addresses)



if __name__ == '__main__':
    try:
        main()
    except Exception as err:
        with open('error log.txt', 'w') as f:
            f.write('An exception occurred - %s' % err)
        raise
