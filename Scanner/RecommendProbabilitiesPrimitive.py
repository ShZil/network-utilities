import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

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


def render_ax1(fig, ax1):
    import matplotlib.pyplot as plt
    import matplotlib.colors as mcolors

    cmap = mcolors.LinearSegmentedColormap.from_list("", ["red", "grey", "green"])
    norm = plt.Normalize(vmin=0, vmax=1)

    pos = nx.circular_layout(G)
    colors = [w['weight'] for v, u, w in G.edges(data=True)]
    nodes = nx.draw_networkx_nodes(G, pos, node_size=100, node_color=list(probabilities.values()), cmap=cmap, norm=norm, ax=ax1)
    edges = nx.draw_networkx_edges(
        G,
        pos,
        node_size=100,
        arrowstyle="->",
        arrowsize=10,
        edge_color=colors,
        edge_cmap=plt.cm.RdYlGn,
        width=2,
        arrows=True,
        ax=ax1
    )
    labels = nx.draw_networkx_labels(G, pos, ax=ax1)

    ax1.set_title("Graph")
    for node in G.nodes():
        ax1.annotate(f"{probabilities[node]:.2f}", xy=pos[node], xytext=(-10, -10), textcoords="offset points")



def render_ax2(fig, ax2):
    adj_matrix = nx.adjacency_matrix(G)
    adj_array = adj_matrix.toarray()
    im = ax2.imshow(adj_array, cmap='coolwarm', interpolation='nearest', vmin=-1, vmax=1)
    ax2.set_title("Adjacency Matrix")
    fig.colorbar(im, ax=ax2)
    for i in range(adj_array.shape[0]):
        for j in range(adj_array.shape[1]):
            ax2.text(j, i, f"{adj_array[i,j]:.2f}", ha="center", va="center", color="black")


def render_graph():
    fig, (ax1, ax2) = plt.subplots(ncols=2, figsize=(12, 6))
    
    render_ax1(fig, ax1)

    render_ax2(fig, ax2)
    
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
