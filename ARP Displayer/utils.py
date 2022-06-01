from scapy.all import Net, Ether, IP, ICMP, ARP, sr1, srp1, show_interfaces, conf, get_working_ifaces, sniff
from os import system
from os import devnull
import sys
from subprocess import check_output as read_command
from json import dumps
from threading import Thread
from socket import gethostbyaddr as hostify_base
from socket import herror as hostify_error1
from socket import gaierror as hostify_error2
import networkx as nx
from networkx.exception import NetworkXError as nxerr
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from math import ceil
from pyvis.network import Network
import numpy as np
import graphistry
import pylab

__author__ = 'Shaked Dan Zilberman'
connectable = []
dns_servers = []
routes = {}
scan_count = 0
lookup_hostify = {}
global_addresses = []
timeout_index = 0
chains = []
position_generator = {}
G = None
pos = None
unrecognised = []
devices = {}

# True = do network scanning and then render
# False = no internet, just rendering
scan = False
# Number of times to repeat scanning which determines
# connectable IPv4 devices. [TODO 3.2]
# Min = 0. WARNING: Heavy on performance
repeats = 1
# Number of times to repeat scanning from cache
# for connectable IPv4 devices.
cache_repeats = 4
# Completely disable `hostify` by setting this to True
no_hosts = False
# Draw text labels (ip+host name) on Graph for all nodes
do_labels = True
# Time Per Packet (hand-measured!). Only affects time display pre-scanning.
tpp = 0.09
# Timeout for each scapy.sr1. Do not raise too much
timeout = 2
# On the graph, display the name of important nodes?
# i.e. the computer "Here", local area "Router", and "DNS" servers
display_base = False
# How many hex digits allowed for each timedout ghost node?
timeout_digits = 3
# smallest distance in order to choose a node?
smallest_dist = 0.01
# LAYOUT SELECTION. Choose the most-fitting method.
# Ordered by my preferences (top is best).
def layout(G):
    return nx.circular_layout(reversed(ipv4sort(list(G.nodes))))
    # return nx.kamada_kawai_layout(G)
    # return nx.spring_layout(G)
    # return nx.planar_layout(G)
    # return nx.shell_layout(G)
    # return nx.spectral_layout(G)


def ipify(name):
    if isipv4(name):
        return name
    return Net.name2addr(name)


def isipv4(text):
    text = text.replace("(Preferred)", "")
    for seg in text.split('.'):
        if not seg.isnumeric():
            return False
    return len(text.split('.')) == 4


def ismac(text):
    hexdigits = [hex(i)[2:].upper() for i in range(16)]
    text = text.replace("(Preferred)", "")
    text = text.replace(":", "-")
    for seg in text.split('-'):
        if len(seg) != 2:
            return False
        if seg[0].upper() not in hexdigits:
            return False
        if seg[1].upper() not in hexdigits:
            return False
    return len(text.split('-')) == 6


def hop(*, ttl, dst):
    packet = IP(ttl=ttl, dst=dst) / ICMP()
    res = sr1(packet, timeout=timeout, verbose=False)
    return res


def getip(res):
    if res is None:
        return '*'.ljust(17)
    return res[IP].src.ljust(17)


def compact(responses, gateway):
    compacted = [avg_ip(x) for x in responses]
    if len(compacted) >= 2:
        if "Timed out" in compacted[0]:
            compacted[0] = gateway
    return compacted


def avg_ip(x):
    global timeout_index
    ip = 'Timed out'
    for res in x:
        if res is None:
            continue
        ip = res[IP].src
    if ip == 'Timed out':
        ip += hex(timeout_index)[2:].zfill(timeout_digits).upper()
        timeout_index += 1
        if timeout_index > 16 ** timeout_digits:
            raise Exception("Not enough timeout digits. Try to increase")
    return ip


def is_in_ip_block(block, address):
    base = block.split('/')
    base, mask = base[0], base[1]
    mask = ('1' * int(mask)) + ('0' * (32-int(mask)))
    mask = unbitify(mask)
    return is_in_network(base, mask, address)


