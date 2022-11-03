from import_handler import ImportDefence
with ImportDefence():
    import re
    import ipaddress

class NetworkEntity:
    def __init__(self, mac, ip, ipv6, name):
        self.mac = standard_mac(mac)
        self.ip = check_ip(ip)
        self.ipv6 = extend_ipv6(ipv6)
        self.name = name
    
def standard_mac(mac: str) -> str:
    MAC_REGEX = r'^([0-9A-F]{2}-){5}([0-9A-F]{2})$'
    # using the IEEE Std 802-2014 definition.
    mac = mac.replace(':', '-').upper()
    if not re.match(MAC_REGEX, mac):
        raise ValueError(f"Invalid MAC address: \"{mac}\"")
    return mac


def check_ip(ip: str) -> str:
    IP_REGEX = r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
    if not re.match(IP_REGEX, ip):
        raise ValueError(f"Invalid IP address: \"{ip}\"")
    return ip


def extend_ipv6(ipv6: str) -> str:
    IPV6_REGEX = r'([a-f0-9:]+:+)+[a-f0-9]+'
    ipv6 = ipv6.lower()
    if not re.match(IPV6_REGEX, ipv6):
        raise ValueError(f"Invalid IPv6 address: \"{ipv6}\"")
    return ipaddress.ip_address(ipv6).exploded.lower()


nothing = NetworkEntity(mac="00:00:00:00:00:00", ip="0.0.0.0", ipv6="::", name="Unknown")
localhost = NetworkEntity(mac=nothing.mac, ip="127.0.0.1", ipv6="::1", name="loopback")
multicast = NetworkEntity(mac=nothing.mac, ip="224.0.0.2", ipv6="ff00::", name="multicast")  # hostify returns '*.mcast.net' (* differs for 224.0.0.*)
broadcast = NetworkEntity(mac="FF-FF-FF-FF-FF-FF", ip="255.255.255.255", ipv6=nothing.ipv6, name="broadcast")

class NetworkStorage:
    data = []

    def add(self, *args, mac=nothing.mac, ip=nothing.ip, ipv6=nothing.ipv6, name=nothing.name):
        entity = NetworkEntity(mac, ip, ipv6, name)
        self.data.append(entity)
