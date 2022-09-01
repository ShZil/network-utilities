import json
from scapy.all import conf, get_working_ifaces, sniff, ARP
from subprocess import check_output as read_command
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Arrow
import networkx as nx
from colorsys import hsv_to_rgb
from socket import gethostbyaddr as hostify_base
from socket import herror as hostify_error1
from socket import gaierror as hostify_error2
from threading import Thread
from networkx.exception import NetworkXError as nxerr


__author__ = 'Shaked Dan Zilberman'
ipconfig_data = None

### Utility methods
def isipv4(text):
    """Is `text` in IPv4 address format (0.0.0.0 to 255.255.255.255)?"""
    text = text.replace("(Preferred)", "")
    for seg in text.split('.'):
        if not seg.isnumeric():
            return False
    return len(text.split('.')) == 4


def isipv6(text):
    """Is `text` in IPv6 address format (0000:0000:0000:0000:0000:0000:0000:0000 and similar)?"""
    hexdigits = [hex(i)[2:].upper() for i in range(16)]
    text = text.replace("(Preferred)", "")
    max_len = 0
    for seg in text.split(':'):
        for letter in seg:
            if letter.upper() not in hexdigits:
                return False
        if len(seg) > max_len: max_len = len(seg)
    return len(text.split(':')) > 1 and max_len > 2


def ismac(text):
    """Is `text` in MAC address format (00:00:00:00:00:00 to FF:FF:FF:FF:FF:FF)?"""
    hexdigits = [hex(i)[2:].upper() for i in range(16)]
    text = text.replace("(Preferred)", "")
    text = text.replace(":", "-")
    for seg in text.split('-'):
        if len(seg) != 2:
            return False
        if seg[0].upper() not in hexdigits:
            return False
        if seg[1].upper() not in hexdigits:
            return False
    return len(text.split('-')) == 6


### NetEntity class
class NetEntity:
    def __init__(self, *args):
        self.mac, self.ip, self.ipv6 = NetEntity._parse(args)
        self.mac = self.mac.replace('-', ':')

    def __str__(self):
        return f"(MAC: {self.mac} | IP: {self.ip} | IPv6: {self.ipv6})"
    
    def hasMAC(self): return self.mac != '0'

    def hasIP(self): return self.ip != '0'

    def hasIPv6(self): return self.ipv6 != '0'
    
    @staticmethod
    def _parse(args):
        if isinstance(args[0], list):
            args = args[0]
        else:
            args = list(args)
        addresses = []
        for method in [ismac, isipv4, isipv6]:
            address = [address for address in args if method(address)]
            if len(address) > 1:
                raise ValueError("Multiple similar addresses given.")
            elif len(address) == 1:
                addresses.append(address[0])
            else:
                addresses.append('0')
        unknown = set(args) - set(addresses)
        for u in unknown: print("NetEntity init: Unable to resolve format [MAC/IPv4/IPv6] of", u)
        return tuple(addresses)


### IPCONFIG related functions
def read_ipconfig():
    """Read the command `>ipconfig /all` from console and decode it to UTF-8 text."""
    data = read_command(['ipconfig','/all'])
    data = data.split(b'\n')
    decoded = []
    for line in data:
        try:
            decoded.append(line.decode('utf-8'))
        except UnicodeDecodeError:
            continue
    return decoded


def dictify(text):
    """Turn `text` to a python dictionary"""
    result = {}
    current = None
    mini = None
    for line in text:
        if line.strip() == '':
            continue
        elif line[0].strip() == '':
            if '. :' in line:
                data = line.split(':', 1)
                mini, value = data[0].strip(), data[1].strip()
                mini = mini.strip(' .')
                result[current][mini] = value
            else:
                value = line.strip()
                if not isinstance(result[current][mini], list):
                    result[current][mini] = [result[current][mini]]
                result[current][mini].append(value)
        else:
            current = line.strip().strip(':')
            result[current] = {}
    return result


def get_ipconfig() -> tuple[int, str]:
    """Get information from >ipconfig,
    select the first interface with a Default Gateway,
    insert its info as a dictionary into `global ipconfig_data`.
    Returns the error level (0 = fine; anything else is error)."""
    global ipconfig_data

    d = dictify(read_ipconfig())
    try:
        filtered = filter(lambda elem: 'Default Gateway' in elem[1], d.items())
        selected = list(filtered)[0]
    except IndexError:
        print("ERROR: Could not find an interface with a default gateway.")
        print("Check connection to internet. Execute `ipconfig` to debug.")
        return -1, "No internet connection found."
    interface, data = selected[0], selected[1]
    ipconfig_data = clarify_filter(data)
    ipconfig_data["Interface"] = interface
    return 0, ''


def clarify_filter(data):
    """Filters unnecessary parts of the >ipconfig dictionary."""
    result = {}
    for key, value in data.items():
        if isinstance(value, list):
            result[key] = []
            for item in value:
                result[key].append(item.replace("(Preferred)", "").split('%')[0])
            if len(result[key]) == 1:
                result[key] = result[key][0]
            elif len(result[key]) == 0:
                del result[key]
        else:
            if value in ["Yes", "Enabled"]:
                result[key] = True
            elif value in ["No", "Disabled"]:
                result[key] = False
            else:
                result[key] = value.replace("(Preferred)", "").split('%')[0]
    return result


###### Automation
def auto_select_interface(ip, description):
    """Select the interface which matches the IP given"""
    for iface in get_working_ifaces():
        if iface.ip == ip:
            conf.iface = iface
    print("Interface:", conf.iface, f'  ( {description} )')


### Main 
def main():
    err, msg = get_ipconfig()
    if err != 0:
        print("An error happened.", err, msg)
        return
    here = NetEntity(ipconfig_data["Physical Address"], ipconfig_data["IPv4 Address"], ipconfig_data["IPv6 Address"])
    auto_select_interface(here.ip, ipconfig_data["Description"])
    router = NetEntity(ipconfig_data["Default Gateway"])
    subnet_mask = ipconfig_data["Subnet Mask"]
    with open('ipconfig.json', 'w') as f:
        f.write(json.dumps(ipconfig_data, indent=4))
    print("Default gateway:", router)
    print("Subnet Mask:", subnet_mask)
    print("Here:", here)


if __name__ == '__main__':
    main()
