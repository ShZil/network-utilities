from subprocess import CalledProcessError, check_output as read_command
from util import *


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


def dictify(text: list[str]) -> dict:
    """Turn `text` to a python dictionary.
    The nested dictionary is created according to the following rules:
    - loop over the lines.
    - if the line isn't indented, inistalise a new subdictionary.
    This is a new network interface, e.g. Ethernet, Wireless LAN, Bluetooth; or general info ("Windows IP Configuration").
    - otherwise,
        - if the line is formatted like "key . . . . : value", add this pair to the current active dictionary.
        - otherwise, convert the pair to a (key, list) pair, and add the line's contents as a new value.
    
    Examples:

        `Windows IP Configuration`
            `Host Name . . . . . . . . . . . . : MyComputer-007`
            `Primary Dns Suffix  . . . . . . . :`
            `Node Type . . . . . . . . . . . . : Hybrid`
            `IP Routing Enabled. . . . . . . . : No`
        
        {
            "Windows IP Configuration": {
                "Host Name": "MyComputer-007",
                "Primary Dns Suffix": "",
                "Node Type": "Hybrid",
                "IP Routing Enabled": "No"
            }
        }

        ``Wireless LAN adapter Wi-Fi:``
            ``Media State . . . . . . . . . . . : Media disconnected``
            ``Connection-specific DNS Suffix  . : local``
            ``Description . . . . . . . . . . . : Wireless-ABCDE``
            ``Physical Addresses. . . . . . . . : AB-CD-EF-01-02-03``
            ``                                    AB-CD-EF-01-02-04``
            ``                                    AB-CD-EF-01-02-05``
            ``DHCP Enabled. . . . . . . . . . . : Yes``
            ``Autoconfiguration Enabled . . . . : Yes``
        
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
        dict: the interface's information.
        dict: Windows IP Configuration dictionary.
    
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
    
    data = {**information["Windows IP Configuration"], **information[selected], 'Interface': interface}
    get_ip_configuration.cache = data
    return data


def main():
    from tests import test
    test()
    print_dict(get_ip_configuration())


if __name__ == '__main__':
    main()