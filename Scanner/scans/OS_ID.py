from time import sleep
from threading import Thread

def operating_system_fingerprinting():
    from NetworkStorage import here, SpecialInformation, NetworkEntity
    from PacketSniffer import PacketSniffer

    def _determine_os(packet):
        # do more testing on this
        return "Linux or Android" if packet.ttl <= 64 else "Windows"

    def _fingerprinter():
        while True:
            # for each packet,
            for packet in PacketSniffer():
                # if it originates at some other computer...
                if packet.src == here.ipv4:
                    continue
                entity = NetworkEntity(ip=packet.src)
                # ...that has not yet been OS-ID'd
                if entity in SpecialInformation():
                    continue
                # Then guess what it's OS is, using `_determine_os`, and save it to `SpecialInformation`.
                SpecialInformation()[entity, 'OS'] = _determine_os(packet)
            sleep(10)

    Thread(target=_fingerprinter).start()


if __name__ == '__main__':
    print("This file is responsible for the OS-ID scan-like action.")
    print("This action guesses the Operating System of scanned devices,")
    print("and of devices that sent an IP packet (for any reason) that was sniffed.")
    print("It touches on two pieces of architecture:")
    print("    PacketSniffer - get the packets as input.")
    print("    SpecialInformation - output the OS guess information.")
