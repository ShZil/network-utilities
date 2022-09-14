from scapy.all import Net, IP, ICMP, sr1, show_interfaces, conf, get_working_ifaces
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

# True = do network scanning and then render
# False = no internet, just rendering
scan = True
# Number of times to repeat scanning which determines
# connectable IPv4 devices. [TODO 3.2]
# Min = 0. WARNING: Heavy on performance
repeats = 10
# Number of times to repeat scanning from cache
# for connectable IPv4 devices.
cache_repeats = 0
# Number of times to repeat tracing routes.
# Note: each trace includes 3 checks. This is for information, not reliability.
route_repeats = 3
# Completely disable `hostify` by setting this to True
no_hosts = False
# Allowing self-loops (edge whose `start node == end node`) in graph?
self_loops = False
# Draw text labels (ip+host name) on Graph for all nodes
do_labels = True
# Render the ghost nodes? [Setting this to false
#                          might disconnect some parts of the graph]
show_ghosts = True
# Time Per Packet (hand-measured!). Only affects time display pre-scanning.
tpp = 0.09
# Timeout for each scapy.sr1. Do not raise too much
timeout = 1
# Maximum number of hops in traceroute. Windows uses 30.
route_max = 30
# On the graph, display the IP and Host of destinations?
# (overrides do_labels for certain nodes)
display_destinations = True
# On the graph, display the name of important nodes?
# i.e. the computer "Here", local area "Router", and "DNS" servers
display_base = True
# How careful when guessing which ghost-nodes match?
# 0=no guessing, 1=quite certain, 10=uncertain
# Technical meaning:
#   how many Timed-out nodes allowed in parallel chains between the same ends?
#   max value, any shorter/equal chain will be merged.
guess_ghosts = 35
# How many times to repeat the Timed-out node-chain merging?
chain_removal_repeats = 3
# How many hex digits allowed for each timedout ghost node?
timeout_digits = 5
# smallest distance in order to choose a node?
smallest_dist = 0.01
# LAYOUT SELECTION. Choose the most-fitting method.
# Ordered by my preferences (top is best).
def layout(G):
    return nx.kamada_kawai_layout(G)
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
    packet = IP(dst=address) / ICMP()
    response = sr1(packet, timeout=timeout, verbose=False)
    if response is not None:
        if response[ICMP].type == 0:
            connectable.append(address)


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


def hostify(address, nonone=False):
    if no_hosts:
        return "HOST"
    global lookup_hostify
    try:
        host = lookup_hostify[address]
        if host == "Unknown" and nonone:
            return ""
        return host
    except KeyError:
        try:
            host = hostify_base(address)[0]
            lookup_hostify[address] = host
            return host
        except (hostify_error1, hostify_error2):
            lookup_hostify[address] = "Unknown"
            if nonone:
                return ""
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
        "self_loops": self_loops,
        "do_labels": do_labels,
        "timeout": timeout,
        "route_max": route_max,
        "display_destinations": display_destinations
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
    print("A window will open to accompany you while waiting.")
    input("Press [Enter] to start scanning!")
    system(f"start cmd /c timeout /t {eta}")
    all_computers = network_unmask(data["IPv4 Address"], data["Subnet Mask"])
    # TODO:     3.2 √ Check which computers actually exist.
    dns_servers = data["DNS Servers"]
    if not isinstance(dns_servers, list):
        dns_servers = [dns_servers]
    addresses = get_all_connectable(all_computers) + dns_servers + [addr for addr in readall('add.txt') if isipv4(addr)]
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
    input("\nTracing routes to all computers outside local network. Press [Enter] to confirm.")
    routes = []
    for i in range(route_repeats):
        routes.append(sync_find_routes([a for a in addresses if not is_in_network(data["IPv4 Address"], data["Subnet Mask"], a)], data["Default Gateway"]))
    input()
    system('cls')
    print("Here is", data["IPv4 Address"])
    print("Default gateway at", data["Default Gateway"])


    # TODO:     3.3 √ Trace route (todo1) to every computer.
    for i in range(route_repeats):
        for address in addresses:
            try:
                if is_in_network(data["IPv4 Address"], data["Subnet Mask"], address):
                    print('LAN →', address)
                else:
                    print('→', ' → '.join(compress(routes[i][address], last=address)), end=' ')
            except KeyError:
                print("Unrecognised address")
            print(hostify(address), end='\n\n')
    global global_addresses
    global_addresses = addresses
    return addresses, routes


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


