import os
from subprocess import CalledProcessError, check_output as read_command
from scapy.sendrecv import sr1, sendp, AsyncSniffer
from scapy.layers.inet import IP, ICMP
from scapy.layers.l2 import Ether, ARP
from scapy.config import conf
from scapy.interfaces import get_working_ifaces
from util import *
from ip_handler import *



__author__ = 'Shaked Dan Zilberman'

# A range for the scanned ports.
PORT_RANGE = range(0, 1024)


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


@threadify
def can_connect_ICMP(address: str) -> bool:
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
    response = sr1(packet, verbose=0, timeout=2)
    if response is not None:
        # print(response[IP].show())
        if response[ICMP].type == 0:
            return True
    return False


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


def main():
    get_ip_configuration()

    from testing.tests import test
    test()

    print_dict(ipconfig())

    all_possible_addresses = get_all_possible_addresses()
    print("There are", len(all_possible_addresses), "possible addresses in this subnet.")
    # print(all_possible_addresses)
    
    ICMP_inital_check_repeats = 3
    connectable_addresses = set()
    for _ in range(ICMP_inital_check_repeats):
        connectable_addresses = connectable_addresses.union([address for address, online in zip(all_possible_addresses, can_connect_ICMP(all_possible_addresses)) if online])
    connectable_addresses = sorted(connectable_addresses, key=lambda x: int(x.split('.')[-1]))
    print("There are", len(connectable_addresses), "ICMP connectable addresses in this subnet:")
    print('    ' + '\n    '.join(connectable_addresses))
    # input("Commencing continuous ICMP scan. Press [Enter] to continue . . .")

    table = []
    while True:
        sleep(0.5)
        table.append(can_connect_ICMP(connectable_addresses))
        os.system("cls")
        print("Connection testing (ICMP ping) to", '.'.join(connectable_addresses[0].split('.')[0:3]) + ".___")
        print_table(table, header=connectable_addresses, head=lambda x: x.split('.')[-1].center(3), cell=lambda x: ' █ ' if x else '   ')
        if len(table) > 20:
            table = table[-20:]

    # connectable_addresses = can_connect_ARP(all_possible_addresses)
    # print("There are", len(connectable_addresses), "ARP connectable addresses in this subnet:")
    # print(', '.join(connectable_addresses))






if __name__ == '__main__':
    main()
