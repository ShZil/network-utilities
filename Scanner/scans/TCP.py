from import_handler import ImportDefence

with ImportDefence():
    from scapy.all import sr1, TCP, IP
    from random import randint
    
    from util import threadify


# A range for the scanned ports.
PORT_RANGE = list(range(0, 1024))

# Enum-like
OPEN = 0
CLOSE = 1
RESET = 2


def scan_port(ip: str, port: int) -> int:
    seq = randint(0, 1000)
    syn_segment = TCP(dport=port, seq=seq, flags='S')
    syn_packet = IP(dst=ip) / syn_segment
    syn_ack_packet = sr1(syn_packet, timeout=3, verbose=False)
    if syn_ack_packet is None:
        return CLOSE
    else:
        if 'R' in syn_ack_packet[TCP].flags:
            return RESET
        else:
            return OPEN

scan_ports = threadify(scan_port, silent=False)


def scan_TCP(ip: str, repeats: int) -> dict:
    ports = [(ip, port) for port in PORT_RANGE]
    result = {port: False for port in PORT_RANGE}

    for _ in range(repeats):
        one_scan = scan_ports(ports)
        for i, port in enumerate(PORT_RANGE):
            if one_scan[i] == OPEN:
                result[port] = True
        
    
    return result
