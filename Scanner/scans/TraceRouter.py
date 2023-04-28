from import_handler import ImportDefence
import sys

with ImportDefence():
    from scapy.sendrecv import sr1
    from scapy.layers.inet import IP, ICMP

    from util import threadify
    from NetworkStorage import NetworkStorage
    from ipconfig import ipconfig


def hop(ttl, dst):
    TIMEOUT = 0.1
    REPEATS = 3
    results = set()
    for _ in range(REPEATS):
        packet = IP(ttl=ttl, dst=dst) / ICMP()
        res = sr1(packet, timeout=TIMEOUT, verbose=False)
        if res is None:
            continue
        ip = res[IP].src
        if ip == dst:
            return dst
        results.add(ip)
    if len(results) == 0:
        return 'Timed Out'
    if len(results) >1:
        return 'Undefined'
    return results.pop()

def traceroute(dst):
    ROUTE_MAX = 20
    path = []
    for ttl in range(1, ROUTE_MAX):
        path.append(hop(ttl, dst))
    for previous, address in zip(path, path[1:]):
        if address == 'Timed Out':
            continue
        NetworkStorage().add(ip=address)
        NetworkStorage().connect(previous, address)
    return path