def merge_ghosts(G, node):
    if guess_ghosts == 1:
        if len(list(G.neighbors(node))) != 2:
            return
        for other in list(G.nodes()):
            if other == node:
                continue
            if "Timed out" not in other:
                continue
            if set(list(G.neighbors(node))) == set(list(G.neighbors(other))):
                G.remove_node(node)
    elif guess_ghosts > 1:
        if len(list(G.neighbors(node))) != 2:
            return
        neighbors = list(G.neighbors(node))
        ghosts = [neighbor for neighbor in neighbors if "Timed out" in neighbor]
        reals = [neighbor for neighbor in neighbors if "Timed out" not in neighbor]
        if len(ghosts) != 1 or len(reals) != 1:
            return
        chain = [reals[0], node, ghosts[0]]
        chain = fill_ghost_chain(G, chain, 0)
        if chain == False:
            return
        chains.append(chain)
    else:
        return


def merge_ghosts1(G, node):
    if len(list(G.neighbors(node))) != 2:
        return
    for other in list(G.nodes()):
        if other == node:
            continue
        if "Timed out" not in other:
            continue
        try:
            if set(list(G.neighbors(node))) == set(list(G.neighbors(other))):
                G.remove_node(node)
        except nxerr:
            continue


def fill_ghost_chain(G, chain, i):
    if i >= guess_ghosts - 1:
        return False
    node = chain[-1]
    if len(list(G.neighbors(node))) != 2:
        return False
    neighbors = list(G.neighbors(node))
    ghosts = [neighbor for neighbor in neighbors if "Timed out" in neighbor]
    reals = [neighbor for neighbor in neighbors if "Timed out" not in neighbor]
    if len(reals) > 0:
        chain.append(reals[0])
        return chain
    for ghost in ghosts:
        if ghost not in chain:
            chain.append(ghost)
            break
    return fill_ghost_chain(G, chain, i + 1)


def merge_chains(G, chains):
    for chain in chains:
        # If the chain is a loop, remove it, and replace it with a self-loop
        if chain[0] == chain[-1]:
            G.remove_nodes_from(chain[1:-1])
            chains.remove(chain)
            G.add_edge(chain[0], chain[-1])
            continue
        # If the chain has a parallel one, delete the other one.
        for other in chains:
            if chain is other:
                continue
            if len(chain) == len(other):
                if (chain[0] == other[0] and chain[-1] == other[-1]) or (chain[0] == other[-1] and chain[-1] == other[0]):
                    G.remove_nodes_from(other[1:-1])
                    chains.remove(other)
                    break


def unique_chains(chains):
    chains = ['~'.join(chain) for chain in chains]
    chains = list(set(chains))
    chains = [chain.split('~') for chain in chains]
    for chain in chains:
        for other in chains:
            if chain is other:
                continue
            if set(chain) == set(other):
                chains.remove(other)
    return chains


def remove_semighost(G, node):
    neighbors = list(G.neighbors(node))
    if len(neighbors) != 2:
        return
    a, b = tuple(neighbors)
    if "Timed out" in a or "Timed out" in b:
        return
    neighbors_of_a = list(G.neighbors(a))
    neighbors_of_b = list(G.neighbors(b))
    mutual = [na for na, nb in zip(neighbors_of_a, neighbors_of_b) if na == nb]
    if len(mutual) != 2:
        return
    if node not in mutual:
        return
    other = list(set(mutual) - set([node]))[0]
    if "Timed out" in other:
        return
    print("Removed semighost in favour of", other)
    G.remove_node(node)