def special_ip(address):
    blocks = ["0.0.0.0/8", "127.0.0.0/8", "255.255.255.255/32"]
    for block in blocks:
        if is_in_ip_block(block, address):
            return True
    return False


def route(dst, gateway):
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


def print_responses(responses, address):
    msg = ""
    for i in range(len(responses)):
        msg += str(i+1).rjust(2) + ": "
        for response in responses[i]:
            msg += getip(response) + " "
        msg += "\n"
    msg += f"\nFound route to {address}!\n\n"
    print(msg, end="")


def main1():
    # TODO: 1 √ Repurpose tracert.py from Cyber
    name = input("Insert Destination: ")
    dst = ipify(name)
    traced = route(dst, '0.0.0.0')
    print(f"\nTraced route to {dst}")
    print("\n\n\n")
    for milestone in traced:
        print(milestone)


def dictify(text):
    result = {}
    current = None
    mini = None
    for line in text:
        if line.strip() == '':
            continue
        elif line[0].strip() == '':
            if '. :' in line:
                data = line.split(':', 1)
                mini, value = data[0].strip(), data[1].strip()
                mini = mini.strip(' .')
                result[current][mini] = value
            else:
                value = line.strip()
                if not isinstance(result[current][mini], list):
                    result[current][mini] = [result[current][mini]]
                result[current][mini].append(value)
        else:
            current = line.strip().strip(':')
            result[current] = {}
    return result


def print_dictionary(d):
    from pygments import highlight, lexers, formatters
    formatted_json = dumps(d, sort_keys=False, indent=4)
    colorful_json = highlight(formatted_json, lexers.JsonLexer(), formatters.TerminalFormatter())
    print(colorful_json)


def read_ipconfig():
    data = read_command(['ipconfig','/all'])
    data = data.split(b'\n')
    decoded = []
    for line in data:
        try:
            decoded.append(line.decode('utf-8'))
        except UnicodeDecodeError:
            continue
    return decoded


def ipv4filter(data):
    result = {}
    for key, value in data.items():
        if isinstance(value, list):
            result[key] = []
            for item in value:
                if isipv4(item) or ismac(item):
                    result[key].append(item)
            if len(result[key]) == 1:
                result[key] = result[key][0].replace("(Preferred)", "")
            elif len(result[key]) == 0:
                del result[key]
        elif isipv4(value) or ismac(value):
            result[key] = value.replace("(Preferred)", "")
    return result


def main2():
    # TODO: 2 √ Get information from >ipconfig
    # Turn text from ipconfig into dictionary
    d = dictify(read_ipconfig())
    # Select the first interface with a Default Gateway
    try:
        filtered = filter(lambda elem: 'Default Gateway' in elem[1], d.items())
        selected = list(filtered)[0]
    except IndexError:
        print("ERROR: Could not find an interface with a default gateway.")
        print("Check connection to internet. Execute `ipconfig` to debug.")
        return -1
    interface, data = selected[0], selected[1]
    # print("Connection:", interface)
    # print_dictionary(data)

    # Return most reduced information
    return ipv4filter(data)


def count_LAN_possibilities(mask):
    sum = bitify(mask).count('1')
    return 2 ** (32 - sum)


def bitify(address):
    result = ''
    for part in address.split('.'):
        try:
            binary = "{0:08b}".format(int(part, base=10))
        except ValueError:
            if "Timed out" not in address:
                print("Invalid address:", address)
            return bitify('0.0.0.0')
        result += binary
    return result


def unbitify(binary):
    result = ''
    for byte in [binary[i:i+8] for i in range(0, len(binary), 8)]:
        result += str(int(byte, base=2))
        result += '.'
    return result.strip('.')


def bitwiseand(a, b):
    result = ''
    for c, d in zip(a, b):
        c = c == '1'
        d = d == '1'
        result += '1' if c and d else '0'
    return result


