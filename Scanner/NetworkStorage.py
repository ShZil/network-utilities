from import_handler import ImportDefence
with ImportDefence():
    import re
    import ipaddress
    from queue import Queue

from util import JustifyPrinting
from ipconfig import ipconfig
from ip_handler import get_all_possible_addresses
from globalstuff import G

class NetworkEntity:
    def __init__(self, mac, ip, ipv6, name):
        self.mac = standard_mac(mac)
        self.ip = check_ip(ip)
        self.ipv6 = extend_ipv6(ipv6)
        self.name = name
        self._compare = None
    
    
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
        raise TypeError(f"Subscripting in NetworkEntity must be `mac`, `ip`, `ipv6`, or `name`; got `{key}`")
    

    def __setitem__(self, key, value):
        if key == "mac": self.mac = value
        elif key == "ip": self.ip = value
        elif key == "ipv6": self.ipv6 = value
        elif key == "name": self.name = value
        else: raise TypeError(f"Item assignment in NetworkEntity must be `mac`, `ip`, `ipv6`, or `name`; got `{key}`")
    

    def __str__(self):
        return "< " + ' | '.join([self[field] for field in ["mac", "ip", "ipv6", "name"] if self[field] != nothing[field]]) + " >"
    

    def compare(self):
        """Turns the values of the Entity's fields into integers to be used in a comparison.

        Returns:
            dict: field names as the keys, integers as the values.
        """
        if self._compare is None:
            result = {}
            result["ip"] = [int(part, base=10) for part in self.ip.split('.')]
            result["ip"] = sum([result["ip"][-i] * (256**i) for i in range(4)])
            result["mac"] = [int(part, base=16) for part in self.mac.split('-')]
            result["mac"] = sum([result["mac"][-i] * (256**i) for i in range(6)])
            result["ipv6"] = [int(part, base=16) for part in self.ipv6.split(':')]
            result["ipv6"] = sum([result["ipv6"][-i] * (65536**i) for i in range(8)])
            self._compare = result
        return self._compare
    

    def merge(self, other):
        """Merges the information from two equal NetworkEntity-ies.
        This method fills in any missing information in `self` with the information from `other`.
        Note: they must be equal.
        Note: merges right-into-left -- in `A.merge(B)`, A is full with information, and B is unchanged.

        Args:
            other (NetworkEntity): the entity to be merged with.
        """
        if self != other: raise ValueError("In NetworkEntity.merge(self,other), the entities must be equal.")
        for field in ["mac", "ip", "ipv6", "name"]:
            if other[field] != nothing[field]:
                self[field] = other[field]
        self._compare = None


def standard_mac(mac: str) -> str:
    MAC_REGEX = r'^([0-9A-F]{2}-){5}([0-9A-F]{2})$'
    # using the IEEE Std 802-2014 definition.
    mac = mac.replace(':', '-').upper()
    if not re.match(MAC_REGEX, mac):
        raise ValueError(f"Invalid MAC address: \"{mac}\"")
    return mac


def check_ip(ip: str) -> str:
    IP_REGEX = r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
    if not isinstance(ip, str):
        raise ValueError(f"Invalid IP address type: \"{ip}\"")
    if not re.match(IP_REGEX, ip):
        raise ValueError(f"Invalid IP address: \"{ip}\"")
    return ip


def filterIP(l: list[str]) -> list[str]:
    if isinstance(l, str): return [l]

    def isip(ip: str) -> bool:
        try:
            return check_ip(ip) == ip
        except ValueError:
            return False
    
    return list(filter(isip, l))


def extend_ipv6(ipv6: str) -> str:
    IPV6_REGEX = r'(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))'
    ipv6 = ipv6.lower()
    if not re.match(IPV6_REGEX, ipv6):
        raise ValueError(f"Invalid IPv6 address: \"{ipv6}\"")
    return ipaddress.ip_address(ipv6).exploded.lower()


class LockedNetworkEntity(NetworkEntity):
    def __setitem__(self, key, value):
        raise TypeError(f"Item assignment in NetworkEntity cannot be done on a locked entity.")
    
    
    def merge(self, other):
        # Since we know LockedNetworkEntities will have complete information, there's no need to merge additions into them (plus it causes errors).
        pass


# Special Entities: LockedNetworkEntity
nothing = LockedNetworkEntity(mac="00:00:00:00:00:00", ip="0.0.0.0", ipv6="::", name="nothing")
localhost = None
mDNS = None
multicast = None
broadcast = None
router = None
local_broadcast = None
here = None

specials = []