def main4():
    global this_device
    global subnet_router
    # TODO: 4 √ Visualise (using NetworkX?)
    data = main2()
    if data == -1:
        print("No internet connection found. Terminating...")
        return
    ip = data["IPv4 Address"]
    auto_select_interface(ip)
    addresses, routes = main3(data)
    addresses = list(set(addresses) - set(["Timed out", "127.0.0.1"]))
    G = nx.Graph()

    # Routes is built like (key=address, value=path to it):
    #    Consider only the path. Connect the first to second, etc.
    G.add_nodes_from(addresses)
    # for i in range(route_repeats):
    #     print_dictionary(routes[i])
    input()
    for i in range(route_repeats):
        for route in routes[i].values():
            if len(route) > 0:
                if route[0] == None:
                    route[0] = main_router
            for i in range(len(route) - 1):
                G.add_edge(route[i], route[i+1])
            if len(route) == 1 and self_loops:
                G.add_edge(route[0], route[0])
    # Connect all in-network devices to router
    subnet_router = main_router = data["Default Gateway"]
    subnet_mask = data["Subnet Mask"]
    for address in addresses:
        if is_in_network(main_router, subnet_mask, address) and address != main_router:
            G.add_edge(address, main_router)
    # Connect self to main_router
    this_device = here = data["IPv4 Address"]
    G.add_edge(here, main_router)
    # Remove self-loops
    if not self_loops:
        G.remove_edges_from(list(nx.selfloop_edges(G)))
    post_process(G)
    print("\n\n\n\n")
    hostify_sync(list(G.nodes))
    for node in list(G.nodes):
        name = " "
        if node == main_router:
            name += "Router "
        if node == here:
            name += "Here "
        if isipv4(node):
            print(node + " = " + hostify(node) + name)

    render(G)
    save_graph(G)


def start_position(*, x, y, n):
    mag = 10 / n
    mag = min(mag, 1)
    global position_generator
    position_generator = {
        "x": x,
        "y": y,
        "i": 0,
        "dirs": [
            (0, -mag),
            (-mag, 0),
            (0, mag),
            (mag, 0)
        ],
        "borders": (0.9, 0.9)
    }
    bx, by = position_generator["borders"]
    if not (x > bx or x < -bx):
        if not (y > by or y < -by):
            print("Invalid start_position (x,y) couple.")
            position_generator["x"] = bx + 0.01


def next_position():
    global position_generator
    i = position_generator["i"]
    dirs = position_generator["dirs"]
    borderx, bordery = position_generator["borders"]
    dx, dy = dirs[i]
    position_generator["x"] += dx
    x = position_generator["x"]
    position_generator["y"] += dy
    y = position_generator["y"]
    if x > borderx and (y > bordery or y < -bordery):
        i += 1
    elif x < -borderx and (y > bordery or y < -bordery):
        i += 1
    position_generator["i"] = i % len(dirs)
    return [x, y]


def draw_interactable(G, pos, ax):
    # from https://stackoverflow.com/questions/12894985/how-to-make-a-click-able-graph-by-networkx

    class AnnoteFinder:  # thanks to http://www.scipy.org/Cookbook/Matplotlib/Interactive_Plotting
        """
        callback for matplotlib to visit a node (display an annotation) when points are clicked on.  The
        point which is closest to the click and within xtol and ytol is identified.
        """
        def __init__(self, xdata, ydata, annotes, axis=None, xtol=None, ytol=None):
            self.data = list(zip(xdata, ydata, annotes))
            if xtol is None:
                xtol = ((max(xdata) - min(xdata))/float(len(xdata)))/2
            if ytol is None:
                ytol = ((max(ydata) - min(ydata))/float(len(ydata)))/2
            self.xtol = xtol
            self.ytol = ytol
            if axis is None:
                axis = pylab.gca()
            self.axis = axis
            self.drawnAnnotations = {}
            # self.links = []

        def __call__(self, event):
            if event.inaxes:
                clickX = event.xdata
                clickY = event.ydata
                # print(dir(event), event.key)
                if self.axis is None or self.axis == event.inaxes:
                    annotes = []
                    smallest_x_dist = smallest_dist
                    smallest_y_dist = smallest_dist

                    for x,y,a in self.data:
                        if abs(clickX-x) <= smallest_x_dist and abs(clickY-y) <= smallest_y_dist:
                            dx, dy = x - clickX, y - clickY
                            annotes.append((dx*dx + dy*dy, x, y, a))
                            # smallest_x_dist = abs(clickX-x)
                            # smallest_y_dist = abs(clickY-y)
                            # print(annotes, 'annotate')
                        # if  clickX-self.xtol < x < clickX+self.xtol and  clickY-self.ytol < y < clickY+self.ytol :
                        #     dx,dy=x-clickX,y-clickY
                        #     annotes.append((dx*dx+dy*dy,x,y, a) )
                    # print(annotes, clickX, clickY, self.xtol, self.ytol)
                    if annotes:
                        distance, x, y, annote = sorted(annotes, key=lambda tup: tup[0])[0]
                        self.drawAnnote(event.inaxes, x, y, annote)
                    else:
                        # clear annotations
                        self.clearAnnotes(event.inaxes)
                    # print(plt.isinteractive())
                    plt.ion()  # idk but it works. it might still work if I remove it. I'm just too lazy to check

        def drawAnnote(self, axis, x, y, annote):
            if (x, y) in self.drawnAnnotations:
                text, marker = self.drawnAnnotations.pop((x, y))
                text.set_visible(False)
                marker.set_visible(False)
            else:
                t = axis.text(x, y-0.003, f"  {annote}\n  {hostify(annote) if isipv4(annote) else 'Not IPv4'}")
                color = brighten(colorof(annote)) if isipv4(annote) else '#FF0000'
                m = axis.scatter([x], [y], marker='*', c=color, zorder=3)
                self.drawnAnnotations[(x, y)] = (t, m)
            self.axis.figure.canvas.draw()

        def clearAnnotes(self, axis):
            for position, (text, marker) in self.drawnAnnotations.items():
                marker.set_visible(False)
                text.set_visible(False)
            if len(self.drawnAnnotations) > 0:
                self.axis.figure.canvas.draw()
            self.drawnAnnotations = {}

    x, y, annotes = [], [], []
    for key in pos:
        d = pos[key]
        annotes.append(key)
        x.append(d[0])
        y.append(d[1])

    af = AnnoteFinder(x, y, annotes)
    pylab.connect('button_press_event', af)

    # pylab.show()

