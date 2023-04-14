import networkx as nx
import numpy  # Sure?

G = nx.DiGraph()
probabilities = []

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
    probabilities = [1 / len(G) for node in G]
    

def render_graph():
    import matplotlib.pyplot as plt
    pos = nx.circular_layout(G)
    colors = [w['weight'] for v, u, w in G.edges(data=True)]
    print(colors)
    print(probabilities)
    nodes = nx.draw_networkx_nodes(G, pos, node_size=100, node_color=probabilities, cmap=plt.cm.RdYlGn)
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


def main():
    construct_graph()
    render_graph()
    # step
    # renormalise
    # render
        


if __name__ == '__main__':
    main()
