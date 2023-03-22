from import_handler import ImportDefence

with ImportDefence():
    from util import threadify, barstyle, shift, render_opacity, InstantPrinting, TablePrinting, JustifyPrinting, AutoLinebreaks
    from ipconfig import ipconfig
    from NetworkStorage import NetworkStorage
    from colors import Colors
    from hostify import hostify, hostify_sync
    from ip_handler import subnet_address_range, subnet_slash_notation
    
    from queue import Queue
    from threading import Thread
    from time import sleep
    from math import floor
    import os

    from scapy.sendrecv import sr1
    from scapy.layers.inet import IP, ICMP


continuous_pause_seconds = 1.1
save_count = 60

def can_connect_ICMP_base(address: str) -> bool:
    """This function tests whether it's possible to connect to another IPv4 address `address`,
    using an Internet Control Message Protocol (ICMP) ping request.
    If the address given is localhost, `return False`.

    Args:
        address (str): the IPv4 address to try pinging.

    Returns:
        bool: a boolean indicating whether the echo ping had been successfully sent, and a response was received.
    """
    if (address == ipconfig()["IPv4 Address"]): return False
    packet = IP(dst=address) / ICMP()
    response = sr1(packet, verbose=0, timeout=1)
    lookup = NetworkStorage()
    if response is not None:
        # print(response[IP].show())
        if response[ICMP].type == 0:
            lookup.add(ip=response[IP].src)
            return True
    return False

can_connect_ICMP_base.options = {"format": barstyle("Dot Fill")}
scan_ICMP = threadify(can_connect_ICMP_base)


def calculate_opacity(connections: list[bool]) -> float:
    """This function calculates the opacity of a given connection list (a list of booleans indicating some contacting attempts' successes),
    according to a probabilistic formula derived in an attached TXT file.

    Args:
        connections (list[bool]): a list of contact attempts' successes, taking the form of `[...True, True, False, True, False]`

    Returns:
        float: a value between `0.0` (disconnected) and `1.0` (connected) representing certainty that the device is still connected (a.k.a its opacity).
    """
    
    # #   │++                             │+++++++++ 
    # #   │  ++                           │         +++++  
    # #   │    ++                         │              ++
    # #   │      ++                       │                ++ 
    # #   │        ++                =>   │                  + 
    # #   │          ++                   │                   + 
    # #   │            ++                 │                    +
    # #   │              ++               │                    + 
    # #   │                ++             │                     +
    # #   │                  ++           │                     + 
    # # ──┼─────────────────────────    ──┼────────────────────────
    # #   │                               │

    # GONE_AFTER: int = 11

    # if len(connections) == 0: return 0.0
    # if not any(connections): return 0.0
    # distance_to_last = list(reversed(connections)).index(True)
    # # Change this function? (see art above)
    # opacity = 1.0 - distance_to_last / GONE_AFTER
    # if opacity < 0: return 0.0
    # # Maybe calculate the average amount of disconnected time for devices? And not just choose some random numbers?
    # return opacity
    if len(connections) == 0: return 1.0
    if not any(connections): return 0.0
    n = list(reversed(connections)).index(True)
    a = connections.count(True) / len(connections)
    return a ** n