def render(G):
    addresses = list(G.nodes)
    print(G)
    print("Nodes:")
    for node in ipv4sort(list(G.nodes)):
        print("    ", node)
    print("Edges:")
    for edge in list(G.edges):
        print("    ", edge[0], "↔", edge[1])
    pos = layout(G)
    print("\n\n  Created position dictionary.")

    # Move isolated nodes
    isolated = list(nx.isolates(G))
    start_position(x=0.95, y=0.95, n=len(isolated))
    for node in isolated:
        pos[node] = np.asarray(next_position())
    # print("\n{")
    # for address in ipv4sort(isolated):
    #     print(f"    \"{address}\": @{pos[address]},")
    # print("}")
    options = {
        "font_size": -1
    }
    node_size = 300 if do_labels else 80
    ghost_nodes = [node for node in list(G.nodes) if not isipv4(node)]
    H = G.copy()
    copy_addresses = addresses
    if not show_ghosts:
        H.remove_nodes_from(ghost_nodes)
        copy_addresses = [address for address in addresses if address not in ghost_nodes]

    nx.draw_networkx(
        H,
        arrows=False,
        with_labels=False,
        pos=pos,
        node_color=colorify(copy_addresses),
        node_size=node_size,
        **options
    )
    print("  Drawn network.")
    if show_ghosts:
        nx.draw_networkx_nodes(
            G,
            pos,
            nodelist=ghost_nodes,
            node_color='#FFFFFF',
            linewidths=1,
            edgecolors='#000000',
            node_size=node_size
        )
        print("  Drawn ghost nodes.")
    percent = 100 * len(ghost_nodes) / len(list(G.nodes))
    print(f"Ghost percentage is {percent:.2f}%")

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
    ax.set_title('Network Analysis / Shzil')

    # legendary(ax, addresses)
    data = main2()
    if data == -1:
        data = {"Has Internet": "False"}
    config_legend(ax, data)
    print("  Added legend.")
    if do_labels:
        labels(G, pos, addresses)
    else:
        special_labels(G, pos, addresses)
    print("  Added labels.")

    plt.axis("off")
    plt.subplots_adjust(bottom=0, left=0, right=1, top=1)
    draw_interactable(H, pos, ax)
    plt.show()
    print("Graph rendered!")


def dynamic_render(G):
    net = Network()
    net.from_nx(G)
    net.show('nx.html')


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
    if address in global_addresses and display_destinations and not do_labels:
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
        address: f"{address}\n{hostify(address, nonone=True)}{special(address)}"
        for address in addresses
    }
    nx.draw_networkx_labels(G, pos, labels=labels, font_size=10, font_color="black")


def special_labels(G, pos, addresses):
    if display_destinations:
        hostify_sync(addresses)
    labels = {
        address: f"{special(address)}"
        for address in addresses
    }
    nx.draw_networkx_labels(G, pos, labels=labels, font_size=13, font_color="black")


