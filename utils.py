import networkx as nx
from collections import defaultdict

def read_graph(graphname, directed=False):
    """
    Read a data/graphname.net file.
    Parameter directed indicates whether the graph is directed.
    By default it is False, meaning the function returns a Graph object.
    In the case it's True, the function returns a DiGraph object.
    """
    if directed:
        graph = nx.DiGraph(name=graphname)
    else:
        graph = nx.Graph(name=graphname)
    with open(f"data/{graphname}.net", 'r', encoding='utf8') as f:
        f.readline()
        
        for line in f:
            if line.startswith("*"):
                break
            else:
                node_info = line.split("\"")
                node = int(node_info[0]) - 1
                label = node_info[1]
                cluster = int(node_info[2]) if len(node_info) > 2 and len(node_info[2].strip()) > 0 else None
                graph.add_node(node, label=label, cluster=cluster)

        # add edges
        for line in f:
            node1_str, node2_str = line.split()[:2]
            graph.add_edge(int(node1_str) - 1, int(node2_str) - 1)

    return graph

def degree_distribution(sequence, n):
    """
    Return the degree distribution for this degree sequence
    """
    distribution = defaultdict(int)
    for degree in sequence:
        distribution[degree] += 1
    for degree in distribution:
        distribution[degree] /= n
    return distribution
