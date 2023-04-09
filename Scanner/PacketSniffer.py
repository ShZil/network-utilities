from import_handler import ImportDefence
with ImportDefence():
    from scapy.all import AsyncSniffer


class PacketSniffer:
    def __init__(self):
        self.packets = []
        self.sniff_thread = AsyncSniffer(prn=self._packet_handler)
        self.sniff_thread.start()

    def stop(self):
        if self.sniff_thread:
            self.sniff_thread.stop()
            self.sniff_thread = None

    def get_packets(self):
        return self.packets

    def _packet_handler(self, packet):
        self.packets.append(packet)
