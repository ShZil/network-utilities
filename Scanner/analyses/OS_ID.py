def operating_system_fingerprinting() -> None:
    """This function does the OS-ID scan-like action.
    It's an infinite action, so this method starts a thread to run that action.
    (Updated: this method creates an observer of PacketSniffer)
    For further explanation, execute this file alone, or read OS-ID's information.
    """
    from NetworkStorage import here, SpecialInformation, NetworkEntity, nothing
    from PacketSniffer import PacketSniffer
    from scapy.all import Ether, IP

    def _determine_os(packet):
        # do more testing on this *************
        return "Linux or Android" if packet.ttl <= 64 else "Windows"

    def fingerprint(packet):
        # for each packet,
        # if it originates at some other computer...
        if packet.src == here.ip:
            return
        entity = NetworkEntity(mac=packet[Ether].src, ip=packet[IP].src, ipv6=nothing.ipv6, name="Unknown")
        # ...that has not yet been OS-ID'd
        if entity in SpecialInformation()['OS']:
            return
        # Then guess what it's OS is, using `_determine_os`, and save it to `SpecialInformation`.
        SpecialInformation()[entity, 'OS'] = _determine_os(packet)
    
    PacketSniffer.add_observer(fingerprint)



if __name__ == '__main__':
    print("This file is responsible for the OS-ID scan-like action.")
    print("This action guesses the Operating System of scanned devices,")
    print("and of devices that sent an IP packet (for any reason) that was sniffed.")
    print("It touches on two pieces of architecture:")
    print("    PacketSniffer - get the packets as input.")
    print("    SpecialInformation - output the OS guess information.")
