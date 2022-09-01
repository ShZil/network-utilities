import json
from scapy.all import conf, get_working_ifaces, sniff, ARP
from subprocess import check_output as read_command
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Arrow
import networkx as nx
from colorsys import hsv_to_rgb
from socket import gethostbyaddr as hostify_base
from socket import herror as hostify_error1
from socket import gaierror as hostify_error2
from threading import Thread
from networkx.exception import NetworkXError as nxerr


__author__ = 'Shaked Dan Zilberman'
ipconfig_data = None
disable_hostify = False
lookup_hostify = {}
G = None
from_scratch = False
def layout(G):
    nodes = ipv4sort(list(G.nodes))
    return nx.circular_layout(nodes)
    # return nx.kamada_kawai_layout(G)
    # return nx.spring_layout(G)  # Fruchterman-Reingold algorithm


### Utility methods
def isipv4(text):
    """Is `text` in IPv4 address format (0.0.0.0 to 255.255.255.255)?"""
    if not isinstance(text, str): return False
    text = text.replace("(Preferred)", "")
    for seg in text.split('.'):
        if not seg.isnumeric():
            return False
    return len(text.split('.')) == 4


def isipv6(text):
    """Is `text` in IPv6 address format (0000:0000:0000:0000:0000:0000:0000:0000 and similar)?"""
    if not isinstance(text, str): return False
    hexdigits = [hex(i)[2:].upper() for i in range(16)]
    text = text.replace("(Preferred)", "")
    max_len = 0
    for seg in text.split(':'):
        for letter in seg:
            if letter.upper() not in hexdigits:
                return False
        if len(seg) > max_len: max_len = len(seg)
    return len(text.split(':')) > 1 and max_len > 2


def ismac(text):
    """Is `text` in MAC address format (00:00:00:00:00:00 to FF:FF:FF:FF:FF:FF)?"""
    if not isinstance(text, str): return False
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


def bitify(address):
    """Returns the address in binary.
    Example: 127.0.0.1 to '01111111000000000000000000000001'"""
    if not isipv4(address):
        return '00000000000000000000000000000000'
    result = ''
    for part in address.split('.'):
        try:
            binary = "{0:08b}".format(int(part, base=10))
        except ValueError:
            # Return 0.0.0.0 if address is invalid
            print("Invalid address:", address)
            return '00000000000000000000000000000000'
        result += binary
    return result


def ipv4sort(addresses):
    """Sorts the given list by the network entities' addresses' actual numerical value."""
    return sorted(addresses, key=lambda x: int(bitify(x.ip), base=2))


### Hostify
def hostify(address):
    """Returns the host name of an IPv4 address. Uses a cache."""
    if disable_hostify:
        return "HOST"
    global lookup_hostify
    try:
        return lookup_hostify[address]
    except KeyError:
        try:
            host = hostify_base(address)[0]
            lookup_hostify[address] = host
            return host
        except (hostify_error1, hostify_error2):
            lookup_hostify[address] = ""
            return ""


def hostify_sync(addresses):
    """Quickly add hosts of an IPv4 list to hostify cache"""
    threads = []
    for address in addresses:
        t = Thread(target=hostify, args=(address,))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()


### NetEntity class
class NetEntity:
    def __init__(self, *args):
        self.mac, self.ip, self.ipv6 = NetEntity._parse(args)
        self.mac = self.mac.replace('-', ':')
        self.name = hostify(self.ip) if self.hasIP() else "Unknown"

    def __str__(self):
        return f"<{self.name} | MAC: {self.mac} | IP: {self.ip} | IPv6: {self.ipv6}>"
    
    def hasMAC(self): return self.mac != '0'

    def hasIP(self): return self.ip != '0'

    def hasIPv6(self): return self.ipv6 != '0'
    
    @staticmethod
    def _parse(args):
        if isinstance(args[0], list):
            args = args[0]
        else:
            args = list(args)
        addresses = []
        for method in [ismac, isipv4, isipv6]:
            address = [address for address in args if method(address)]
            if len(address) > 1:
                raise ValueError("Multiple similar addresses given.")
            elif len(address) == 1:
                addresses.append(address[0])
            else:
                addresses.append('0')
        unknown = set(args) - set(addresses)
        for u in unknown: print("NetEntity init: Unable to resolve format [MAC/IPv4/IPv6] of", u)
        return tuple(addresses)


### IPCONFIG related functions
def read_ipconfig():
    """Read the command `>ipconfig /all` from console and decode it to UTF-8 text."""
    data = read_command(['ipconfig','/all'])
    data = data.split(b'\n')
    decoded = []
    for line in data:
        try:
            decoded.append(line.decode('utf-8'))
        except UnicodeDecodeError:
            continue
    return decoded


def dictify(text):
    """Turn `text` to a python dictionary"""
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


