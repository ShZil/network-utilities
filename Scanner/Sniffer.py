from import_handler import ImportDefence
with ImportDefence():
    from scapy.sendrecv import AsyncSniffer

class Sniffer(AsyncSniffer):
    references = []

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        Sniffer.references.append(self)
    
    @staticmethod
    def stopall():
        for sniffer in Sniffer.references:
            if sniffer.running:
                sniffer.stop()
        Sniffer.references = []


if __name__ == '__main__':
    print("This file contains the Sniffer class,")
    print("which extends scapy's AsyncSniffer,")
    print("and upgrades it with a `.stopall` static function.")
