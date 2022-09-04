from functools import cache
import json
from math import ceil, exp, sqrt
from scapy.all import conf, get_working_ifaces, sniff, Ether, Dot3, IP, IPv6
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Arrow
import networkx as nx
from colorsys import hsv_to_rgb
from threading import Thread
from networkx.exception import NetworkXError as nxerr

from GraphCache import GraphCache
from NetEntity import NetEntity
from hostify import hostify, hostify_sync
from ipconfig import get_ipconfig
from util import *


__author__ = 'Shaked Dan Zilberman'
past_messages = []
ipconfig_data = None
G = None
_dot = False
here, router = None, None
counter = 0
cache = None

# Ignores cache in initialisation
from_scratch = False
# Selects layout for the graph
def layout(G):
    # return nx.circular_layout(ipv4sort(list(G.nodes)))
    # return nx.kamada_kawai_layout(G, weight="nonexistant")
    return nx.spring_layout(G, weight="nonexistant", k=0.6)  # Fruchterman-Reingold algorithm

### Utility methods


def print_once(*msg, instead=".", sep=" "):
    global _dot
    msg = [str(o) for o in msg]
    if sep.join(msg) in past_messages:
        print(instead, end="")
        _dot = True
        return
    else:
        if _dot:
            if instead != '': print()
            _dot = False
        past_messages.append(sep.join(msg))
    print(sep.join(msg))


def no_weights(G):
    G = G.copy()
    for u, v, d in G.edges(data=True):
        d['weight'] = 1
    return G


def width_from_weight(x):
    """Calculates a width of an edge from its weight."""
    f = 1 - exp(-0.1 * x)
    g = 4 - 2.4 * exp(-0.01 * x * x)
    return 13.2 * f / g


### Automation
def auto_select_interface(ip, description):
    """Select the interface which matches the IP given"""
    for iface in get_working_ifaces():
        if iface.ip == ip:
            conf.iface = iface
    print("Interface:", conf.iface, f'  ( {description} )')


### Colours
def colorify(nodes):
    """Returns a list of colours matching the NetEntities in `nodes` list"""
    colors = []
    for node in nodes:
        if here.sameAs(node):
            colors.append('#00FF00')
        elif node.hasIP():
            colors.append(colorof(node.ip))
        elif node.hasMAC():
            colors.append(colorofmac(node.mac))
        else:
            colors.append("#000000")
    return colors


def colorconfig(key):
    """Applies a specific colour palette to the ipconfig headers"""
    colors = {
        "Physical Address": "#b05d1e",
        "IPv4 Address": "#17d495",
        "Subnet Mask": "#7c79b0",
        "Default Gateway": "#b835b8",
        "DHCP Server": "#8f0000",
        "DNS Servers": "#9dff00",
        "DNS Server": "#9dff00"
    }
    return colors[key]


def colorof(address):
    """Colours a specific IPv4 address.
    From #000000 to #FFFFFF."""
    if not isipv4(address): return '#000000'
    network, nettoo, center, device = [int(part) for part in address.split('.')]
    h, s, v = (
        pseudo_random(network + nettoo),
        1 - (0.5 * center) / 255,
        1 - pseudo_random(device)/4
    )
    r, g, b = hsv_to_rgb(h, s, v)
    x = lambda a: hex(int(a * 255))[2:].zfill(2)
    r, g, b = x(r), x(g), x(b)
    return f'#{r}{g}{b}'


def colorofmac(address):
    """Colours a specific MAC address.
    From #000000 to #FFFFFF."""
    if not ismac(address): return '#000000'
    parts = [int(part, base=16) for part in address.replace('-', ':').split(':')]
    h, s, v = (
        pseudo_random(parts[0] + parts[1]),
        1 - (parts[2] + parts[3]) / 255,
        1 - pseudo_random(parts[4] + parts[5]) / 4
    )
    r, g, b = hsv_to_rgb(h, s, v)
    x = lambda a: hex(int(a * 255))[2:].zfill(2)[:2]
    r, g, b = x(r), x(g), x(b)
    return f'#{r}{g}{b}'


def pseudo_random(value):
    """Selects a pseudo random value based on `value`.
    Most importantly, close `value`s do not yield close results."""
    # Use `295` for fairly random results (high changes between close inputs)
    # Use `256/N` for N distinct colours
    return ((value * 295) % 256) / 255


### Graphing
def start_graphing():
    """Commance the graphing."""
    while True:
        render(G, printing=False)
        plt.show()
        cache.save_graph(G, printing=True)


