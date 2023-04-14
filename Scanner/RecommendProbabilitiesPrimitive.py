import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.cm as cm

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
    G.add_weighted_edges_from(list((n, n, -0.9) for n in G.nodes))
    # positive values are "Yeah, if you executed `v`, consider executing `u`".
    # negative values are "If you executed `v` please do not execute `u`".
    probabilities = {node: 1 for node in G}


def normalise():
    global probabilities
    s = sum(probabilities.values())
    probabilities = {node: float(i)/s for node, i in probabilities.items()}


def render_ax1(fig, ax1):
    pos = nx.circular_layout(G)
    node_values = list(probabilities.values())

    cmap = cm.RdYlGn
    norm = plt.Normalize(vmin=0, vmax=1)
    sm = cm.ScalarMappable(norm=norm, cmap=cmap)

    node_colors = [sm.to_rgba(value) for value in node_values]
    nodes = nx.draw_networkx_nodes(G, pos, node_size=100, node_color=node_colors, ax=ax1)
    
    colors = [w['weight'] for v, u, w in G.edges(data=True)]
    cmap = plt.cm.RdYlGn
    norm = plt.Normalize(vmin=min(colors), vmax=max(colors))
    sm = plt.cm.ScalarMappable(norm=norm, cmap=cmap)
    sm.set_array([])

    edges = nx.draw_networkx_edges(
        G,
        pos,
        node_size=100,
        arrowstyle="->",
        arrowsize=10,
        edge_color=colors,
        edge_cmap=cmap,
        edge_vmin=min(colors),
        edge_vmax=max(colors),
        width=2,
        arrows=True,
        ax=ax1
    )

    plt.colorbar(sm, ax=ax1)


    y_off = -0.13

    pos_higher = {k: (v[0], v[1]+y_off) for k, v in pos.items()}
    labels = nx.draw_networkx_labels(G, pos_higher, ax=ax1)
    ax1.set_title("Scan's Influence On Each Other")
    
    for node, value in probabilities.items():
        ax1.annotate(f"{value:.2f}", xy=pos[node], xytext=(-10, -15), textcoords="offset points")
    
    sm.set_array(node_values)
    plt.colorbar(sm, ax=ax1)



def render_ax2(fig, ax2):
    adj_matrix = nx.adjacency_matrix(G)
    adj_array = adj_matrix.toarray()
        
    im = ax2.imshow(adj_array, cmap='coolwarm', interpolation='nearest', vmin=-1, vmax=1)
    ax2.set_title("Presented as Adjacency Matrix")
    fig.colorbar(im, ax=ax2)

    node_names = list(G.nodes())
    ax2.set_xticks(range(len(node_names)))
    ax2.set_yticks(range(len(node_names)))
    ax2.set_xticklabels(node_names, rotation=45)
    ax2.set_yticklabels(node_names)
    
    for i in range(adj_array.shape[0]):
        for j in range(adj_array.shape[1]):
            ax2.text(j, i, f"{adj_array[i,j]:.2f}", ha="center", va="center", color="black")


def render_graph():
    fig, (ax1, ax2) = plt.subplots(ncols=2, figsize=(17, 7), gridspec_kw={'width_ratios': [1.3, 1]})
    
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
    normalise()
    

def main():
    construct_graph()
    normalise()
    render_graph()
    step("ICMP Sweep")
    render_graph()


if __name__ == '__main__':
    main()