def post_process(G):
    processes = {
        "process ghosts": True
    }

    if processes["process ghosts"]:
        # Remove ghost trails. (Failed traceroutes)
        for node in list(G.nodes):
            if "Timed out" in node:
                remove_ghosts(G, node)
        # Guess which ghosts to merge:
        global chains
        for i in range(chain_removal_repeats):
            if guess_ghosts >= 1:
                for node in list(G.nodes):
                    if "Timed out" in node:
                        merge_ghosts1(G, node)
            chains = []
            for node in list(G.nodes):
                if "Timed out" in node:
                    merge_ghosts(G, node)
            chains = unique_chains(chains)
            for chain in chains:
                print('~'.join(chain))
            merge_chains(G, chains)
        # Remove a specific case where a server replied on one traceroute,
        # but not on another
        for node in list(G.nodes):
            if "Timed out" in node:
                remove_semighost(G, node)

    # If any post-process was applied,
    # the graph was likely changed and cache should be updated.
    if any(processes.values()):
        save_graph(G)


def main5():
    global subnet_router
    global this_device
    global dns_servers
    global global_addresses
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

    post_process(G)

    render(G)
    # dynamic_render(G)


if __name__ == '__main__':
    # select_iface()  # Manual
    if scan:
        main4()
    else:
        main5()


# TODO: 1 √ Repurpose tracert.py from Cyber
# TODO: 2 √ Get information from >ipconfig
# TODO: 3 √ Realise map of local area network
# TODO:     3.1 √ Do some Cybery math to list all computers.
# TODO:     3.2 √ Check which computers actually exist.
# TODO:     3.3 √ Trace route (todo1) to every computer.
# TODO: 4 √ Visualise (using NetworkX?)
# TODO:     4.1 √ Colours! (IPv4 → Number → colour for the node).
#             *   Close addresses (similar networks) -- closer colours
# TODO: 5 √ Cache and re-render of graph

# TODO: * √ Bug fix: tracing route to localhost doesn't work
# TODO: *   Bug fix: tracing routes on WiFi doesn't work
# TODO: *   Bug fix: setting repeats=-1 displays time as 0m0s which is wrong
# TODO: *   GUI improvement: add wait.py animation to replace timeout /t
# TODO: *   Get public IP of network/router/whatever you wanna call it
# TODO: *   Ports: port scan? [could be interpreted as attack]
# TODO: * √ Save graph and its nodes and edges to some cache.
# TODO: *   Printable versions (image/png, console/text)
# TODO: *   Another viewing library with HTML + motion
# TODO: * √ Clickity bickity on graphity
# TODO: *   Path taken to get to selected (clicked-on) node
# TODO: *   Subnet mask guesser; display probable networks
# TODO: *   Addresses from add.txt shouldn't be saved to addresses.txt
# TODO: * √ no tracert to local network!
# TODO: * √ Routes (branches) which end only with ghosts should be removed
# TODO: *   Display graph on a map!!! like one of earth
# TODO: * √ Beautify: disable printing for traceroute & pings. Yes, IK it's not perfect.
# TODO: *   Beautify: Make a GUI, animations, and such.
# TODO: *   Bug fix: remove semi-ghosts doesn't seem to work in all cases
# TODO: *   Beautify: Display ipconfig info in the legend!
# TODO: *   Beautify: How many nodes did each ghost-filter remove?
# TODO: * √ Beautify: Merge reasonably-identical ghosts
# TODO: *   Beautify: Reposition completely disconnected nodes to form a box around the graph
# TODO: *   Edge attribute `weight` according to response time. Note: it affects layout_spring
# TODO: *   Figure some way to select a node and know info about it
# TODO: * √ Beautify: Seprate different timeout nodes (of different routes) and render a "ghost" node there (white bg black outline)
# TODO: * √ Beautify: Route prints go on top of each other. Queue of printing?
# TODO: * √ Beautify: When displaying the graph, add '\nHOST' to each address node + if important (Router/Here/DNS)
# TODO: * √ Performance: Make an Address-To-Name lookup table
# TODO: * √ Performance: Hostify with threading once rendering graph
# TODO: * √ Conveniency: Remove manual interface selection, choose interface which has correct self-IP
