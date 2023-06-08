from import_handler import ImportDefence
with ImportDefence():
    import networkx as nx
    import matplotlib.pyplot as plt
    import matplotlib.colors as mcolors
    import matplotlib.cm as cm
    import random
from db import get_scans

R = nx.DiGraph()
probabilities = {}

# For `step(node)`
dp = 0.09  # change the `prev`-`node` link by this amount
maxp = 0.99  # however, if it's gotten greater than `maxp`,
reduction_factor = 0.9  # reduce it by multiplying it by `reduction_factor`.


def construct_graph():
    """
    The construct_graph function is used to construct the graph that will be used for the "Markov Chain".
    The graph has some nodes: "ARP Sweep", "ICMP Sweep", "Live ARP", "Live ICMP", "TCP Ports", "Public Address", "Trace Route", and "Reveal Myself".
    Each node represents a step in our attack process. The edges represent probabilities of going from one step to another.
    
    :return: A graph with nodes and edges
    """
    
    global probabilities, R
    R.add_nodes_from(get_scans())
    R.add_weighted_edges_from([
        # (v, u, w: float)
        ("ARP Sweep", "Live ARP", 0.4),
        ("ICMP Sweep", "Live ICMP", 0.4),
        ("ARP Sweep", "ICMP Sweep", 0.2),
        ("ICMP Sweep", "ARP Sweep", 0.3),
        ("Live ARP", "Live ICMP", 0.05),
        ("ARP Sweep", "TCP Ports", 0.2),
        ("ICMP Sweep", "TCP Ports", 0.2),
        ("Live ARP", "TCP Ports", 0.2),
        ("Live ICMP", "TCP Ports", 0.2),
        ("Trace Route", "TCP Ports", 0.5)
    ])
    R.add_weighted_edges_from(list((n, n, -1 if n.startswith("Live") else -0.5) for n in R.nodes))  # negative diagonal
    # positive values are "Yeah, if you executed `v`, consider executing `u`".
    # negative values are "If you executed `v`, please do not execute `u`".
    probabilities = {node: 0 if node == 'Reveal Myself' else 1 for node in R}


def normalise():
    """
    The normalise function takes the dictionary of probabilities and divides each value by the sum of all values.
    This is done to ensure that all probabilities add up to 1.
    
    :return: A dictionary of the probabilities for each node
    """
    global probabilities
    s = sum(probabilities.values())
    probabilities = {node: float(i) / s for node, i in probabilities.items()}


def render_ax1(fig, ax1):
    """
    The render_ax1 function takes a figure and an axis as arguments.
    It then uses the networkx library to draw the graph R on that axis,
    using a circular layout. The node colors are determined by their probabilities,
    and the edge colors are determined by their weights.
    
    :param fig: Pass the figure to the function
    :param ax1: Specify which axis to draw the graph on
    """
    
    pos = nx.circular_layout(R)
    node_values = list(probabilities.values())

    # Node colormap and colorbar
    cmap_nodes = cm.PiYG_r
    norm_nodes = plt.Normalize(vmin=0, vmax=1)
    sm_nodes = cm.ScalarMappable(norm=norm_nodes, cmap=cmap_nodes)

    node_colors = [sm_nodes.to_rgba(value) for value in node_values]
    nodes = nx.draw_networkx_nodes(R, pos, node_size=100, node_color=node_colors, ax=ax1)

    # Edge colormap and colorbar
    colors = [w['weight'] for v, u, w in R.edges(data=True)]
    cmap_edges = plt.cm.coolwarm_r
    norm_edges = plt.Normalize(vmin=-1, vmax=1)
    sm_edges = plt.cm.ScalarMappable(norm=norm_edges, cmap=cmap_edges)
    sm_edges.set_array([])

    edges = nx.draw_networkx_edges(
        R,
        pos,
        node_size=100,
        arrowstyle="->",
        arrowsize=10,
        edge_color=colors,
        edge_cmap=cmap_edges,
        edge_vmin=min(colors),
        edge_vmax=max(colors),
        alpha=[min(abs(c) * 2, 1) for c in colors],
        width=2,
        arrows=True,
        ax=ax1
    )

    plt.colorbar(sm_edges, ax=ax1, label='Edge weights')
    plt.colorbar(sm_nodes, ax=ax1, label='Node probabilities')

    y_off = -0.13

    pos_higher = {k: (v[0], v[1] + y_off) for k, v in pos.items()}
    labels = nx.draw_networkx_labels(R, pos_higher, ax=ax1)
    ax1.set_title("Scan's Influence On Each Other")

    for node, value in probabilities.items():
        ax1.annotate(f"{value:.2f}", xy=pos[node], xytext=(-10, -15), textcoords="offset points")


