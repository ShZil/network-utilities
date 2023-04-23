from import_handler import ImportDefence
with ImportDefence():
    import ipaddress

from util import one_cache
from ipconfig import ipconfig


@one_cache
def get_scan_id() -> str:
    """Generates the current scan's identifier, based on `ipconfig()` info.
    The format:
    [Host Name]@[Interface]@[Gateway IPv4][Subnet Mask][Physical Address]
    All in Base64, with integer values whenever possible.

    Returns:
        str: the scan ID, encoded in base64, as a regular string.
    """
    from NetworkStorage import router, here
    import base64

    # '@' == (char)64 == '\x40'

    host = here.name.replace('@', '\x02').encode()
    iface = ipconfig()["Interface"].replace('@', '\x02').encode()

    gateway = int(ipaddress.IPv4Address(router.ip)).to_bytes(4, 'big')

    mask = ipconfig()["Subnet Mask"]
    mask = sum(bin(int(x)).count('1')
               for x in mask.split('.')).to_bytes(1, 'big')

    physical = here.mac
    physical = int(physical.replace('-', ''), 16).to_bytes(6, 'big')

    return base64.b64encode(
        host + b'\x40' + iface + b'\x40' + gateway + mask + physical
    ).decode()


def parse_scan_id(scan_id: str) -> str:
    """Decodes a scan ID.
    Reversing the logic in `get_scan_id`.
    Here, the `scan_id` doesn't have to be of the current network,
    but any valid scan ID.
    The returned string is of this format:
    "Here: {host name}, {host mac}, via {network interface}
    Router: {gateway ipv4}/{mask}"
    (yes, it contains a newline character)

    Args:
        scan_id (str): the scan ID to parse.

    Returns:
        str: a textual description of the network.
    """
    import base64
    decoded = base64.b64decode(scan_id)
    host, iface, others = decoded.split(b'\x40')

    host = host.decode().replace('\x02', '@')
    iface = iface.decode().replace('\x02', '@')

    gateway, mask, physical = others[:4], others[4:5], others[5:]
    gateway = int.from_bytes(gateway, 'big')
    gateway = str(ipaddress.ip_address(gateway))
    mask = int.from_bytes(mask, 'big')
    physical = hex(int.from_bytes(physical, 'big'))[2:].upper()
    physical = '-'.join(a + b for a, b in zip(physical[::2], physical[1::2]))

    router = f"{gateway}/{mask}"

    return f"Here: {host}, {physical}, via {iface}\nRouter: {router}"


if __name__ == '__main__':
    print("This file is responsible for the concept of Scan ID.")
    print("Scan ID is a base64 string that uniquely represents a network and the device in it running the software.")
    print("It's built from:")
    print("    - The host computer's name")
    print("    - The network interface used")
    print("    - The router's IPv4")
    print("    - The subnet mark of the network")
    print("    - The physical (MAC) address of the host computer")
    print("This file provides both an encoder: get_scan_id() -> scan ID,")
    print("and a decoder: parse_scan_id(scan ID) -> textual description of the network")