def scan_ICMP_continuous(addresses, all_possible_addresses, parallel_device_discovery=True, compactness=0):
    # compactness=0 -> "255.255.255.255 (Smartphone-Galaxy-S90-5G) █████ █    ███████ █  ███ ████┅  [█]".
    # compactness=1 -> "255.255.255.255 (Smartphone-Galaxy-S90-5G) [█]".
    # compactness=2 -> "<ff:ff:ff:ff:ff:ff | 255.255.255.255 | Smartphone-Galaxy-S90-5G>" (text colour changes depending on opacity).
    # otherwise -> "255.255.255.255 (Smartphone-Galaxy-S90-5G)" (text colour changes depending on opacity).
    if not isinstance(addresses, list): addresses = list(addresses)
    table = {address: [] for address in addresses}
    waiting = Queue()
    
    network = subnet_address_range(ipconfig()["Subnet Mask"], ipconfig()["IPv4 Address"])
    # from NetworkStorage import router
    # network = subnet_slash_notation(ipconfig()["Subnet Mask"], router.ip)

    if parallel_device_discovery:
        # How many threads should be dedicated to the detection of new devices?
        # The iteration shifts in different threads by `shifting = thread_index * 71 mod 255`, to ensure efficiency.
        # Range of values: 1 to 18 (inclusive).
        # Optimal values: 18, 6, 3, 2, 1
        SCANNER_THREADS = 18

        def new_devices(order: int):
            all_addresses = shift(all_possible_addresses, 71*order)
            while True:
                for address in all_addresses:
                    if address in table.keys(): continue
                    if address in waiting.queue: continue
                    if can_connect_ICMP_base(address):
                        waiting.put(address)

        for i in range(SCANNER_THREADS):
            Thread(target=new_devices, args=(i, )).start()
    

    def resolve_queue():
        lookup = NetworkStorage()
        while not waiting.empty():
            address = waiting.get()
            if address not in addresses:
                addresses.append(address)
                lookup.add(ip=address)
                print("Adding address", address)
    

    def sweep_scan():
        for address, online in zip(addresses, scan_ICMP(addresses)):
            if address not in table:
                table[address] = []
            table[address].append(online)
            if len(table[address]) > save_count:
                table[address] = table[address][-save_count:]
    

    def print0(sorted_table):
        print(f"Connection testing (ICMP ping) to {network}\n")

        with InstantPrinting():
            example_length = len("255.255.255.255 (Smartphone-Galaxy-S90-5G)")
            bar_length = os.get_terminal_size().columns - example_length - len(":  ") - len("┅  [ ]")
            for address in sorted_table:
                print(
                    f"{address} ({hostify(address)}): ".rjust(example_length),
                    (''.join(['█' if x else ' ' for x in table[address][-bar_length:]]) + "┅ ").rjust(bar_length),
                    f"[{render_opacity(100 * calculate_opacity(table[address]))}]"
                )
            print()
    

    def print1(sorted_table):
        print(f"Connections (ICMP ping) to {network}\n")
        with TablePrinting():
            for address in sorted_table:
                print(
                    address,
                    f"({hostify(address)})",
                    f"[{render_opacity(100 * calculate_opacity(table[address]))}]"
                )
    

    def print2(sorted_table):
        print(f"ICMP ping sweep over {network}\n")
        with JustifyPrinting():
            opacities = [Colors.BLACK, Colors.DARK_GRAY, Colors.LIGHT_GRAY, Colors.LIGHT_WHITE]
            data = NetworkStorage().organise('ip')
            for address in sorted_table:
                opacity = calculate_opacity(table[address])
                index = floor(opacity * (len(opacities) - 1))
                if index == 0: continue
                color = opacities[index]
                try:
                    print(f"{color}{data[address]}{Colors.END}  ")
                except KeyError:
                    print(f"{color}{address} ({hostify(address)}){Colors.END}  ")
    

    def print3(sorted_table):
        print(f"ICMP continuous: {network}\n")
        with AutoLinebreaks():
            opacities = [Colors.BLACK, Colors.DARK_GRAY, Colors.LIGHT_GRAY, Colors.LIGHT_WHITE]
            for address in sorted_table:
                opacity = calculate_opacity(table[address])
                index = floor(opacity * (len(opacities) - 1))
                if index == 0: continue
                color = opacities[index]
                print(f"{color}{address} ({hostify(address)}){Colors.END}  ")


    while True:
        sleep(continuous_pause_seconds)

        resolve_queue()
        sweep_scan()
        
        hostify_sync(list(table.keys()))
        # os.system("cls")
        
        sorted_table = sorted(table.keys(), key=lambda x: int(''.join(x.split('.'))))

        # try:
        #     [print0, print1, print2][compactness](sorted_table)
        # except KeyError:
        #     print3()


