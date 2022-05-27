import networkx as nx
import pandas as pd
from collections import defaultdict

DISCRETE = 0
CONTINUOUS = 1

algorithm_type = {
    # NOTE: "smaller network" means smaller out of these that are present
    # in this project - so networks w/ around 20-50k nodes

    # True discrete - single CP
    "BE": DISCRETE, # extra slow
    "Lip": DISCRETE, # super fast, useless
    "LapCore": DISCRETE, # quite fast (for smaller, not so much for larger)
    "LowRankCore": DISCRETE, # speed similar to LapCore for smaller, memory error for larger
    "LapSgnCore": DISCRETE, # super fast
    "Surprise": DISCRETE, # extra slow; there is a faster implementation for this algo, check cpnet repo
    "Rich_core": DISCRETE, # super fast

    # "Discrete" - multiple pairs of CP
    "KM_ER": DISCRETE, # quite fast
    "KM_config": DISCRETE, # quite fast, slower than KM_ER for larger
    "Divisive": DISCRETE, # depends on the network (?), even w/ smaller
    
    # Continuous
    "Rombach": CONTINUOUS, # relatively slow for smaller networks even
    "Rossa": CONTINUOUS, # quite fast (for smaller networks)
    "MINRES": CONTINUOUS, # quite fast!
}

def continuous(algorithm_name):
    return algorithm_type[algorithm_name] == CONTINUOUS

def degree_sequences(graph: nx.Graph, algorithm_name, coreness_map, core_threshold=0.7):
    """
    For a given network (and algorithm), return the core 
    and periphery degree sequences.

    Parameters
    ----------
    graph: nx.Graph object
    algorithm_name: one of cpnet CP decomposition algorithms, or rich core decomp algorithm
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

def read_net(network_name, directed=False):
    """
    Read a network from the given file. 

    Parameter "network_name" is given without .net extension.

    Parameter "directed" indicates whether the network is directed.
    By default it is False, meaning the function returns a Graph object.
    In the case it's True, the function returns a DiGraph object.
    """
    if directed:
        graph = nx.DiGraph(name=network_name)
    else:
        graph = nx.Graph(name=network_name)

    folder = "directed" if directed else "undirected"
    path = f"data/{folder}/{network_name}.net"
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

def read_csv(network_name, directed=False):
    """
    Read a network from pairs of .csv files. 

    Parameter "network_name" is given without any extensions or additional stuff.

    Parameter "directed" indicates whether the network is directed.
    By default it is False, meaning the function returns a Graph object.
    In the case it's True, the function returns a DiGraph object.
    """
    if directed:
        graph = nx.DiGraph(name=network_name)
    else:
        graph = nx.Graph(name=network_name)

    folder = "directed" if directed else "undirected"
    path = f"data/{folder}/{network_name}"
    
    nodes = pd.read_csv(path + "_nodes.csv")
    graph.add_nodes_from(range(len(nodes)))

    edges = pd.read_csv(path + "_edges.csv")
    # Adding edges like this is WAY faster than iterating and adding,
    # especially for larger networks with hundreds of thousands of edges.
    # For example, for a network with 2312497 edges, it took less than 
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