def mask_on(a, mask):
    return a[:mask.count('1')]


def ipv4sort(addresses):
    return sorted(addresses, key=lambda x: int(bitify(x), base=2))


def network_unmask(here, mask):
    here, mask = bitify(here), bitify(mask)
    base = mask_on(here, mask)
    max = 2 ** (mask.count('0'))
    return [unbitify(base + bin(i)[2:].zfill(mask.count('0'))) for i in range(max)]


def exists(address):
    # Ping the address, if replies - exists.
    packet = Ether(dst='FF:FF:FF:FF:FF:FF') / ARP(pdst=address)
    response = srp1(packet, timeout=timeout, verbose=False)
    if response is not None:
        if response[ARP].op == 2 and address == response[ARP].psrc:
            connectable.append(address)
            devices[response[ARP].psrc] = response[ARP].hwsrc


def get_all_on(all):
    global connectable
    global scan_count
    threads = []
    connectable = []
    for address in all:
        t = Thread(target=exists, args=(address,))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
    system('cls')
    scan_count += 1
    print(f"Scan #{scan_count} done.\n")
    return connectable


def create(path):
    try:
        f = open(path, "x")
    except FileExistsError:
        return


def readall(path):
    create(path)
    with open(path, 'r') as file:
        return [line.strip('\n') for line in file.readlines()]
    raise FileNotFoundError()
    return []


def get_all_connectable(all_computers):
    global scan_count
    scan_count = 0
    cached = []
    addresses = []

    if cache_repeats > 0:
        cached = readall('addresses.txt')
        print("Cached in addresses.txt:")
        print('   ', '\n    '.join(cached))
        for i in range(cache_repeats):
            addresses += get_all_on(cached)

    for i in range(repeats):
        addresses += get_all_on(all_computers)
    return ipv4sort(list(set(addresses)))


def compress(l, *, last):
    if len(l) == 0:
        return []
    k = []
    count = 0
    prev = l[0]
    for i in l:
        if i != prev:
            k.append(prev + (" * " + str(count) if count > 1 else ''))
            prev = i
            count = 0
        else:
            count += 1
    k.append(prev + (" * " + str(count) if count > 1 else ''))
    if last is not None and prev != last:
        k.append(last)
    return k


def sync_find_routes(addresses, gateway):
    global routes
    routes = {}
    threads = []
    for address in addresses:
        t = Thread(target=add_route, args=(address,gateway))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
    system('cls')
    print(f"Finished finding routes, found {len(routes.items())} routes!")
    return routes


def add_route(address, gateway):
    routes[address] = route(address, gateway)


def hostify(address):
    if no_hosts:
        return "HOST"
    global lookup_hostify
    try:
        return lookup_hostify[address] + '\n' + devices[address].upper()
    except KeyError:
        try:
            host = hostify_base(address)[0]
            lookup_hostify[address] = host
            return host
        except (hostify_error1, hostify_error2):
            lookup_hostify[address] = "Unknown"
            return "Unknown"


def hostify_sync(addresses):
    threads = []
    for address in addresses:
        t = Thread(target=hostify, args=(address,))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()


