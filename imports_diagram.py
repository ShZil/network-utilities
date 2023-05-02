import os
import re
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.cm import ScalarMappable
from matplotlib.colors import Normalize
import numpy as np

def list_py_files(directory):
    py_files = []
    for root, dirs, files in os.walk(directory):
        for f in files:
            if f.endswith('.py'):
                py_files.append(os.path.join(root, f))
    return py_files


def find_import_statements(file_path):
    import_regex = re.compile(r'^\s*from .* import .*|^\s*import .*')  # manual regex using regexr.com
    matching_lines = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if import_regex.match(line):
                line = line.strip()
                if 'from ' in line:
                    line = line.split('from ', 1)[1]
                    line = line.split(' import ', 1)[0]
                if ' as ' in line:
                    line = line.split(' as ', 1)[0]
                if line.startswith('import '):
                    line = line.split('import ', 1)[1]
                matching_lines.append(line.strip())
    return list(set(matching_lines))


def name(f):
    return f[len(directory)+1:-len(".py")].replace('\\', '.')


def render(G, pos):
    node_numbers = {node: sum(1 for _ in G.predecessors(node)) for node in G.nodes()}
    print(node_numbers)
    norm = Normalize(vmin=min(node_numbers.values()), vmax=max(node_numbers.values()))
    cmap = plt.get_cmap('YlOrRd')
    node_colors = [cmap(norm(node_numbers[node])) for node in G.nodes()]
    nx.draw_networkx(G, pos, with_labels=True, node_color=node_colors)
    sm = ScalarMappable(norm=norm, cmap=cmap)
    sm.set_array([])
    cbar = plt.colorbar(sm)
    cbar.set_label('Number of Modules In Which I\'m used')
    plt.show()


def update_position(pos, changes):
    for node, position in pos.items():
        if node.startswith('gui.'):
            x, y = position[0], position[1]
            pos[node] = np.array([(1+x)*4, (1+y)*4])
    for name, value in changes.items():
        pos[name] = np.array(value)
    return pos


def distribute_weights(G):
    # create a dictionary to store the weight for each node
    node_weights = {node: 1 for node in G.nodes()}
    
    # loop through each node in the graph
    for node in G.nodes():
        # get the list of incoming edges for this node
        incoming_edges = list(G.in_edges(node))
        num_incoming_edges = len(incoming_edges)
        
        # if this node has no incoming edges, continue to the next node
        if num_incoming_edges == 0:
            continue
        
        # calculate the weight to assign to each incoming edge
        weight_per_edge = node_weights[node] / num_incoming_edges
        
        # loop through each incoming edge and assign the weight
        for edge in incoming_edges:
            G[edge[0]][edge[1]]['weight'] = weight_per_edge
            
    return G


directory = "./Scanner"
files = list_py_files(directory)
file_names = list(map(name, files))
G = nx.DiGraph()
for f in files:
    G.add_node(name(f))
    print(name(f))
    # print(find_import_statements(f))
    G.add_edges_from([(name(f), v) for v in find_import_statements(f) if v in file_names])

print(G)
G = distribute_weights(G)

pos = nx.kamada_kawai_layout(G)  # dict {name: array[float, float] between (-1) to (1)}
# index = -1
# def position(node):
#     global index
#     index += 1
#     return [(index % 10) * .1, (index // 10) * .1]
# pos = {node: np.array(position(node)) for node in G}
changes = {
    'scans.__init__': [-.9, .8],
    'gui.__init__': [-.9, .6],
    'gui.Screens.__init__': [-.9, .4],
    'RecommendProbabilitiesPrimitive': [-.9, .2],
    'exe': [-.6, 0]
}
pos = update_position(pos, changes)
G.remove_nodes_from(['import_handler', 'globalstuff', 'CacheDecorators'])
render(G, pos)
