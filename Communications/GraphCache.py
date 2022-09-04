from NetEntity import NetEntity
import networkx as nx

__author__ = 'Shaked Dan Zilberman'


class GraphCache:
    def __init__(self) -> None:
        self.path = 'graph.txt'
    
    def save_graph(self, G, printing=True):
        create_file(self.path)
        with open(self.path, 'w', encoding="utf-8") as file:
            file.write("Nodes:\n")
            l = list(G.nodes)
            for node in l:
                file.write("    " + node.destruct() + "\n")
            file.write("Edges:\n")
            for u, v, info in list(G.edges(data=True)):
                file.write(f"    {l.index(u)} > {l.index(v)} M {info['weight']}\n")
        if printing:
            print("\nSaved graph to ", self.path)


    def read_graph(self, printing=True):
        lines = readall(self.path)
        nodes = []
        edges = []
        current = None
        counter = 0

        for line in lines:
            if "Nodes" in line:
                current = nodes
                continue
            elif "Edges" in line:
                current = edges
                continue
            else:
                current.append(line.strip())
        
        real_nodes = []
        for node in nodes:
            real_nodes.append(NetEntity.restruct(node))
    
        edges_tuples = []
        for edge in edges:
            try:
                left, right = tuple(edge.split('>'))
                left = int(left)
            except ValueError:
                print("Invalid edge:", edge)
                continue
            try:
                right, weight = tuple(right.split("M"))
                right = int(right)
                weight = int(weight.strip())
            except ValueError:
                weight = 1
            edges_tuples.append((real_nodes[left], real_nodes[right], weight))
            if weight > counter: counter = weight
            counter += 1
        
        G = nx.DiGraph()
        G.add_nodes_from(real_nodes)
        G.add_weighted_edges_from(edges_tuples)
        if printing:
            print("\nRead graph from ", self.path)
        return G, counter


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
