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
        """
        The stopall function stops all running sniffers.
        This is the main purpose of the Sniffer class --
        to keep a list of running sniffers and terminate them,
        when the software closes.
        Technically reusable indefinitely,
        but indended usage is to call just once when the software is closed.
        """

        for sniffer in Sniffer.references:
            if sniffer.running:
                sniffer.stop()
        Sniffer.references = []


if __name__ == '__main__':
    print("This file contains the Sniffer class,")
    print("which extends scapy's AsyncSniffer,")
    print("and upgrades it with a `.stopall` static function.")
