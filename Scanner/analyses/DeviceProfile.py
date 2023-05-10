from typing import Any
from gui.dialogs import get_string, popup


def _match_device(address):
    from NetworkStorage import NetworkStorage, match
    try:
        entity = match(address)
        for item in NetworkStorage():
            if entity.equals(item):
                return item
    except ValueError:
        name = address
        if name == "Unknown":
            return None
        for item in NetworkStorage():
            if item.name == name:
                return item
    return None


def _construct_content(info: dict) -> str:
    from NetworkStorage import nothing
    
    def _transform_item(item: tuple[Any, Any]) -> tuple[Any, Any]:
        key, value = item

        if key in ['mac', 'ipv6']:
            value = value.upper()
        if len(value) > 30:
            value = value[:27] + '...'
        
        if key in ['mac']:
            key = key.upper()
        elif key.startswith('ip'):
            key = 'IP' + key[2:]
        else:
            key = key.title()
        
        return key, value
    info = {
        key: value.upper() if key in ['mac', 'ipv6'] else value
        for key, value in info.items()
    }
    info = dict(map(_transform_item, info.items()))
    markdowned = [
        f"### {key}:\n{value}"
        for key, value in info.items()
        if nothing[key.lower()].lower() != value.lower()
    ]
    return '\n\n'.join(markdowned)


def device_profile(*_):
    address = get_string("Device Profile", "Insert device's MAC / IP / IPv6 address or device name:")
    entity = _match_device(address)
    if entity is None:
        popup("Device Profile", f"The device was not found.\nCheck whether you wrote the address correctly.\nThe address: `{address}`", warning=True)
        return
    regular_info = entity.to_dict()  # contains mac, ip, ipv6, and name.
    from NetworkStorage import SpecialInformation
    special_info = SpecialInformation()[entity]  # contains possible additional information, like OS (from OS-ID), or Device Discovery status, or role (e.g. router, broadcast).
    information = {**regular_info, **special_info}  # merge all information to one dictionary
    popup("Device Profile", _construct_content(information), info=True)


if __name__ == "__main__":
    print("This module contains the `device_profile` function,")
    print("i.e. the code for the Device Profile analysis.")