class NetworkStorage:
    data = []
    waiting = Queue()

    # Use Singleton pattern:
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = object.__new__(cls)
            # Initialise special entities
            global nothing, localhost, mDNS, multicast, broadcast, router, local_broadcast, here
            localhost = LockedNetworkEntity(mac=nothing.mac, ip="127.0.0.1", ipv6="::1", name="loopback")
            mDNS = LockedNetworkEntity(mac=nothing.mac, ip="224.0.0.251", ipv6="ff02::fb", name="multicast DNS")
            multicast = LockedNetworkEntity(mac=nothing.mac, ip="224.0.0.2", ipv6="ff00::", name="multicast")  # hostify returns '*.mcast.net' (differs for 224.0.0.*)
            broadcast = LockedNetworkEntity(mac="FF-FF-FF-FF-FF-FF", ip="255.255.255.255", ipv6=nothing.ipv6, name="broadcast")
            router = LockedNetworkEntity(mac=nothing.mac, ip=filterIP(ipconfig()["Default Gateway"])[0], ipv6=nothing.ipv6, name="router")  # You sure you can't know the MAC and IPv6? + improve getting the default gateway's IPv4
            local_broadcast = LockedNetworkEntity(mac=nothing.mac, ip=get_all_possible_addresses()[-1], ipv6=nothing.ipv6, name="local broadcast")  # You sure you can't know the MAC and IPv6?
            here = LockedNetworkEntity(mac=ipconfig()["Physical Address"], ip=ipconfig()["IPv4 Address"], ipv6=ipconfig()["IPv6 Address"] if 'IPv6 Address' in ipconfig() else nothing.ipv6, name=ipconfig()["Host Name"])

            cls.instance.special_add(localhost, mDNS, multicast, broadcast, router, local_broadcast, here)
            print(nothing, *specials, sep="\n")

            cls.instance._give_names()
        return cls.instance
    

    def _give_names(self):
        for method in dir(self):
            if not method.startswith('_'):
                try:
                    getattr(self, method).__func__.__name__ = "NetworkStorage." + method
                except AttributeError:
                    continue


    def add(self, *args, mac=nothing.mac, ip=nothing.ip, ipv6=nothing.ipv6, name=nothing.name):
        if len(args) == 0:
            self.waiting.put(NetworkEntity(mac, ip, ipv6, name))
        else:
            for entity in args:
                if isinstance(entity, NetworkEntity):
                    self.waiting.put(entity)

    
    def special_add(self, *entities):
        """Adds a special LockedNetworkEntity to the `specials` list.
        NOT THREAD-SAFE. Only use in non-parellel code.

        Args:
            entities (LockedNetworkEntity): the special entities to be added.
        """
        for entity in entities:
            if isinstance(entity, LockedNetworkEntity):
                specials.append(entity)


    def _resolve(self):
        def append(entity):
            for other in self.data:
                if entity == other:
                    other.merge(entity)
                    return
            if not isinstance(entity, LockedNetworkEntity):
                for special in specials:
                    if entity == special:
                        entity.merge(special)
            self.data.append(entity)
            G.add_node(entity)
        
        from hostify import hostify_sync, hostify
        hostify_sync([entity.ip for entity in self.waiting.queue if entity.ip != nothing.ip])
        for entity in list(self.waiting.queue):
            if entity.name == nothing.name:
                entity.name = hostify(entity.ip)
            append(entity)


    def sort(self, key="ip"):
        self._resolve()
        try:
            others = ['ip', 'mac', 'ipv6']
            others.remove(key)
        except ValueError:
            raise ValueError('Sorting key must be either `mac`, `ip`, or `ipv6`.')
        keys = [key] + others

        if len(self.data) == 0: return [nothing]
        return sorted(self.data, key=lambda entity: tuple([entity.compare()[field] for field in keys]))
    

    def organise(self, key="ip"):
        """Converts the storage into a dictionary, with the key being one of the fields, and the values -- the whole entity.
        Example:
        ```
        data = [networkEntity1, networkEntity2, networkEntity3]
        organise('ip') = {
            "1.1.1.1": networkEntity1,
            "2.2.2.2": networkEntity2,
            "1.0.0.3": networkEntity3
        }
        ```

        Args:
            key (str, optional): the key for the dictionary. Must be `mac`, `ip`, `ipv6`, or `name`. Defaults to `ip`.

        Returns:
            dict: the dictionary as described above.
        
        Raises:
            TypeError: if the key is invalid.
        """
        self._resolve()
        if key not in ["mac", "ip", "ipv6", "name"]:
            raise TypeError(f"NetworkStorage.organise's key must be `mac`, `ip`, `ipv6`, or `name`; got `{key}`")
        return {entity[key]: entity for entity in self.data if entity[key] != nothing[key]}
    

    def __iter__(self):
        self._resolve()
        for elem in self.sort():
            yield elem
    

    def __getitem__(self, key):
        """Gets a single "column" (key, property, field) as a list from all the NetworkEntity-ies stored.
        Note: this will not include empty values. E.g., asking for `lookup['ipv6']` will not return any data from entities without an IPv6 datum.

        Args:
            key (str): the key to select from all the entities. Must be 'mac', 'ip', 'ipv6', or 'name'.

        Raises:
            TypeError: if the key is invalid.

        Returns:
            list: a list containing all the requested data.
        """
        self._resolve()
        if key in ["mac", "ip", "ipv6", "name"]:
            self._resolve()
            return [entity[key] for entity in self.data if entity[key] != nothing[key]]
        raise TypeError(f"Subscripting in NetworkStorage must be `mac`, `ip`, `ipv6`, or `name`; got `{key}`")
    

    def print(self):
        self._resolve()
        with JustifyPrinting():
            for entity in self:
                print(entity)


