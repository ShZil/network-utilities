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


### NetEntity class
class NetEntity:
    def __init__(self, *args):
        self.mac, self.ip, self.ipv6 = NetEntity._parse(args)
        self.mac = self.mac.replace('-', ':')

    def __str__(self):
        return f"(( {self.mac} | {self.ip} ))"

    def destruct(self):
        return f"{self.mac}%{self.ip}"

    @staticmethod
    def restruct(text):
        mac, ip = tuple(text.split('%'))
        return NetEntity(mac, ip)
    
    @staticmethod
    def _parse(args):
        if not (2 <= len(args) <= 3):
            raise ValueError("NetEntity must recevive 2 to 3 arguments.")
        a = args[0]
        b = args[1]
        try:
            c = args[2]
        except IndexError:
            c = ""
        ipv4 = [ip for ip in [a, b, c] if isipv4(ip)]
        if len(ipv4) != 1:
            raise ValueError(("Multiple" if len(ipv4) > 1 else "No") + " IPv4 addresses given.")
        ipv4 = ipv4[0]

        


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
def auto_select_interface(ip):
    """Select the interface which matches the IP given"""
    for iface in get_working_ifaces():
        if iface.ip == ip:
            conf.iface = iface
    print("Interface:", conf.iface)


### Main 
def main():
    err, msg = get_ipconfig()
    if err != 0:
        print("An error happened.", err, msg)
        return
    here = NetEntity(ipconfig_data["Physical Address"], ipconfig_data["IPv4 Address"], ipconfig_data["IPv6 Address"])
    auto_select_interface(here.ip)
    # If you wanna do an active ARP scan, do it here.
    router_ip = ipconfig_data["Default Gateway"]
    subnet_mask = ipconfig_data["Subnet Mask"]
    with open('ipconfig.json', 'w') as f:
        f.write(json.dumps(ipconfig_data, indent=4))
    print("Default gateway:", router_ip)
    print("Mask:", subnet_mask)


if __name__ == '__main__':
    main()