def render(G, printing=True):
    H = G.copy()
    print("\n----\n")
    nodes = ipv4sort(list(H.nodes))
    edges = list(H.edges)
    if printing:
        print(H)
        print("Nodes:")
        for node in nodes: print("    ", node)
        print("Edges:")
        for edge in edges: print("    ", edge[0], "↔", edge[1])

    for node in H.copy():
        if do_invisible(node):
            H.remove_node(node)
    pos = layout(H)
    if printing: print("\n\n  Created position dictionary.")

    nodes = ipv4sort(list(H.nodes))
    edges = list(H.edges)
    nx.draw_networkx(
        H,
        arrows=True,
        with_labels=False,
        pos=pos,
        node_color=colorify(list(H.nodes)),
        node_size=300,
        edgelist=[]
        # connectionstyle="arc3,rad=0.02",
    )
    if printing: print("  Drawn network.")

    
    nx.draw_networkx_edges(
        H,
        pos,
        width=[max(5 * width_from_weight(edge[2]) / sqrt(counter), 0.2) for edge in H.edges(data='weight')],
        arrowstyle='<-',
        arrowsize=20,
        edge_color=['#000000' for edge in H.edges(data='weight')]
    )
    if printing: print("  Drawn edges.")


    ax = plt.gca()
    ax.margins(0.20)
    ax.set_title('Network Analysis - Communications / Shzil')

    data = ipconfig_data
    if data == -1:
        data = {"Has Internet": "False"}

    config_legend(ax, data)
    if printing: print("  Added legend.")

    labels(H, pos, nodes)
    if printing: print("  Added labels.")

    plt.axis("off")
    plt.subplots_adjust(bottom=0, left=0, right=1, top=0.9)
    if printing: print("Graph rendered!")


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
            try:
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
            except KeyError:
                # print("Could not colour ipconfig option:", key)
                pass
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
    hostify_sync([node.ip for node in nodes if node.hasIP()])
    labels = {}
    for node in nodes:
        available = node.get_available()
        available.insert(0, specials(node))
        available.append(hostify(node.ip))
        try:
            available.remove("")
            available.remove("")
        except ValueError:
            pass
        available.insert(ceil(len(available) / 2), '\n')
        labels[node] = '\n'.join(available)
    nx.draw_networkx_labels(H, pos, labels=labels, font_size=9, font_color="black")


def specials(node):
    if node.hasMAC():
        if node.mac == "FF:FF:FF:FF:FF:FF":
            if node.hasIP() and node.ip.endswith(".255") and is_in_network(node.ip, ipconfig_data):
                return "Local broadcast"
            else:
                return "Broadcast"
    if here.sameAs(node):
        return "Here"
    if here.sameAs(node):
        return "Router"
    return ""


### Graph analysis
def process_graph(G):
    """This method merges equal nodes in `G` and treats their edges."""
    if G is None: return
    for a in list(G.nodes):
        for b in list(G.nodes):
            if a is b:
                continue
            if not isinstance(a, NetEntity) and isinstance(b, NetEntity):
                continue
            if a.sameAs(b):
                merge_nodes(G, a, b)
    return G


def merge_nodes(G, a, b):
    """Merge the node `b` into node `a` in the graph."""
    a.unite(b)
    for u, v, info in list(G.in_edges([b], data=True)):
        G.add_edge(u, a, weight=info['weight'])
    for u, v, info in list(G.out_edges([b], data=True)):
        G.add_edge(a, v, weight=info['weight'])
    try:
        G.remove_node(b)
    except nxerr:
        return


### Sniffing
def sniffer():
    sniff(count=-1, prn=graph_it)


def do_invisible(node):
    # if node.hasMAC():
    #     if node.mac == "FF:FF:FF:FF:FF:FF":
    #         return True
    if node.isEmpty():
        return True
    if not node.hasIP():
        return True
    if is_in_network(node.ip, ipconfig_data):
        return False
    return True


### Main 
def main():
    global ipconfig_data, here, router, G, cache, counter
    ipconfig_data, err, msg = get_ipconfig()
    if err != 0:
        print("An error happened.", err, msg)
        return
    here = NetEntity(ipconfig_data["Physical Address"], ipconfig_data["IPv4 Address"], ipconfig_data["IPv6 Address"])
    auto_select_interface(here.ip, ipconfig_data["Description"])
    router = NetEntity(ipconfig_data["Default Gateway"])
    subnet_mask = ipconfig_data["Subnet Mask"]
    with open('ipconfig.json', 'w') as f:
        f.write(json.dumps(ipconfig_data, indent=4))
    print("Default Gateway:", router)
    print("Subnet Mask:", subnet_mask)
    print("Here:", here)

    cache = GraphCache()
    if from_scratch:
        G, counter = nx.DiGraph(), 0
    else:
        G, counter = cache.read_graph()
    G.add_node(here)
    G = process_graph(G)
    render(G, printing=False)
    Thread(target=sniffer).start()
    start_graphing()


def graph_it(packet):
    """Graph a packet onto `G`"""
    global G
    # print(packet.summary())
    mac = {"src": None, "dst": None}
    if not Ether in packet:
        if Dot3 in packet:
            mac["src"], mac["dst"] = packet[Dot3].src, packet[Dot3].dst
        else:
            print("Unknown packet.")
            packet.show()
    else:
        mac["src"], mac["dst"] = packet[Ether].src, packet[Ether].dst
    ip = {"src": None, "dst": None}
    if IP in packet:
        ip["src"], ip["dst"] = packet[IP].src, packet[IP].dst
    ipv6 = {"src": None, "dst": None}
    if IPv6 in packet:
        ipv6["src"], ipv6["dst"] = packet[IPv6].src, packet[IPv6].dst
    source = NetEntity(mac["src"], ip["src"], ipv6["src"])
    destin = NetEntity(mac["dst"], ip["dst"], ipv6["dst"])
    print_once("SRC:", source, instead='')
    print_once("DST:", destin, instead='')
    G.add_node(source)
    G.add_node(destin)
    G = process_graph(G)
    src, dst = None, None
    for node in list(G.nodes):
        if source.sameAs(node): src = node
        if destin.sameAs(node): dst = node
    if src != None and dst != None:
        if G.has_edge(dst, src):
            G[dst][src]['weight'] += 1
        else:
            G.add_edge(dst, src, weight=1)
        global counter
        if G[dst][src]['weight'] > counter: counter = G[dst][src]['weight']


if __name__ == '__main__':
    main()
