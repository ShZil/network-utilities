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


if __name__ == '__main__':
    print("This is a module for doing calculations on IPv4 addresses.")
