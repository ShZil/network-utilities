from import_handler import ImportDefence
import sys

with ImportDefence():
    from scapy.sendrecv import sendp, AsyncSniffer
    from scapy.layers.l2 import Ether, ARP

    from util import threadify
    from NetworkStorage import NetworkStorage
    from ipconfig import ipconfig


def scan_ARP(addresses: list[str]) -> list[str]:
    """This function tests whether it's possible to connect to other IPv4 addresses `addresses`,
    using Address Resolution Protocol (ARP) who-has requests.
    If an is-at response is detected, save the IP and MAC to the NetworkStorage,
    and return only a list of IPs.

    Args:
        addresses (list[str]): the IPv4 addresses to try connecting to.

    Returns:
        list[str]: the IPv4 addresses that sent an is-at response.
    """
    results = []
    appender = lambda x: results.append((x[ARP].hwsrc, x[ARP].psrc))
    filter_is_at_ARP = lambda x: ARP in x and x[ARP].op == 2 and x[ARP].psrc != ipconfig()["IPv4 Address"]
    sniffer = AsyncSniffer(prn=appender, lfilter=filter_is_at_ARP, store=False)
    sniffer.start()

    send_ARP = lambda packet: sendp(packet, verbose=0)
    send_ARP.__name__ = "can_connect_ARP_base"
    packets = [Ether() / ARP(pdst=address) for address in addresses]
    threadify(send_ARP)(packets)

    from scapy.error import Scapy_Exception as NoNpcap
    try:
        sniffer.stop()
    except NoNpcap as e:
        if e.args[0] == "Unsupported (offline or unsupported socket)":
            print("Npcap / WinPcap aren't installed. Please install either one lol")
            sys.exit(1)
        else:
            raise
    
    lookup = NetworkStorage()
    for result in results:
        lookup.add(mac=result[0], ip=result[1])
    
    return [result[1] for result in results]
