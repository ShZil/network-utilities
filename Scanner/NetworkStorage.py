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
    
    def __eq__(self, other: object) -> bool:
        """This method checks equality between `self` and `other`.
        This is a magic method in Python, so you should call it using:
        ```py
        A = NetworkEntity(...)
        B = NetworkEntity(...)
        A == B
        ```

        Note: Transitive Property of Equality (A=B and B=C => A=C) doesn't necessarily apply here.
        There can be cases where A = B and B = C but A != C.
        This is because this method is based on (possibly) incomplete information in NetworkEntity-ies.

        Examples:
        ```
            | MAC               | IPv4        | IPv6                                   |
        |---|-------------------|-------------|----------------------------------------|
        | A | 00:00:5E:00:53:AF | 192.168.0.5 | 2001:db8:3333:4444:CCCC:DDDD:EEEE:FFFF |
        | B |                   | 192.168.0.5 | 2001:db8:3333:4444:CCCC:DDDD:EEEE:FFFF |
        | C | 00:00:5E:11:90:B1 | 192.168.0.5 |                                        |
        | D |                   |             | 2001:db8:3333:4444:CCCC:DDDD:EEEE:FFFF |
        ```
        Here, for example, `A` contains the full information,
        `B` contains only IPv4 and IPv6 addresses,
        `C` contains the true IPv4, a false MAC (maybe from an ARP poisoning attack), and no IPv6;
        and `D` contains only an IPv6 address.
        - Comparing `A == B` will compare the IPv4 and IPv6, and return `True`.
        - Comparing `B == C` will compare only the IPv4, and return `True`.
        - Comparing `A == C` will compare the MAC (doesn't match) and IPv4 (does match), and return `False`.
        - Comparing `D == C` will find no intersection between the address data, and return `False`.
        - Comparing `E == nothing` will return `False` for every `NetworkEntity E` (including `E = nothing`!).

        Args:
            other (object): the object to compare to.

        Returns:
            bool: whether the NetworkEntity-ies are equal.
        """
        if not isinstance(other, NetworkEntity):
            return False
        intersection = []
        for address in ["mac", "ip", "ipv6"]:
            if self[address] != nothing[address] and other[address] != nothing[address]:
                intersection.append(address)

        if len(intersection) == 0: return False
        
        for address in intersection:
            if self[address] != other[address]:
                return False
        
        return True
    
    def __getitem__(self, key):
        if key == "mac": return self.mac
        if key == "ip": return self.ip
        if key == "ipv6": return self.ipv6
        if key == "name": return self.name
        raise TypeError("Subscripting in NetworkEntity must be `mac`, `ip`, `ipv6`, or `name`.")


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
