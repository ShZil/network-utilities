from import_handler import ImportDefence
with ImportDefence():
    import re
    import ipaddress
    from queue import Queue

from PrintingContexts import JustifyPrinting
from ipconfig import ipconfig
from ip_handler import get_all_possible_addresses
from globalstuff import G


class NetworkEntity:
    """An entity in the network, a connected device, the atom of information about the network.
    """
    def __init__(self, mac, ip, ipv6, name):
        """Each NetworkEntity has 4 main fields, listed below.

        Args:
            mac (str): the MAC address.
            ip (str): the IPv4 address.
            ipv6 (str): the IPv6 address.
            name (str): the host name.
        """
        self.mac = standard_mac(mac)
        self.ip = check_ip(ip)
        self.ipv6 = extend_ipv6(ipv6)
        self.name = name
        self._compare = None

    def equals(self, other: object) -> bool:
        """This method checks equality between `self` and `other`.

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
        # cannot compare with non-NetworkEntity objects
        if not isinstance(other, NetworkEntity):
            return False
        
        # the `intersection` list will inlude all the addresses that both entities have.
        # e.g., in the comparison `B == C` above, `intersection = ["ip"]`.
        intersection = []
        for address in ["mac", "ip", "ipv6"]:
            if self[address] != nothing[address] and other[address] != nothing[address]:
                intersection.append(address)

        # if there's no intersection, then we have no basis to decide whether they are equal (see `C == D`).
        # This will also make `nothing == nothing` return False.
        if len(intersection) == 0:
            return False

        # if there's a conflict, even just once, they're not equal.
        # a conflict is when both entities have that key, but the values don't match.
        for address in intersection:
            if self[address] != other[address]:
                return False

        # the code will get here if and only if there's some intersection and no conflicts.
        # this is a reasonable basis to conclude that the entities are indeed equal, and probably represent the same device.
        return True

    def __getitem__(self, key):
        if key == "mac":
            return self.mac
        if key == "ip":
            return self.ip
        if key == "ipv6":
            return self.ipv6
        if key == "name":
            return self.name
        raise TypeError(
            f"Subscripting in NetworkEntity must be `mac`, `ip`, `ipv6`, or `name`; got `{key}`"
        )

    def __setitem__(self, key, value):
        if key == "mac":
            self.mac = value
        elif key == "ip":
            self.ip = value
        elif key == "ipv6":
            self.ipv6 = value
        elif key == "name":
            self.name = value
        else:
            raise TypeError(
                f"Item assignment in NetworkEntity must be `mac`, `ip`, `ipv6`, or `name`; got `{key}`"
            )

    def __str__(self):
        return "< " + ' | '.join([self[field] for field in ["mac", "ip",
                                 "ipv6", "name"] if self[field] != nothing[field]]) + " >"

    def to_string(self, sep=' '):
        """The to_string function takes a single argument, sep, which is the separator between fields.
        It returns a string containing all of the non-empty fields in the order mac, ipv4 address, ipv6 address and name.
        If any field is missing, it will just skip over it.
        The default value for sep is ' ',
        so that if you call to_string with no arguments it will return a space-separated list of values.
        

        Args:
            sep (str, optional): Separate the fields in the string. Defaults to ' '.

        Returns:
            str: A string that looks like: `00-11-22-33-44-55 100.0.0.0 SomeWeirdDevice`.
        """        
        return sep.join([self[field] for field in ["mac", "ip",
                        "ipv6", "name"] if self[field] != nothing[field]])

    def to_dict(self):
        """
        The to_dict function returns a dictionary of the entity's attributes.

        Returns:
            dict: A dictionary with the following keys: `mac`, `ip`, `ipv6`, `name`.
        """
        return {field: self[field] for field in ["mac", "ip", "ipv6", "name"]}

    def compare(self):
        """Turns the values of the Entity's fields into integers to be used in a comparison.

        Returns:
            dict: field names as the keys, integers as the values.
        """
        if self._compare is None:
            result = {}
            result["ip"] = [int(part, base=10) for part in self.ip.split('.')]
            result["ip"] = sum([result["ip"][-i] * (256**i) for i in range(4)])
            result["mac"] = [int(part, base=16)
                             for part in self.mac.split('-')]
            result["mac"] = sum([result["mac"][-i] * (256**i)
                                for i in range(6)])
            result["ipv6"] = [int(part, base=16)
                              for part in self.ipv6.split(':')]
            result["ipv6"] = sum([result["ipv6"][-i] * (65536**i)
                                 for i in range(8)])
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
        if not self.equals(other):
            raise ValueError(
                "In NetworkEntity.merge(self,other), the entities must be equal."
            )
        for field in ["mac", "ip", "ipv6", "name"]:
            if other[field] != nothing[field]:
                self[field] = other[field]
        self._compare = None

    def __hash__(self):
        return hash((self.mac, self.ip, self.ipv6, self.name))

    def __eq__(self, other):
        # Use `.equals` for usual comparisons!
        if other is None:
            return False
        return self.mac == other.mac and self.ip == other.ip and self.ipv6 == other.ipv6 and self.name == other.name

    def tablestring(self, lengths):
        """
        The tablestring function takes a list of lengths and returns a string that is formatted to fit into the table.

        Args:
            lengths (list[int]): Determine the length of each column in the table

        Returns:
            str: A string of the object's attributes, with each attribute padded to a certain length
        """
        padded = []
        fields = [
            self.mac,
            self.ip,
            ipaddress.ip_address(self.ipv6).compressed,
            self.name
        ]
        titles = ["mac", "ip", "ipv6", "name"]
        # longests = ["FF-FF-FF-FF-FF-FF", "255.255.255.255", "0000:0000:0000::0000:0000", "NamesShouldntBeThisLong"]
        for title, field, length in zip(titles, fields, lengths):
            length = min(23, length)
            if field == nothing[title]:
                padded.append(" " * length)
            else:
                if len(str(field)) > length:
                    padded.append(str(field)[:length - 3] + '...')
                else:
                    padded.append(str(field).ljust(length))
        return ' | '.join(padded)


def standard_mac(mac: str) -> str:
    """Checks that the MAC address is valid, and standardises it.

    Args:
        mac (str): the MAC address.

    Raises:
        ValueError: if the address is invalid.

    Returns:
        str: the standardised MAC address.
    """
    MAC_REGEX = r'^([0-9A-F]{2}-){5}([0-9A-F]{2})$'
    # using the IEEE Std 802-2014 definition.
    mac = mac.replace(':', '-').upper()
    if not re.match(MAC_REGEX, mac):
        raise ValueError(f"Invalid MAC address: \"{mac}\"")
    return mac


def check_ip(ip: str) -> str:
    """The check_ip function takes a string as an argument and checks if it is a valid IP address.
    If the input is not of type str, or does not match the regex pattern for an IP address, 
    a ValueError will be raised. Otherwise, the function returns the input.

    Raises:
        ValueError: the argument is not a string.
        ValueError: the argument is not a valid IPv4 address.

    Returns:
        str: the same address, if valid.
    """
    IP_REGEX = r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
    if not isinstance(ip, str):
        raise ValueError(f"Invalid IP address type: \"{ip}\"")
    if not re.match(IP_REGEX, ip):
        raise ValueError(f"Invalid IP address: \"{ip}\"")
    return ip


def filterIPv4(addresses: list[str]) -> list[str]:
    """The filterIPv4 function takes a list of strings and returns only those that are valid IPv4 addresses.

    Args:
        addresses (list[str]): the input addresses.

    Returns:
        list[str]: A list of ipv4 addresses
    """
    if isinstance(addresses, str):
        return [addresses]

    def isip(ip: str) -> bool:
        """
        The isip function checks if a string is an IP address.

        Args:
            ip (str): the function that it will be receiving a string

        Returns:
            bool: A boolean value indicating whether the string is an IP address.
        """
        try:
            return check_ip(ip) == ip
        except ValueError:
            return False

    return list(filter(isip, addresses))


def extend_ipv6(ipv6: str) -> str:
    """
    The extend_ipv6 function takes an IPv6 address and returns the fully expanded version of that address.

    Args:
        ipv6 (str): Pass in the ipv6 address to be extended

    Raises:
        ValueError: in case the input is not a valid IPv6 address

    Returns:
        str: The ipv6 address in expanded form
    """
    IPV6_REGEX = r'(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))'
    ipv6 = ipv6.lower()
    if not re.match(IPV6_REGEX, ipv6):
        raise ValueError(f"Invalid IPv6 address: \"{ipv6}\"")
    return ipaddress.ip_address(ipv6).exploded.lower()


def match(address: str) -> NetworkEntity:
    """
    The match function takes an address and returns a NetworkEntity.
    The entity will have exactly one field set,
    depending on the type of the input,
    which is automatically detected (MAC / IPv4 / IPv6 / Error).

    Args:
        address (str): the address to categorise and insert.

    Raises:
        ValueError: if it's not a MAC, not an IPv4, and not an IPv6 address.

    Returns:
        NetworkEntity: A NetworkEntity object with one field.
    """
    try:
        standard_mac(address)
        return NetworkEntity(mac=address, ip=nothing.ip, ipv6=nothing.ipv6, name="Unknown")
    except ValueError:
        pass

    try:
        check_ip(address)
        return NetworkEntity(mac=nothing.mac, ip=address, ipv6=nothing.ipv6, name="Unknown")
    except ValueError:
        pass

    try:
        extend_ipv6(address)
        return NetworkEntity(mac=nothing.mac, ip=nothing.ip, ipv6=address, name="Unknown")
    except ValueError:
        pass

    raise ValueError("The address is not MAC, not IP, and not IPv6.")


class LockedNetworkEntity(NetworkEntity):
    """A LockedNetworkEntity is a NetworkEntity that has complete and total information,
    and so won't be changed (thus, locked).
    Code-wise, this means that `__setitem__` and `merge` are disabled;
    the former will raise an exception and the latter will just ignore calls.
    """
    def __setitem__(self, key, value):
        raise TypeError(
            f"Item assignment in NetworkEntity cannot be done on a locked entity.")

    def merge(self, other):
        """Since we know LockedNetworkEntities will have complete information,
        there's no need to merge additions into them (plus it causes errors).

        Args:
            other (NetworkEntity): the entity to NOT merge with. For compatibility with `NetworkEntity.merge`.
        """
        pass



class PublicAddressNetworkEntity(LockedNetworkEntity):
    """A PublicAddressNetworkEntity is a LockedNetworkEntity that represents the "outer" side of the router,
    i.e. its external address.
    Code-wise, this is just used for type-checking. The class overrides no methods.
    """
    pass


# Special Entities: LockedNetworkEntity
nothing = LockedNetworkEntity(
    mac="00:00:00:00:00:00",
    ip="0.0.0.0",
    ipv6="::",
    name="Unknown"
)
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
    connections = Queue()

    # Use Singleton pattern:
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = object.__new__(cls)
            # Initialise special entities
            global nothing, localhost, mDNS, multicast, broadcast, router, local_broadcast, here
            localhost = LockedNetworkEntity(
                mac=nothing.mac,
                ip="127.0.0.1",
                ipv6="::1",
                name="loopback"
            )

            mDNS = LockedNetworkEntity(
                mac=nothing.mac,
                ip="224.0.0.251",
                ipv6="ff02::fb",
                name="multicast DNS"
            )

            multicast = LockedNetworkEntity(
                mac=nothing.mac,
                ip="224.0.0.2",
                ipv6="ff00::",
                name="multicast"
            )  # hostify returns '*.mcast.net' (differs for 224.0.0.*)

            broadcast = LockedNetworkEntity(
                mac="FF-FF-FF-FF-FF-FF",
                ip="255.255.255.255",
                ipv6=nothing.ipv6,
                name="broadcast"
            )

            router = NetworkEntity(
                mac=nothing.mac,
                ip=filterIPv4(
                    ipconfig()["Default Gateway"])[0],
                ipv6=nothing.ipv6,
                name="router"
            )
            SpecialInformation()[router, 'role'] = 'router'

            local_broadcast = LockedNetworkEntity(
                mac=nothing.mac,
                ip=get_all_possible_addresses()[-1],
                ipv6=nothing.ipv6,
                name="local broadcast"
            )

            here = LockedNetworkEntity(
                mac=ipconfig()["Physical Address"],
                ip=ipconfig()["IPv4 Address"],
                ipv6=ipconfig()["IPv6 Address"] if 'IPv6 Address' in ipconfig() else nothing.ipv6,
                name=ipconfig()["Host Name"]
            )
            SpecialInformation()[here, 'role'] = 'here'

            cls.instance.special_add(
                localhost,
                mDNS,
                multicast,
                broadcast,
                router,
                local_broadcast,
                here
            )
            # print(nothing, *specials, sep="\n")

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
        """
        The add function adds a NetworkEntity to the waiting queue.

        Args:
            *args (list, optional): Pass a variable number of NetworkEntities to the function; OR:
            mac (str, optional): Set the mac address of a network entity. Defaults to nothing.mac.
            ip (str, optional): Set the ip address of a network entity. Defaults to nothing.ip.
            ipv6 (str, optional): Add an ipv6 address to the networkentity. Defaults to nothing.ipv6.
            name (str, optional): Give the entity a name. Defaults to nothing.name.
        """
        if len(args) == 0:
            self.waiting.put(NetworkEntity(mac, ip, ipv6, name))
        else:
            for entity in args:
                if isinstance(entity, NetworkEntity) \
                        or isinstance(entity, LockedNetworkEntity):
                    self.waiting.put(entity)

    def special_add(self, *entities):
        """Adds a special LockedNetworkEntity to the `specials` list.
        NOT THREAD-SAFE. Only use in non-parellel code.
        Intended for LockedNetworkEntities but regular NetworkEntities are allowed too.

        Args:
            entities (list[NetworkEntity]): the special entities to be added.
        """
        for entity in entities:
            specials.append(entity)
    
    def connect(self, ip1, ip2):
        """
        The connect function takes two IP addresses as arguments and adds them to the connections queue.
        Later on, they will be connected by an edge in the G (Graph).

        Args:
            ip1 (str): Identify the first node in the connection
            ip2 (str): Connect the ip2 to the ip1
        """
        self.connections.put((ip1, ip2))

    def _resolve(self):
        def append(entity):
            """
            The append function is used to add a new entity to the network.
            It loops through all the other entities,
            checking whether the entity is already present.
            If another entity is found that is "closly enough related",
            they will be merged.
            If it's not a LockedNetworkEntity, it will also be compared with the `specials`.
            If a match is found, the entity will be "inspired" by the special entity,
            and take its knowledge.
            Finally, the entity is added to `self.data` and `G`.
            If it's in the LAN, an edge to the router is also added.
            
            Args:
                entity (NetworkEntity): Add a new entity to the network
            """
            for other in self.data:
                if entity is other:
                    return
                if other.equals(entity):
                    other.merge(entity)
                    return
            if not isinstance(entity, LockedNetworkEntity):
                for special in specials:
                    if entity.equals(special):
                        entity.merge(special)
            self.data.append(entity)
            G.add_node(entity)
            if entity in LAN or isinstance(entity, PublicAddressNetworkEntity):
                G.add_edge(router, entity)

        from hostify import hostify_sync, hostify
        hostify_sync([
            entity.ip
            for entity in list(self.waiting.queue)
            if entity.ip != nothing.ip
        ])
        for entity in list(self.waiting.queue):
            if entity.name == nothing.name:
                entity.name = hostify(entity.ip)
            append(entity)
        ips = {entity.ip: entity
                for entity in self.data
                if entity.ip != nothing.ip}
        for ip1, ip2 in list(self.connections.queue):
            if (ip1 not in ips) or (ip2 not in ips):
                continue
            G.add_edge(ips[ip1], ips[ip2])
            

    def sort(self, key="ip"):
        """
        The sort function takes a key argument, which is either 'ip', 'mac', or
        'ipv6'. It then sorts the data list by that key. If there are no entries in
        the data list, it returns an empty list. Otherwise, it returns a sorted version of the 
        data list.

        Args:
            key (str, optional): Specify the field to sort by. Defaults to "ip".

        Raises:
            ValueError: for invalid keys.

        Returns:
            list: the entities sorted by the chosen key.
        """
        self._resolve()
        try:
            others = ['ip', 'mac', 'ipv6']
            others.remove(key)
        except ValueError:
            raise ValueError(
                'Sorting key must be either `mac`, `ip`, or `ipv6`.'
            )
        keys = [key] + others

        if len(self.data) == 0:
            return [nothing]
        return sorted(self.data,
                      key=lambda entity: tuple(entity.compare()[field]
                                               for field in keys))

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
            raise TypeError(
                f"NetworkStorage.organise's key must be `mac`, `ip`, `ipv6`, or `name`; got `{key}`"
            )
        return {entity[key]: entity
                for entity in self.data
                if entity[key] != nothing[key]}

    def __iter__(self):
        self._resolve()
        for elem in self.sort():
            yield elem

    def __len__(self):
        return len(self.data)

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
            return [entity[key]
                    for entity in self.data
                    if entity[key] != nothing[key]]
        raise TypeError(f"Subscripting in NetworkStorage must be `mac`, `ip`, `ipv6`, or `name`; got `{key}`")

    def print(self):
        """
        The print function is used to print the contents of the NetworkStorage structure.
        Uses JustifyPrinting for its style.
        """
        self._resolve()
        with JustifyPrinting():
            for entity in self:
                print(entity)

    def tablestring(self):
        """
        The tablestring function is used to create a table of the hosts in the network.
        It returns a list of strings, each string being one line of the table, representing one entity.
        The first and last lines are borders, with titles in between them, and the data.

        Returns:
            list[str]: the data structure, presented as a tidy table.
        """
        lengths = [max(map(lambda x: len(str(x)), self[field]), default=4)
                   for field in ["mac", "ip", "ipv6", "name"]]
        lengths = [min(length, 23) for length in lengths]
        titles = ["MAC", "IPv4", "IPv6", "Name"]
        titles = "| " + ' | '.join([title.center(length)
                                   for title, length in zip(titles, lengths)]) + " |"

        width = sum(lengths) + 11
        top = "/" + ("-" * width) + "\\"
        subtitles = "|" + ('-' * width) + "|"
        bottom = "\\" + ("-" * width) + "/"
        return [top, titles, subtitles,
                *["| " + x.tablestring(lengths) + " |" for x in self.sort()], bottom]


class LAN:
    def __contains__(self, entity):
        return entity.ip in get_all_possible_addresses()


LAN = LAN()

class SpecialInformation(dict):
    # singleton
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

    def __setitem__(self, keys: tuple[NetworkEntity, str], value):
        if isinstance(keys, NetworkEntity) and isinstance(value, dict):
            super().__setitem__(keys, value)
            return
        if not isinstance(keys[0], NetworkEntity):
            raise TypeError("First key must be of type NetworkEntity.")
        if not isinstance(keys[1], str):
            raise TypeError("Second key must be a string.")
        entity, info_key = keys
        if entity not in self:
            super().__setitem__(entity, {})
        self[entity][info_key] = value

    def __getitem__(self, key):
        # This function trys to find any NetworkEntities in the dict's keys that `.equals` with `key`,
        # and merges all their information to a single dict that is returned.
        if isinstance(key, NetworkEntity):
            merged = {}
            for entity, value in list(self.items()):
                if key.equals(entity):
                    merged.update(value)
            self[key] = merged
            return merged
        elif isinstance(key, tuple):
            entity, info_key = key
            merged = {}
            for item, value in self.items():
                if entity.equals(item):
                    merged.update(value)
            self[entity] = merged
            return merged[info_key]
        elif isinstance(key, str):
            entities = []
            for entity, value in self.items():
                if key in value:
                    entities.append(entity)
            return entities
        else:
            raise TypeError("Key must be NetworkEntity or tuple or key.")

    def __contains__(self, item):
        if isinstance(item, NetworkEntity):
            return any(item.equals(entity) for entity in self.keys())
        entity, info_key = item
        if entity not in self:
            return False
        return info_key in self[entity]


if __name__ == '__main__':
    print("This module is responsible for the Network Storage data,")
    print("and all the infrastructure that supports it.")
    NetworkStorage()
    print([str(entity) for entity in specials])
    print(str(SpecialInformation()))
