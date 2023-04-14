import networkx as nx
import numpy  # Sure?

G = nx.DiGraph()
probabilities = {}

def construct_graph():
    global probabilities, G
    G.add_nodes_from(["ARP Sweep", "ICMP Sweep", "ARP Live", "ICMP Live", "OS-ID", "Public Address"])
    G.add_weighted_edges_from([
        # (v, u, w: float)
        ("ARP Sweep", "ARP Live", 0.4),
        ("ICMP Sweep", "ICMP Live", 0.4),
        ("ARP Sweep", "ICMP Sweep", 0.2),
        ("ICMP Sweep", "ARP Sweep", 0.3),
        ("ARP Live", "ICMP Live", 0.05),
        ("ICMP Sweep", "OS-ID", 0.5),
        ("ICMP Live", "OS-ID", 0.6)
    ])
    G.add_weighted_edges_from(list((n, n, -1) for n in G.nodes))
    # positive values are "Yeah, if you executed `v`, consider executing `u`".
    # negative values are "If you executed `v` please do not execute `u`".
    probabilities = {node: 1 for node in G}


def normalise():
    global probabilities
    s = sum(probabilities.values())
    probabilities = {node: float(i)/s for node, i in probabilities.items()}
    

def render_graph():
    import matplotlib.pyplot as plt
    import matplotlib.colors as mcolors
    pos = nx.circular_layout(G)
    colors = [w['weight'] for v, u, w in G.edges(data=True)]
    print("Edge colours:", colors)
    print("Node probabilities:", probabilities)
    delta_p = -1 / len(probabilities)
    nodes = nx.draw_networkx_nodes(G, pos, node_size=100, node_color=[p + delta_p for p in probabilities.values()], cmap=plt.cm.RdYlGn)
    edges = nx.draw_networkx_edges(
        G,
        pos,
        node_size=100,
        arrowstyle="->",
        arrowsize=10,
        edge_color=colors,
        edge_cmap=plt.cm.RdYlGn,
        width=2,
        arrows=True
    )
    labels = nx.draw_networkx_labels(G, pos)
    plt.show()


def step(node):
    edges = G.edges(node, data=True)
    edges = [(dst, data['weight']) for src, dst, data in edges]
    print(edges)
    p = probabilities[node]
    for scan, weight in edges:
        probabilities[scan] += weight * p
        print(f"Changed {scan} by {weight * p}")
    

def main():
    construct_graph()
    normalise()
    render_graph()
    step("ARP Live")
    normalise()
    render_graph()


if __name__ == '__main__':
    main()