def get_ipconfig() -> tuple[int, str]:
    """Get information from >ipconfig,
    select the first interface with a Default Gateway,
    insert its info as a dictionary into `global ipconfig_data`.
    Returns the error level (0 = fine; anything else is error)."""
    global ipconfig_data

    d = dictify(read_ipconfig())
    try:
        filtered = filter(lambda elem: 'Default Gateway' in elem[1], d.items())
        selected = list(filtered)[0]
    except IndexError:
        print("ERROR: Could not find an interface with a default gateway.")
        print("Check connection to internet. Execute `ipconfig` to debug.")
        return -1, "No internet connection found."
    interface, data = selected[0], selected[1]
    ipconfig_data = clarify_filter(data)
    ipconfig_data["Interface"] = interface
    return 0, ''


def clarify_filter(data):
    """Filters unnecessary parts of the >ipconfig dictionary."""
    result = {}
    for key, value in data.items():
        if isinstance(value, list):
            result[key] = []
            for item in value:
                result[key].append(item.replace("(Preferred)", "").split('%')[0])
            if len(result[key]) == 1:
                result[key] = result[key][0]
            elif len(result[key]) == 0:
                del result[key]
        else:
            if value in ["Yes", "Enabled"]:
                result[key] = True
            elif value in ["No", "Disabled"]:
                result[key] = False
            else:
                result[key] = value.replace("(Preferred)", "").split('%')[0]
    return result


### Automation
def auto_select_interface(ip, description):
    """Select the interface which matches the IP given"""
    for iface in get_working_ifaces():
        if iface.ip == ip:
            conf.iface = iface
    print("Interface:", conf.iface, f'  ( {description} )')


### Colours
def colorify(addresses):
    """Returns a list of colours matching the NetEntities in `addresses` list"""
    return [colorof(address) for address in addresses]


def colorconfig(key):
    """Applies a specific colour palette to the ipconfig headers"""
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


def colorof(address):
    """Colours a specific IPv4 address.
    From #000000 to #FFFFFF."""
    if not isipv4(address): return '#000000'
    network, nettoo, center, device = [int(part) for part in address.split('.')]
    h, s, v = (
        pseudo_random(network + nettoo),
        1 - (center) / 255,
        1 - pseudo_random(device)/4
    )
    r, g, b = hsv_to_rgb(h, s, v)
    x = lambda a: hex(int(a * 255))[2:].zfill(2)
    r, g, b = x(r), x(g), x(b)
    return f'#{r}{g}{b}'


def pseudo_random(value):
    """Selects a pseudo random value based on `value`.
    Most importantly, close `value`s do not yield close results."""
    # Use `295` for fairly random results (high changes between close inputs)
    # Use `256/N` for N distinct colours
    return ((value * 295) % 256) / 255


### File handling
def create_file(path):
    try:
        f = open(path, "x")
    except FileExistsError:
        return


def readall(path):
    create_file(path)
    with open(path, 'r') as file:
        return [line.strip('\n') for line in file.readlines()]
    raise FileNotFoundError()
    return []

### File managment
def save_graph(G, printing=True):
    create_file("graph.txt")
    with open("graph.txt", 'w', encoding="utf-8") as file:
        file.write("Nodes:\n")
        for node in list(G.nodes):
            file.write("    " + node.destruct() + "\n")
        file.write("Edges:\n")
        for edge in list(G.edges):
            file.write("    " + edge[0].destruct() + " > " + edge[1].destruct() + "\n")
    if printing:
        print("\nSaved graph to graph.txt")


def read_graph(printing=True):
    lines = readall("graph.txt")
    nodes = []
    edges = []
    current = None
    for line in lines:
        if "Nodes" in line:
            current = nodes
            continue
        elif "Edges" in line:
            current = edges
            continue
        else:
            current.append(line.strip())
    edges_tuples = []
    for edge in edges:
        try:
            left, right = tuple(edge.split('>'))
        except ValueError:
            print("Invalid edge:", edge)
            continue
        left = NetEntity.restruct(left.strip())
        right = NetEntity.restruct(right.strip())
        edges_tuples.append((left, right))
    real_nodes = []
    for node in nodes:
        real_nodes.append(NetEntity.restruct(node))
    G = nx.DiGraph()
    G.add_nodes_from(real_nodes)
    G.add_edges_from(edges_tuples)
    if printing:
        print("\nRead graph from graph.txt")
    return G



### Graphing
def start_graphing():
    """Commance the graphing."""
    while True:
        render(G, printing=False)
        plt.show()
        save_graph(G, printing=False)


def read_graph(printing=True):
    lines = readall("graph.txt")
    nodes = []
    edges = []
    current = None
    for line in lines:
        if "Nodes" in line:
            current = nodes
            continue
        elif "Edges" in line:
            current = edges
            continue
        else:
            current.append(line.strip())
    edges_tuples = []
    for edge in edges:
        try:
            left, right = tuple(edge.split('>'))
        except ValueError:
            print("Invalid edge:", edge)
            continue
        left = NetEntity.restruct(left.strip())
        right = NetEntity.restruct(right.strip())
        edges_tuples.append((left, right))
    real_nodes = []
    for node in nodes:
        real_nodes.append(NetEntity.restruct(node))
    G = nx.DiGraph()
    G.add_nodes_from(real_nodes)
    G.add_edges_from(edges_tuples)
    if printing:
        print("\nRead graph from graph.txt")
    return G


