from import_handler import ImportDefence

with ImportDefence():
    from scapy.all import sr1, TCP, IP
    from random import randint

    from util import threadify
    from PrintingContexts import InstantPrinting


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


# This is not supposed to be under an `if __name__ == '__main__`. It's called from ./Do TCP Scan.bat.
# If one did execute it from this context, Python would be unable to import util for example, as that's an outside file.
def main(addr=''):
    import ipaddress

    if addr:
        address = addr
    else:
        address = input("Which IP address? ")

    def is_ipv4(string):
        try:
            ipaddress.IPv4Network(string)
            return True
        except ValueError:
            return False

    while not is_ipv4(address):
        print("This does not appear to be a valid IPv4 address.")
        address = input("Which IP address? ")

    try:    
        repeats = int(input("How many repeats? "))
    except ValueError:
        repeats = 3

    try:
        minimum = int(input("Choose min port: "))
        maximum = int(input("Choose max port: "))
        if maximum < minimum:
            raise ValueError("Maximum can't be smaller than minimum.")
        if minimum < 0:
            minimum = 0
        if maximum > 65536:
            maximum = 65536
        global PORT_RANGE
        PORT_RANGE = list(range(minimum, maximum))
    except ValueError:
        pass

    print()
    print(f"Open TCP ports in {address} in range {PORT_RANGE[0]} → {PORT_RANGE[-1]} ({repeats} repeats):")
    with InstantPrinting():
        for port, res in scan_TCP(address, repeats).items():
            if res:
                print(port)
