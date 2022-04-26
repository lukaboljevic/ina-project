import networkx as nx
from collections import defaultdict
import cpnet

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
    # Fast
    "MINRES": CONTINUOUS,
    "Rombach": CONTINUOUS,
    "Rossa": CONTINUOUS,
}

def continuous(algorithm):
    algo_name = algorithm.__class__.__name__
    return algorithm_type[algo_name] == CONTINUOUS

def degree_sequences(graph: nx.Graph, algorithm: cpnet.CPAlgorithm, coreness_map, core_threshold=0.7):
    """
    For a given graph (and algorithm), return the core 
    and periphery degree sequences.

    Parameters
    ----------
    graph: nx.Graph object
    algorithm: one of cpnet core periphery decomposition algorithms
    coreness_map: a dictionary returned by the same algorithm, which tells us 
        the coreness value of each node (0 or 1 if discrete algorithm,
        value between 0 and 1 for a continuous algorithm)
    core_threshold: meaningful only when we're talking about a continuous
        algorithm - any node whose coreness value is above this threshold
        is considered as part of the core, otherwise it's considered as 
        part of the periphery
    """
    algo_name = algorithm.__class__.__name__
    if algorithm_type[algo_name] == DISCRETE:
        periphery_degs = [graph.degree[node] for node in graph.nodes() if coreness_map[node] == 0]
        core_degs = [graph.degree[node] for node in graph.nodes() if coreness_map[node] == 1]
    else:
        periphery_degs = [graph.degree[node] for node in graph.nodes() if coreness_map[node] < core_threshold]
        core_degs = [graph.degree[node] for node in graph.nodes() if coreness_map[node] >= core_threshold]
    
    return periphery_degs, core_degs

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
