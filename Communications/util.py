__author__ = 'Shaked Dan Zilberman'

### Utility methods
def isipv4(text):
    """Is `text` in IPv4 address format (0.0.0.0 to 255.255.255.255)?"""
    if not isinstance(text, str): return False
    text = text.replace("(Preferred)", "")
    for seg in text.split('.'):
        if not seg.strip().isnumeric():
            return False
    return len(text.split('.')) == 4


def isipv6(text):
    """Is `text` in IPv6 address format (0000:0000:0000:0000:0000:0000:0000:0000 and similar)?"""
    if not isinstance(text, str): return False
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
    if not isinstance(text, str): return False
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


def bitify(address):
    """Returns the address in binary.
    Example: 127.0.0.1 to '01111111000000000000000000000001'"""
    if not isipv4(address):
        return '00000000000000000000000000000000'
    result = ''
    for part in address.split('.'):
        try:
            binary = "{0:08b}".format(int(part, base=10))
        except ValueError:
            # Return 0.0.0.0 if address is invalid
            print("Invalid address:", address)
            return '00000000000000000000000000000000'
        result += binary
    return result


def ipv4sort(addresses):
    """Sorts the given list by the network entities' addresses' actual numerical value."""
    return sorted(addresses, key=lambda x: int(bitify(x.ip), base=2))


def is_in_network(address, ipconfig_data):
    """Is the IPv4 address in the local network?"""
    gateway = list(filter(isipv4, ipconfig_data["Default Gateway"]))[0]
    mask = ipconfig_data["Subnet Mask"]
    gateway, mask, address = bitify(gateway), bitify(mask), bitify(address)
    base = mask_on(gateway, mask)
    network = mask_on(address, mask)
    return network == base


def mask_on(a, mask):
    """Apply a subnet mask to address `a`.
    Assuming both are valid."""
    return a[:mask.count('1')]