def render_ax2(fig, ax2):
    """
    The render_ax2 function takes a figure and an axis as arguments.
    It then creates an adjacency matrix from the graph R, which is defined in the global scope.
    The adjacency matrix is converted to a numpy array, and then plotted using imshow().
    The title of the plot is set to &quot;Presented as Adjacency Matrix&quot;.  The colorbar() function was commented out because it was not working properly for me (it would only show up if I called plt.show() after calling render_ax2(), but that would also cause both plots to be displayed at once).  The node names are extracted
    
    :param fig: Pass in the figure object that we created earlier
    :param ax2: Specify the axis that we want to draw on
    """
    adj_matrix = nx.adjacency_matrix(R)
    adj_array = adj_matrix.toarray()

    im = ax2.imshow(adj_array, cmap='coolwarm_r', interpolation='nearest', vmin=-1, vmax=1)
    ax2.set_title("Presented as Adjacency Matrix")
    # fig.colorbar(im, ax=ax2)

    node_names = list(R.nodes())
    ax2.set_xticks(range(len(node_names)))
    ax2.set_yticks(range(len(node_names)))
    ax2.set_xticklabels(node_names, rotation=45)
    ax2.set_yticklabels(node_names)

    for i in range(adj_array.shape[0]):
        for j in range(adj_array.shape[1]):
            ax2.text(j, i, f"{adj_array[i,j]:.2f}", ha="center", va="center", color="black")


def render_graph():
    """
    The render_graph function renders the graph in two parts:
        1. The left side of the graph, which is a bar chart showing how many times each word appears in the text.
        2. The right side of the graph, which is a scatter plot showing where each word appears in relation to other words.
    """
    fig, (ax1, ax2) = plt.subplots(ncols=2, figsize=(17, 7), gridspec_kw={'width_ratios': [1.5, 1]})

    render_ax1(fig, ax1)

    render_ax2(fig, ax2)

    plt.show()


prev = None  # Suggestion: do more "prev"s and have the effect of each one drop off exponentially
def step(node):
    """
    The step function takes a node as input and updates the probabilities of all nodes in the graph.
    It does this by iterating over all edges connected to that node, and adding a weighted amount of probability to each destination.
    The weight is determined by the edge's weight attribute and the node's current probability.
    Therefore, it simulates a "flow" of probability.
    
    :param node: Specify which node to step on
    """
    edges = R.edges(node, data=True)
    edges = [(dst, data['weight']) for src, dst, data in edges]
    try:
        p = probabilities[node]
    except KeyError:
        # Analyses will land here and be ignored
        return
    for scan, weight in edges:
        probabilities[scan] += weight * p
    global prev
    if prev is not None:
        if R.has_edge(prev, node):
            R[prev][node]['weight'] += dp * random.uniform(0.8, 1.2)
            if R[prev][node]['weight'] > maxp:
                R[prev][node]['weight'] *= reduction_factor
        else:
            R.add_edge(prev, node, weight=random.uniform(dp/2, dp))
    prev = node
    normalise()


def random_picker():
    normalise()
    return random.choices(list(probabilities.keys()), weights=probabilities.values())[0]


def main():
    """
    The main function is the entry point for this script.
    It constructs a graph, normalises it and then renders it.
    """
    construct_graph()
    normalise()
    for _ in range(250):
        render_graph()
        # step("ICMP Sweep")
        picked = random_picker()
        print(picked)
        step(picked)


if __name__ == '__main__':
    main()
