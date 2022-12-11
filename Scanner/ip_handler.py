from ipconfig import ipconfig
from util import memorise

__author__ = 'Shaked Dan Zilberman'


def bitify(address: str) -> str:
    """This method turns an IPv4 address (0.0.0.0 to 255.255.255.255) to a string of 0s and 1s.
    Each part in the address turns to 8 binary digits, thus the result must always be 32 characters long.
    
    Examples:
        0.0.0.0 -> '00000000000000000000000000000000' (32 0s)
        255.255.255.255 -> '11111111111111111111111111111111' (32 1s)
        192.168.0.1 -> '11000000101010000000000000000001'

    Args:
        address (str): the address to be converted.

    Returns:
        str: a binary-looking string.
    """
    result = ''
    if len(address.split('.')) != 4:
        raise TypeError(f"Given address ({address}) is not IPv4 - not composed of 4 dot-separated parts.")
    for part in address.split('.'):
        try:
            result += "{0:08b}".format(int(part, base=10))
        except ValueError:
            raise TypeError(f"Given address ({address}) is not IPv4 -- part \"{part}\" is not a valid integer.")
    return result


def unbitify(binary: str) -> str:
    """This method turns an IPv4 address represented as a string of binary digits to the regular representation.
    Each part in the address turns from 8 binary digits to 1-3 decimal digits.
    Acts as the inverse of `bitify`.
    
    Examples:
        '00000000000000000000000000000000' (32 0s) -> 0.0.0.0
        '11111111111111111111111111111111' (32 1s) -> 255.255.255.255
        '11000000101010000000000000000001' -> 192.168.0.1

    Args:
        address (str): the address to be parsed.

    Returns:
        str: an IPv4 address.
    """
    result = ''
    for byte in [binary[i:i+8] for i in range(0, len(binary), 8)]:
        result += str(int(byte, base=2))
        result += '.'
    return result.strip('.')


def subnet_address_range(subnet_mask: str, *some_addresses: tuple[str]):
    """This function computes the address range of a subnet (i.e. the Network ID, with all (*)s in the Device ID section).

    Code explanation:

    Define a wrapper for `bitify` which also converts the result to an integer. Apply it to subnet_mask.
    ```
    bits = lambda address: int(bitify(address), base=2)
    mask = bits(subnet_mask)
    ```

    Compute the *bitwise logical AND* of each address and the mask.
    ```
    base = [bits(address) & mask for address in some_addresses]
    ```

    Raise exceptions if no unique values are found / more than one unique value is found.

    Find the network ID: using the bitwise AND result, zfill it up to 32 characters, and cut only the part with 1s in the mask.
    ```
    mask = format(mask, 'b')
    network = format(base[0], 'b').zfill(32)[:mask.count('1')]
    ```

    Find the lowest and highest possible addresses by filling the empty space with 0s or 1s respectively.
    ```
    lowest = unbitify(network + ('0' * mask.count('0')))
    highest = unbitify(network + ('1' * mask.count('0')))
    ```

    For each part of the address (i.e. `A.B.C.D`, then A, B, C, and D are parts), find the correct format.
    ```
    if low == high:
        result += low
    elif low == '0' and high == '255':
        result += '*'
    else:
        result += f"{low}-{high}"
    ```

    Args:
        subnet_mask (str): the subnet mask, `like 255.255.255.0`.
        *some_addresses (str, str, str...): some example addresses of devices in the network. Must be at least one.

    Raises:
        TypeError: If no example addresses are given.
        ValueError: If the example addresses belong to different networks.

    Returns:
        str: the address range. Note: this is not a valid IPv4 address, it uses (*)s and (-)s in the Device ID portion.
    """
    bits = lambda address: int(bitify(address), base=2)
    mask = bits(subnet_mask)
    base = [bits(address) & mask for address in some_addresses]
    base = list(set(base))
    if len(base) == 0:
        raise TypeError("No addresses were given besides the mask.")
    if len(base) > 1:
        raise ValueError("The addresses given fit different networks.")
    mask = format(mask, 'b')
    network = format(base[0], 'b').zfill(32)[:mask.count('1')]
    lowest = unbitify(network + ('0' * mask.count('0')))
    highest = unbitify(network + ('1' * mask.count('0')))
    result = ''
    for low, high in zip(lowest.split('.'), highest.split('.')):
        if low == high: result += low
        elif low == '0' and high == '255': result += '*'
        else: result += f"{low}-{high}"
        result += '.'
    return result.strip('.')


def base_subnet_address(subnet_mask: str, *some_addresses: tuple[str]):
    """This function computes the base address of a network (i.e. the Network ID, with all 0s in the Device ID section)

    Code explanation:

    Define a wrapper for `bitify` which also converts the result to an integer. Apply it to subnet_mask.
    ```
    bits = lambda address: int(bitify(address), base=2)
    mask = bits(subnet_mask)
    ```

    Compute the *bitwise logical AND* of each address and the mask.
    ```
    base = [bits(address) & mask for address in some_addresses]
    ```

    Raise exceptions if no unique values are found / more than one unique value is found.

    Turn `base[0]` (the only unique value) to a binary string, zfill it to 32 characters, pass it to `unbitify`, and return.
    ```
    return unbitify(format(base[0], 'b').zfill(32))
    ```

    Args:
        subnet_mask (str): the subnet mask, `like 255.255.255.0`.
        *some_addresses (str, str, str...): some example addresses of devices in the network. Must be at least one.

    Raises:
        TypeError: If no example addresses are given.
        ValueError: If the example addresses belong to different networks.

    Returns:
        str: the base address. Note: this is a valid IPv4 address, the lowest in the network.
    """
    bits = lambda address: int(bitify(address), base=2)
    mask = bits(subnet_mask)
    base = [bits(address) & mask for address in some_addresses]
    base = list(set(base))
    if len(base) == 0:
        raise TypeError("No addresses were given besides the mask.")
    if len(base) > 1:
        raise ValueError("The addresses given fit different networks.")
    return unbitify(format(base[0], 'b').zfill(32))


@memorise
def get_all_possible_addresses() -> list[str]:
    """This method calculates all the possible IPv4 addresses in the current subnet,
    according to this device's IP address and the Subnet Mask, both from `ipconfig()`.

    Returns:
        list[str]: a list of IPv4 addresses, that are all the possible ones in the current network.
    """
    this_device_ip = ipconfig()["IPv4 Address"]
    subnet_mask = ipconfig()["Subnet Mask"]

    this_device_ip, subnet_mask = bitify(this_device_ip), bitify(subnet_mask)
    unique, mutual = subnet_mask.count('0'), subnet_mask.count('1')

    base = this_device_ip[:mutual]
    binary = lambda number: bin(number)[2:].zfill(unique)

    # All possible addresses in binary look like `[mutual part to all in network][special identifier]`,
    # i.e. base + binary representation of i (where i ranges from (0) to (2 ^ unique))
    return [unbitify(base + binary(i)) for i in range(2 ** unique)]


if __name__ == '__main__':
    print("This is a module for doing calculations on IPv4 addresses.")
