from import_handler import ImportDefence
with ImportDefence():
    from scapy.sendrecv import send
    from scapy.all import IP, UDP, Raw
    
    from time import sleep
    from threading import Thread


DST_PORT = 3581

def reveal_myself():
    from gui.dialogs import get_string
    name = get_string("Reveal Myself As", "Starting Device Discovery\nInsert the name you wish to reveal to others:")
    from globalstuff import terminator
    from NetworkStorage import broadcast
    while not terminator.is_set():
        packet = IP(dst=broadcast.ip)
        packet /= UDP(dport=DST_PORT)
        packet /= Raw(load="Hello there, sir " + name)
        send(packet, verbose=0)
        sleep(3)


class DeviceDiscoveryListener:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            
        return cls._instance

    def __init__(self):
        from PacketSniffer import PacketSniffer
        PacketSniffer().add_observer(self.check_packet)

    def check_packet(self, packet):
        from NetworkStorage import broadcast, SpecialInformation, NetworkStorage, match
        if UDP not in packet:
            return
        if packet[IP].dst != broadcast.ip:
            return
        if packet[UDP].dport != DST_PORT:
            return
        entity = match(packet[IP].src)
        load = packet[UDP].payload.load.decode()
        load = load.split("sir ", 1)[1]
        SpecialInformation()[entity, 'discovery'] = load
        NetworkStorage().add(entity)


if __name__ == '__main__':
    print("This file is responsible for the Device Discovery scan,")
    print("which reveals this computer to others that use this software")
