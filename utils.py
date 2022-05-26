import networkx as nx
import pandas as pd
from collections import defaultdict

DISCRETE = 0
CONTINUOUS = 1

algorithm_type = {
    # Slow 
    "BE": DISCRETE,
    "Lip": DISCRETE,
    "LapCore": DISCRETE,
    "LapSgnCore": DISCRETE,
    "Surprise": DISCRETE,
    "LowRankCore": DISCRETE,
    # Rather fast
    "KM_ER": DISCRETE,
    "KM_config": DISCRETE,
    "Divisive": DISCRETE,
    "Rombach": CONTINUOUS,
    "Rossa": CONTINUOUS,
    # Fast
    "MINRES": CONTINUOUS,
    # Super fast
    "Rich-core": DISCRETE,
}

def continuous(algorithm_name):
    return algorithm_type[algorithm_name] == CONTINUOUS

def degree_sequences(graph: nx.Graph, algorithm_name, coreness_map, core_threshold=0.7):
    """
    For a given graph (and algorithm), return the core 
    and periphery degree sequences.

    Parameters
    ----------
    graph: nx.Graph object
    algorithm_name: one of cpnet core periphery decomposition algorithms, or rich core decomp algorithm
    coreness_map: a dictionary returned by the same algorithm, which tells us 
        the coreness value of each node (0 or 1 if discrete algorithm,
        value between 0 and 1 for a continuous algorithm)
    core_threshold: meaningful only when we're talking about a continuous
        algorithm - any node whose coreness value is above this threshold
        is considered as part of the core, otherwise it's considered as 
        part of the periphery
    """
    if not continuous(algorithm_name):
        periphery_degs = [graph.degree[node] for node in graph.nodes() if coreness_map[node] == 0]
        core_degs = [graph.degree[node] for node in graph.nodes() if coreness_map[node] == 1]
    else:
        periphery_degs = [graph.degree[node] for node in graph.nodes() if coreness_map[node] < core_threshold]
        core_degs = [graph.degree[node] for node in graph.nodes() if coreness_map[node] >= core_threshold]
    
    return periphery_degs, core_degs

def read_net(graphname, directed=False):
    """
    Read a graph from the given file. 

    Parameter "graphname" is given without .net extension.

    Parameter "directed" indicates whether the graph is directed.
    By default it is False, meaning the function returns a Graph object.
    In the case it's True, the function returns a DiGraph object.
    """
    if directed:
        graph = nx.DiGraph(name=graphname)
    else:
        graph = nx.Graph(name=graphname)

    folder = "directed" if directed else "undirected"
    path = f"data/{folder}/{graphname}.net"
    with open(path, 'r', encoding='utf8') as f:
        f.readline()
        
        for line in f:
            if line.startswith("*"):
                break
            else:
                node_info = line.split("\"")
                node = int(node_info[0]) - 1
                graph.add_node(node)

        # add edges
        for line in f:
            node1_str, node2_str = line.split()[:2]
            graph.add_edge(int(node1_str) - 1, int(node2_str) - 1)

    return graph

def read_csv(graphname, directed=False):
    """
    Read a graph from pairs of .csv files. 

    Parameter "graphname" is given without any extensions or additional stuff.

    Parameter "directed" indicates whether the graph is directed.
    By default it is False, meaning the function returns a Graph object.
    In the case it's True, the function returns a DiGraph object.
    """
    if directed:
        graph = nx.DiGraph(name=graphname)
    else:
        graph = nx.Graph(name=graphname)

    folder = "directed" if directed else "undirected"
    path = f"data/{folder}/{graphname}"
    
    nodes = pd.read_csv(path + "_nodes.csv")
    graph.add_nodes_from(range(len(nodes)))

    edges = pd.read_csv(path + "_edges.csv")
    # Adding edges like this is WAY faster than iterating and adding,
    # especially for larger graphs with hundreds of thousands of edges.
    # For example, for a graph with 2312497 edges, it took less than 
    # 6 seconds to add all of them.
    graph.add_edges_from(zip(edges["# source"], edges[" target"]))

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