def main3(data):
    global dns_servers
    # TODO: 3 √ Realise map of local area network.
    # TODO:     3.1 √ Do some Cybery math to list all computers.
    print_dictionary(data)
    print_dictionary({
        "repeats": repeats,
        "cache_repeats": cache_repeats,
        "no_hosts": no_hosts,
        "do_labels": do_labels,
        "timeout": timeout
    })
    possibilities = count_LAN_possibilities(data["Subnet Mask"])
    # If there are more than 1000 possible computers,
    # ensure the user wants to scan and wait this long.
    if possibilities > 1000:
        print(f"This network may have {possibilities} computers. Do you wish to proceed?")
        if input("[Y/N]").upper() != 'Y':
            print("Alright have a good day!")
            print("I shall not scan the network,")
            print("So there's nothing I can do here.")
            return
    eta = int(tpp * possibilities * repeats) if repeats > -1 else 0
    print(f"Estimated time is {eta//60}m{eta%60}s")
    print("A window will not open to accompany you while waiting.")
    input("Press [Enter] to start scanning!")
    # system(f"start cmd /c timeout /t {eta}")
    all_computers = network_unmask(data["IPv4 Address"], data["Subnet Mask"])
    # TODO:     3.2 √ Check which computers actually exist.
    dns_servers = data["DNS Servers"]
    if not isinstance(dns_servers, list):
        dns_servers = [dns_servers]
    addresses = get_all_connectable(all_computers)
    addresses = list(set(addresses))
    addresses = ipv4sort(addresses)
    hostify_sync(addresses)
    for address in addresses:
        address_brackets = f"[{address}]"
        address_brackets = address_brackets.rjust(17, ' ')
        host = hostify(address)
        host = host.ljust(55, ' ')
        print(f"{host} {address_brackets}")
    found = readall('addresses.txt')
    with open('addresses.txt', 'a') as file:
        for address in ipv4sort(list(set(addresses) - set(found))):
            file.write(address + '\n')
    # input("Press [Enter]")
    system('cls')
    print("Here is", data["IPv4 Address"])
    print("Default gateway at", data["Default Gateway"])
    return addresses


def is_in_network(gateway, mask, address):
    gateway, mask, address = bitify(gateway), bitify(mask), bitify(address)
    base = mask_on(gateway, mask)
    network = mask_on(address, mask)
    return network == base


def select_iface():
    show_interfaces()
    iface = input("Select your interface: ")
    if iface.strip() == '':
        iface = "Intel(R) Ethernet Connection I219-LM"
    conf.iface = iface
    print("Chose:", iface)


def colorify(addresses):
    return [colorof(address) if isipv4(address) else '#000000' for address in addresses]


def brighten(color, brightness_factor=1.2):
    rgb = [color[x:x+2] for x in [1, 3, 5]]
    new_rgb = [int(value, 16) * brightness_factor for value in rgb]
    new_rgb = [int(min([255, max([0, i])])) for i in new_rgb]
    return "#" + ''.join([hex(i)[2:].zfill(2).upper() for i in new_rgb])


def colorof(address, display=False):
    if address in unrecognised:
        return '#FF0000'
    import colorsys
    network, nettoo, center, device = [int(part) for part in address.split('.')]
    h, s, v = (
        pseudo_random(network + nettoo),
        1 - (center) / 255,
        1 - pseudo_random(device)/4)
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    x = lambda a: hex(int(a * 255))[2:].zfill(2)
    r, g, b = x(r), x(g), x(b)
    if display:
        print("HSV:", h, s, v)
        print(f'#{r}{g}{b}')
    return f'#{r}{g}{b}'


def colorconfig(key):
    colors = {
        "Physical Address": "#b05d1e",
        "IPv4 Address": "#17d495",
        "Subnet Mask": "#7c79b0",
        "Default Gateway": "#b835b8",
        "DHCP Server": "#8f0000",
        "DNS Servers": "#9dff00"
    }
    try:
        return colors[key]
    except KeyError:
        return "#666666"


def pseudo_random(value):
    # Use `295` for fairly random results (high changes between close inputs)
    # Use `256/N` for N distinct colours
    return ((value * 295) % 256) / 255


def auto_select_interface(ip):
    for iface in get_working_ifaces():
        if iface.ip == ip:
            conf.iface = iface
    print("Interface:", conf.iface)


def remove_ghosts(G, node):
    # Find all connections
    try:
        connected = list(G.neighbors(node))
    except nxerr:
        print("Already gone")
        return
    print(node, end=": ")
    print(connected)
    # Check whether it can be removed
    #     Connects to a single node whose also a ghost; Or
    #     Is completely disconnected; Or
    #     Forms a triangle with two real nodes.
    if len(connected) < 2:
        try:
            G.remove_node(node)
        except nxerr:
            print("Already gone")
    if len(connected) == 1 and "Timed out" in connected[0]:
        remove_ghosts(G, connected[0])
    if len(connected) == 2:
        if "Timed out" not in connected[0] and "Timed out" not in connected[1]:
            if G.has_edge(connected[0], connected[1]):
                try:
                    G.remove_node(node)
                except nxerr:
                    print("Already gone")

