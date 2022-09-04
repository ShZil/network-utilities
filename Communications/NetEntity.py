from hostify import hostify
from util import ismac, isipv4, isipv6

__author__ = 'Shaked Dan Zilberman'

### NetEntity class
class NetEntity:
    def __init__(self, *args):
        self.mac, self.ip, self.ipv6 = NetEntity._parse(args)
        self.mac = self.mac.replace('-', ':').upper()
        self.name = hostify(self.ip) if self.hasIP() else "Unknown"
        if self.name.strip() == "": self.name = "Unknown"

    def __str__(self) -> str:
        parts = [f"{title} {value}" for title, value in zip(["", "MAC:", "IP:", "IPv6:"], [self.name, self.mac, self.ip, self.ipv6]) if value not in ['0', "Unknown"]]
        parts = ' | '.join(parts)
        parts = parts.strip()
        return f"< {parts} >"
    
    def hasMAC(self) -> bool: return self.mac != '0'

    def hasIP(self) -> bool: return self.ip != '0'

    def hasIPv6(self) -> bool: return self.ipv6 != '0'

    def isEmpty(self) -> bool: return not (self.hasMAC() or self.hasIP() or self.hasIPv6())


    def sameAs(self, other) -> bool:
        if not isinstance(other, NetEntity): return False
        if self.hasMAC() and other.hasMAC():
            return self.mac == other.mac
        if self.hasIP() and other.hasIP():
            return self.ip == other.ip
        if self.hasIPv6() and other.hasIPv6():
            return self.ipv6 == other.ipv6
        return self.isEmpty() and other.isEmpty()
    

    def destruct(self):
        return '|'.join([self.mac, self.ip, self.ipv6])
    

    def get_available(self):
        available = []
        if self.hasMAC(): available.append(self.mac)
        if self.hasIP(): available.append(self.ip)
        if self.hasIPv6(): available.append(self.ipv6)
        return available
    

    def unite(self, other):
        if not isinstance(other, NetEntity): return self
        addresses = [getattr(self, attr) if getattr(self, has)() else getattr(other, attr) for attr, has in zip(["mac", "ip", "ipv6"], ["hasMAC", "hasIP", "hasIPv6"])]
        self.mac, self.ip, self.ipv6 = tuple(addresses)


    @staticmethod
    def _parse(args) -> tuple[str, str, str]:
        if isinstance(args[0], list):
            args = args[0]
        else:
            args = list(args)
        GENERAL = ["0.0.0.0", "255.255.255.255", "00:00:00:00:00:00", "FF:FF:FF:FF:FF:FF", "::"]
        addresses = []
        for method in [ismac, isipv4, isipv6]:
            address = [address for address in args if method(address)]
            if len(address) > 1:
                raise ValueError("Multiple similar addresses given.")
            elif len(address) == 1 and address[0] not in GENERAL:
                addresses.append(address[0].strip())
            else:
                addresses.append('0')
        unknown = set(args) - set(addresses) - set(GENERAL)
        for u in unknown:
            if u != None:
                print(f"NetEntity init: Unable to resolve format [MAC/IPv4/IPv6] of \"{u}\"")
        return tuple(addresses)
    
    @staticmethod
    def restruct(line):
        return NetEntity(line.split('|'))
