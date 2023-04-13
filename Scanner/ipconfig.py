from import_handler import ImportDefence
from Decorators import one_cache

with ImportDefence():
    from scapy.interfaces import get_working_ifaces
    from scapy.config import conf
    from subprocess import CalledProcessError, check_output as read_command


def read_ipconfig():
    """Read the command `>ipconfig /all` from console and decode it to UTF-8 text.

    Returns:
        list[str]: the command's output as a list of lines

    Raises:
        subprocess.CalledProcessError: if subprocess.check_output fails.
    """
    try:
        return read_command(['ipconfig',
                             '/all']).decode(encoding='utf-8',
                                             errors='ignore').split('\n')
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
    if isinstance(text, str):
        text = text.split('\n')
    result = {}  # The dictionary to be returned.
    # The current interface whose configuration values are being decoded.
    interface = None
    # The current title, inside the interface, whose value/s are being decoded.
    title = None
    for line in text:
        if line.strip() == '':
            continue

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
                if value.strip() == "":
                    result[interface][title] = []
                else:
                    result[interface][title] = value
            else:
                # Last property is a list, appending item.
                value = line.strip().replace("(Preferred)", "")
                if not isinstance(result[interface][title], list):
                    result[interface][title] = [result[interface][title]]
                result[interface][title].append(value)
                if len(result[interface][title]) == 1:
                    result[interface][title] = result[interface][title][0]
    return result


def ipconfig() -> dict:
    """Get information from `>ipconfig /all`,
    select the first interface with a Default Gateway (i.e. online),
    return its information as a dictionary. Has cache.

    Guaranteed keys:
    ```
    "IPv4 Address"
    "Subnet Mask"
    "Default Gateway"
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
    if hasattr(ipconfig, 'cache'):
        return ipconfig.cache

    information = dictify(read_ipconfig())
    possible_interfaces = [
        interface for interface,
        info in information.items() if 'Default Gateway' in info.keys()
    ]

    if len(possible_interfaces) <= 0:
        raise RuntimeError("Computer is not connected to Internet.")
    elif len(possible_interfaces) == 1:
        selected = possible_interfaces[0]
    else:
        for i, interface in enumerate(possible_interfaces):
            print(f"    ({i}) {interface}")
        selected = get_interface_safe(possible_interfaces)

    print("Interface:", selected)
    auto_selected_interface = auto_select_interface(
        information[selected]["IPv4 Address"])
    data = {
        **information["Windows IP Configuration"],
        **information[selected],
        'Interface': selected,
        'Auto-Selected Interface': auto_selected_interface
    }
    ipconfig.cache = data
    return data


@one_cache
def get_interface_safe(possible):
    while True:
        try:
            num = int(input("Select: "))
        except ValueError:
            print("Not a number")
            continue

        if not 0 <= num < len(possible):
            print("Not in range")
            continue

        return possible[num]


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


if __name__ == '__main__':
    ipconfig()
    from util import print_dict
    print_dict(ipconfig())
