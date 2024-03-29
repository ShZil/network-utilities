from typing import Any
from gui.dialogs import get_string, popup
from ipconfig import ipconfig


def _match_device(address):
    from NetworkStorage import NetworkStorage, SpecialInformation, match
    # Quality of life: `16` would mean `10.0.0.16` if the subnet is `10.0.0.*`.
    # Note, this assumes the subnet mask is `255.255.255.0`.
    # This is usually the case, and can be used with other subnet masks.
    subnet_start = ipconfig()["IPv4 Address"]  # e.g. `10.0.0.1`
    subnet_start = subnet_start.split('.')[:3]  # e.g. `['10', '0', '0']`
    subnet_start = '.'.join(subnet_start) + '.'  # e.g. `10.0.0.`
    try:
        if 0 <= int(address) <= 255:
            address = subnet_start + str(int(address))
    except ValueError:
        pass
    # Try to match the address to a MAC/IPv4/IPv6, if it exists in `NetworkStorage`.
    try:
        entity = match(address)
        for item in NetworkStorage():
            if entity.equals(item):
                return item
    # Try to use the address as a name, if it exists on some entity in `NetworkStorage`.
    except ValueError:
        name = address.lower()
        if name == "unknown":
            return None
        for item in NetworkStorage():
            if item.name.lower() == name:
                return item
    # Try to use the address as a role, if any entity has that role.
    role = address.lower()
    have_roles = SpecialInformation()['role']
    for entity in have_roles:
        if SpecialInformation()[entity, 'role'].lower() == role:
            return entity
    
    try:
        entity = match(address)
        if entity in SpecialInformation():
            return entity
    except ValueError:
        return None
    # If nothing hit, the address' meaning was not understood / the entity was not found.
    return None


def _construct_content(info: dict) -> str:
    from NetworkStorage import nothing

    def _transform_item(item: tuple[str, str]) -> tuple[str, str]:
        key, value = item

        try:
            if nothing[key] == value:
                return '', ''
        except TypeError:  # occurs on properties which `nothing` doesn't have, e.g. `os`. i.e. anything from Special Information.
            pass

        if key in ['mac', 'ipv6']:
            value = value.upper()
        
        if key in ['mac']:
            key = key.upper()
        elif key.startswith('ip'):
            key = 'IP' + key[2:]
        elif not key.isupper():
            key = ' '.join([word if word.isupper() else word.capitalize() for word in key.split(' ')])  # title case, but doesn't affect acronyms.
        
        return key, value

    info = dict(map(_transform_item, info.items()))
    markdowned = [
        f"### {key}:\n`{value}`"
        for key, value in info.items()
        if key != ''
    ]
    return '\n\n'.join(markdowned)


def device_profile(*_):
    """
    The device_profile function is a function that allows you to view the profile of a device.
    The profile contains information about the device, such as its MAC address, IPv4 and IPv6 addresses (if available), name (if available), and role (e.g. router).
    It also contains additional information about the device if it's available, like OS version or Device Discovery status or Vendor.
    
    Args:
        *_: Ignore the arguments passed to the function
    """
    address = get_string("Device Profile", "Insert device's MAC / IPv4 / IPv6 Address, or Device Name, or Role:")
    entity = _match_device(address)
    if entity is None:
        popup("Device Profile", f"The device was not found.\nCheck whether you wrote the address correctly.\nThe address: `{address}`", warning=True)
        return
    regular_info = entity.to_dict()  # contains mac, ip, ipv6, and name.
    from NetworkStorage import SpecialInformation
    special_info = SpecialInformation()[entity]  # contains possible additional information, like OS (from OS-ID), or Device Discovery status, or role (e.g. router).
    information = {**regular_info, **special_info}  # merge all information to one dictionary
    popup("Device Profile", _construct_content(information), info=True)


if __name__ == "__main__":
    print("This module contains the `device_profile` function,")
    print("i.e. the code for the Device Profile analysis.")
