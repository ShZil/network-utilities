from import_handler import ImportDefence
import sys

with ImportDefence():
    from scapy.sendrecv import sendp, AsyncSniffer
    from scapy.layers.l2 import Ether, ARP

    from util import threadify
    from NetworkStorage import NetworkStorage
    from ipconfig import ipconfig


def traceroute(dst, gateway):
    if special_ip(dst):
        responses = []
        print_responses(responses, dst)
        return compact(responses, gateway)
    responses = []
    arrived = False
    for ttl in range(1, route_max):
        responses.append([])
        for i in range(3):
            res = hop(ttl=ttl, dst=dst)
            responses[-1].append(res)
            if res is not None and res[IP].src == dst:
                arrived = True
        if arrived:
            break
    system('cls')
    print_responses(responses, dst)
    return compact(responses, gateway)