def render(G, printing=True):
    H = G.copy()
    print("\n----\n")
    nodes = ipv4sort(list(H.nodes))
    edges = list(H.edges)
    if printing:
        print(H)
        print("Nodes:")
        for node in nodes:
            print("    ", node)
        print("Edges:")
        for edge in edges:
            print("    ", edge[0], "↔", edge[1])

    for node in H.copy():
        if do_invisible(node):
            H.remove_node(node)
    pos = layout(H)
    if printing:
        print("\n\n  Created position dictionary.")

    nodes = ipv4sort(list(H.nodes))
    edges = list(H.edges)
    nx.draw_networkx(
        H,
        arrows=True,
        with_labels=False,
        pos=pos,
        node_color=colorify(list(H.nodes)),
        node_size=300,
        connectionstyle="arc3,rad=0.02",
        arrowstyle='<-',
        arrowsize=20,
        edge_color=['#000000' for edge in edges]
    )
    if printing:
        print("  Drawn network.")


    ax = plt.gca()
    ax.margins(0.20)
    ax.set_title('Network Analysis - ARP Display / Shzil')

    data = ipconfig_data
    if data == -1:
        data = {"Has Internet": "False"}

    config_legend(ax, data)
    if printing:
        print("  Added legend.")

    labels(H, pos, nodes)
    if printing:
        print("  Added labels.")

    plt.axis("off")
    plt.subplots_adjust(bottom=0, left=0, right=1, top=0.9)
    if printing:
        print("Graph rendered!")


###### Pyplot helper functions
def config_legend(ax, data):
    """Draw a legend to `ax` containing ipconfig data from `data`"""
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
    additional = {}  # {Color (hex with #): title (str)}
    for color, label in additional.items():
        elements.append(
            Line2D(
                [0],
                [0],
                linewidth=0,
                marker='$→$',
                color=color,
                markersize=8,
                label=label
            )
        )
    ax.legend(handles=elements, prop={'size': 8})


def labels(H, pos, nodes):
    """Add the labels to the rendered graph"""
    hostify_sync([node.ip for node in nodes])
    labels = {
        node: f"{node.mac}\n{node.ip}\n{hostify(node.ip)}"
        for node in nodes
    }
    nx.draw_networkx_labels(H, pos, labels=labels, font_size=8, font_color="black")


### Sniffing
def sniffer():
    sniff(count=-1, prn=graph_it)


def do_invisible(node):
    return False


def graph_it(packet):
    """Graph a packet onto `G`"""
    global G
    print(packet.summary())
    # if ARP not in packet:
    #     return
    # arp = packet[ARP]
    # src_ip = arp.psrc
    # src_mac = arp.hwsrc.upper()
    # dst_ip = arp.pdst
    # dst_mac = arp.hwdst.upper()
    # operation = "Unknown"
    # if arp.op == 1:
    #     operation = "who-has"
    # if arp.op == 2:
    #     operation = "is-at"
    # if not outta_net and not is_in_network(dst_ip):
    #     return
    # msg = f"ARP {operation:7} {'from ' + src_ip:>21} {src_mac} {'to ' + dst_ip:>19} {dst_mac}"
    # print(msg)
    # src = NetEntity(src_mac, src_ip)
    # dst = NetEntity(dst_mac, dst_ip)
    # G.add_node(src)
    # G.add_node(dst)
    # if operation == "is-at":
    #     G.add_edge(dst, src, weight=20)
    # elif operation == "who-has":
    #     if not no_who_has:
    #         G.add_edge(src, dst, weight=1)
    # G = process_graph(G)


### Main 
def main():
    err, msg = get_ipconfig()
    if err != 0:
        print("An error happened.", err, msg)
        return
    here = NetEntity(ipconfig_data["Physical Address"], ipconfig_data["IPv4 Address"], ipconfig_data["IPv6 Address"])
    auto_select_interface(here.ip, ipconfig_data["Description"])
    router = NetEntity(ipconfig_data["Default Gateway"])
    subnet_mask = ipconfig_data["Subnet Mask"]
    with open('ipconfig.json', 'w') as f:
        f.write(json.dumps(ipconfig_data, indent=4))
    print("Default gateway:", router)
    print("Subnet Mask:", subnet_mask)
    print("Here:", here)

    
    global G
    if from_scratch:
        G = nx.DiGraph()
        G.add_node(here)
    else:
        G = read_graph()
    render(G)
    Thread(target=sniffer).start()
    start_graphing()


if __name__ == '__main__':
    main()