def main4():
    global this_device
    global subnet_router
    global G
    global global_addresses
    global unrecognised
    unrecognised = []
    data = main2()
    if data == -1:
        print("No internet connection found. Terminating...")
        return
    ip = data["IPv4 Address"]
    auto_select_interface(ip)
    addresses = main3(data)
    addresses = list(set(addresses) - set(["Timed out", "127.0.0.1"]))
    G = nx.DiGraph()
    G.add_nodes_from(addresses)
    global_addresses = addresses
    subnet_router = main_router = data["Default Gateway"]
    subnet_mask = data["Subnet Mask"]
    this_device = here = data["IPv4 Address"]
    G.add_node(main_router)
    G.add_node(here)

    print("\n\n\n\n")
    hostify_sync(list(G.nodes))
    for node in list(G.nodes):
        name = " "
        if node == main_router:
            name += "Router "
        if node == here:
            name += "Here "
        if isipv4(node):
            print(node + " = " + hostify(node).replace('\n', '@') + name)

    render(G)
    save_graph(G)

    # For some reason, doesn't capture all ARP packets (wireshark displays more)
    sniff(count=-1, lfilter=filtering, prn=graph_it)


def render(G, printing=True):
    addresses = list(G.nodes)
    if printing:
        print(G)
        print("Nodes:")
        for node in ipv4sort(list(G.nodes)):
            print("    ", node)
        print("Edges:")
        for edge in list(G.edges):
            print("    ", edge[0], "↔", edge[1])
    global pos
    pos = layout(G)
    if printing:
        print("\n\n  Created position dictionary.")

    options = {
        "font_size": -1
    }
    nx.draw_networkx(
        G,
        arrows=True,
        with_labels=False,
        pos=pos,
        node_color=colorify(list(G.nodes)),
        node_size=300,
        **options
    )
    if printing:
        print("  Drawn network.")

    try:
        nx.draw_networkx_nodes(
            G,
            pos,
            nodelist=[this_device],
            node_color=[brighten(colorof(this_device))],
            linewidths=2,
            edgecolors=[brighten(colorof(this_device))],
            node_size=400 if do_labels else 200,
            alpha=[0.01]
        )
    except (nxerr, KeyError):
        print("No this_device node in the graph.")

    ax = plt.gca()
    ax.margins(0.20)
    ax.set_title('Network Analysis - ARP Display / Shzil')

    # legendary(ax, addresses)
    data = main2()
    if data == -1:
        data = {"Has Internet": "False"}
    config_legend(ax, data)
    if printing:
        print("  Added legend.")
    if do_labels:
        labels(G, pos, addresses)
    else:
        special_labels(G, pos, addresses)

    if printing:
        print("  Added labels.")

    plt.axis("off")
    plt.subplots_adjust(bottom=0, left=0, right=1, top=0.9)
    if printing:
        print("Graph rendered!")


def draw_network(printing=True):
    plt.close()
    render(G, printing)
    plt.show()


def save_graph(G):
    create("graph.txt")
    with open("graph.txt", 'w') as file:
        file.write("Nodes:\n")
        for node in list(G.nodes):
            file.write("    " + node + "\n")
        file.write("Edges:\n")
        for edge in list(G.edges):
            file.write("    " + edge[0] + ", " + edge[1] + "\n")
        # Specials
        file.write(f"Subnet: {subnet_router}\n")
        file.write(f"Here: {this_device}\n")
        file.write(f"DNS: {', '.join(dns_servers)}\n")
        file.write(f"Addresses: {', '.join(global_addresses)}\n")
    print("\nSaved graph to graph.txt")


