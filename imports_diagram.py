import os
import re
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.cm import ScalarMappable
from matplotlib.colors import Normalize
import matplotlib.patches as patches
import numpy as np
from random import random

def list_py_files(directory):
    py_files = []
    for root, dirs, files in os.walk(directory):
        for f in files:
            if f.endswith('.py'):
                py_files.append(os.path.join(root, f))
    return py_files


def find_import_statements(file_path, allow_dynamic_imports=True):
    import_regex = re.compile(r'^\s*from .* import .*|^\s*import .*')  # manual regex using regexr.com
    matching_lines = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if not allow_dynamic_imports and 'def ' in line: break
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
    fig, ax = plt.subplots()
    node_numbers = {node: sum(1 for _ in G.predecessors(node)) for node in G.nodes()}
    # print(node_numbers)
    norm = Normalize(vmin=min(node_numbers.values()), vmax=max(node_numbers.values()))
    cmap = plt.get_cmap('YlOrRd')
    node_colors = [cmap(norm(node_numbers[node])) for node in G.nodes()]
    nx.draw_networkx(G, pos, with_labels=True, node_color=node_colors, ax=ax)
    sm = ScalarMappable(norm=norm, cmap=cmap)
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax)
    cbar.set_label('Number of Modules In Which I\'m used')

    rect = patches.Rectangle((POSX-.05, POSY-.05), POSW+.1, POSH+.1, linewidth=1, edgecolor='black', facecolor='none')
    # Add the rectangle to the plot
    ax.add_patch(rect)
    plt.show()


POSX, POSY, POSW, POSH = .5, 1, 1, .5
def update_position(pos, changes):
    for node, position in pos.items():
        x, y = position[0], position[1]
        if node.startswith('gui.'):
            pos[node] = np.array([POSX + random()*POSW, POSY + random()*POSH])
        if node.startswith('scans.'):
            pos[node] = np.array([-.3+random()*.5, 1.2 + random()*.2])
    for name, value in changes.items():
        pos[name] = np.array(value)
    return pos


def distribute_weights(G):
    # loop through each node in the graph
    for node in G.nodes():
        # get the list of incoming edges for this node
        incoming_edges = list(G.in_edges(node))
        num_incoming_edges = len(incoming_edges)
        
        # if this node has no incoming edges, continue to the next node
        if num_incoming_edges == 0:
            continue
        
        # calculate the weight to assign to each incoming edge
        weight_per_edge = 2 / num_incoming_edges
        
        # loop through each incoming edge and assign the weight
        for edge in incoming_edges:
            G[edge[0]][edge[1]]['weight'] = weight_per_edge
    return G


directory = "./Scanner"
files = list_py_files(directory)
file_names = list(map(name, files))
G = nx.DiGraph()
i = 2
for f in files:
    i += 1
    G.add_node(name(f))
    # print(name(f))
    # print(f'<mxCell id="4mCQ5pcPBgcy5jRonQE--{i}" value="{name(f)}" style="ellipse;whiteSpace=wrap;html=1;fontFamily=Consolas;fontSize=16;" vertex="1" parent="1"><mxGeometry x="240" y="240" width="80" height="80" as="geometry" /></mxCell>')
    # print(find_import_statements(f))
    imported = [v for v in find_import_statements(f, allow_dynamic_imports=True) if v in file_names]
    if 'db' in imported:
        print(name(f))
    G.add_edges_from([(name(f), v) for v in imported])

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
    'exe': [-.6, 0],
    'register': [-.5, .8],
    'colors': [.9, 0],
    'CommandLineStyle': [.9, -.2],
    'PrintingContexts': [.9, -.4],
    'testing.tests': [.35, -.4],
    'ip_handler': [.3, -.2],
    'db': [1.5, .3],
    'NetworkStorage': [1.5, .5],
    'ipconfig': [.75, .5],
    'SimpleScan': [.05, .25]
}
pos = update_position(pos, changes)
G.remove_nodes_from(['import_handler', 'globalstuff', 'CacheDecorators'])
render(G, pos)
