from threading import Thread
from PacketSniffer import PacketSniffer
from gui.dialogs import get_string, popup


def device_profile(*a):
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

    def _construct_content(info: dict):
        return '\n\n'.join([f"### {key.upper()}:\n{value}" for key, value in info.items()])

    from NetworkStorage import SpecialInformation
    address = get_string("Device Profile - Choose Address", "Insert device's MAC/IP/IPv6 address or name:")
    entity = _match_device(address)
    if entity is None:
        popup("Device Profile", f"The device was not found.\nCheck whether you wrote the address correctly.\nThe address: `{address}`", warning=True)
        return
    regular_info = entity.to_dict()
    special_info = SpecialInformation()[entity]
    information = {**regular_info, **special_info}
    # print(_construct_content(information))
    try:
        popup("Device Profile", _construct_content(information), info=True)
    except Exception as e:
        print(e)


def log_packets():
    from gui.dialogs import popup
    packets = [str(packet.summary()) for packet in PacketSniffer()]
    packets = ['</td><td>'.join(packet.replace('>', '&gt;').replace('<', '&lt;').split('/')) for packet in packets]
    packets = [f"<tr><td>{packet}</td></tr>" for packet in packets]
    packets = '\n'.join(packets)
    packets = f"<table>{packets}</table>"
    popup("Packets", packets, info=True)


if __name__ == "__main__":
    print("This module contains analyses.")
    print("An analysis is like a Scan, but passive (no packets), and inside Know screen.")