def special(address):
    if address == subnet_router and display_base:
        return "\nRouter"
    if address == this_device and display_base:
        return "\nHere"
    if address in dns_servers and display_base:
        return "\nDNS"
    if address in global_addresses and not do_labels:
        return address + '\n' + hostify(address)
    return ""


def legendary(ax, addresses):
    addresses = ipv4sort(addresses)
    colors = colorify(addresses)
    elements = []
    for address, color in zip(addresses, colors):
        elements.append(
            Line2D(
                [0],
                [0],
                marker='o',
                color='w',
                label=address,
                markerfacecolor=color,
                markersize=6
            )
        )
    ax.legend(handles=elements, ncol=ceil(len(addresses) / 32), prop={'size': 7})


def config_legend(ax, data):
    elements = []
    for key, value in data.items():
        if isinstance(value, list):
            info = value
            key = key.rstrip('s')
        else:
            info = [value]
        for element in info:
            if isipv4(element):
                color = colorof(element)
            else:
                color = colorconfig(key)
            elements.append(
                Line2D(
                    [0],
                    [0],
                    marker='o',
                    color='w',
                    label=f"{key}: {element}",
                    markerfacecolor=color,
                    markersize=6
                )
            )
    ax.legend(handles=elements, prop={'size': 8})


def labels(G, pos, addresses):
    hostify_sync(addresses)
    labels = {
        address: f"{address}\n{hostify(address)}{special(address)}"
        for address in addresses
    }
    nx.draw_networkx_labels(G, pos, labels=labels, font_size=10, font_color="black")


def special_labels(G, pos, addresses):
    labels = {
        address: f"{special(address)}"
        for address in addresses
    }
    nx.draw_networkx_labels(G, pos, labels=labels, font_size=13, font_color="black")


def filtering(packet):
    return ARP in packet


def graph_it(packet):
    print(packet.summary())
    if ARP not in packet:
        return
    data = packet[ARP]
    src = data.psrc
    dst = data.pdst
    operation = "Unknown"
    if data.op == 1:
        operation = "who-has"
    if data.op == 2:
        operation = "is-at"
    print("ARP", operation, "from", src, data.hwsrc.upper(), "to", dst, data.hwdst.upper())
    # print(','.join(list(G.nodes)))
    # print(src, dst, src in G and dst in G)
    if src in G and dst not in G:
        G.add_node(dst)
        unrecognised.append(dst)
    if dst in G and src not in G:
        G.add_node(src)
        unrecognised.append(src)
    if not G.has_edge(src, dst):
        if data.op == 2:
            G.add_edge(src, dst, weight=20)
        elif data.op == 1:
            G.add_edge(src, dst, weight=1)
        draw_network(printing=False)


def main5():
    global subnet_router
    global this_device
    global dns_servers
    global global_addresses
    global G
    G = nx.Graph()
    data = readall('graph.txt')
    nodes = []
    edges = []
    current = None
    for line in data:
        if "Nodes" in line:
            current = nodes
            continue
        elif "Edges" in line:
            current = edges
            continue
        elif "Subnet" in line:
            subnet_router = line.split(':')[1].strip()
        elif "Here" in line:
            this_device = line.split(':')[1].strip()
        elif "DNS" in line:
            dns_servers = line.split(':')[1].strip().split(', ')
        elif "Addresses" in line:
            global_addresses = line.split(':')[1].strip().split(', ')
        else:
            current.append(line.strip())

    edges_tuples = []
    for edge in edges:
        edges_tuples.append((edge.split(',')[0].strip(), edge.split(',')[1].strip(), ))

    G.add_nodes_from(nodes)
    G.add_edges_from(edges_tuples)

    # Non-blocking possibly? Otherwise, threads
    render(G)



if __name__ == '__main__':
    # select_iface()  # Manual
    main4()


# TODO: 1 √ Copy code from Network Mapper
# TODO: 2   Change it to fit new needs
# TODO:     2.1   Render MAC addresses as well
# TODO: 3   Improve GUI
