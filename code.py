import cpnet
import networkx as nx
import matplotlib.pyplot as plt
from utils import read_graph, degree_distribution

def example():
    # Example code taken from 
    # https://github.com/skojaku/core-periphery-detection/blob/master/notebooks/example1.ipynb

    G = nx.karate_club_graph()
    n = G.number_of_nodes()
    algorithm = cpnet.Surprise(20)
    name = algorithm.__class__.__name__
    algorithm.detect(G)
    c = algorithm.get_pair_id()
    x = algorithm.get_coreness() # core = 1, periphery = 0

    plt.figure(figsize=(10, 7))
    plt.title(f"Core periphery decomposition, {name} algorithm, {G.name} graph")
    ax = plt.gca()
    ax, pos = cpnet.draw(G, c, x, ax) 
    """
    pos is a dict {node_id: (x, y)} where node_id is a node id
    given by G.nodes(), and (x, y) is the (x, y) coordinate
    of that node on the plot. Useful when testing out different
    core periphery decomposition algorithms on the same graph.
    """
    plt.show()

def plot(graphname, directed):
    G = read_graph(graphname, directed)
    n = G.number_of_nodes()
    algorithm = cpnet.Surprise()
    name = algorithm.__class__.__name__
    algorithm.detect(G)
    c = algorithm.get_pair_id()
    x = algorithm.get_coreness() # core = 1, periphery = 0
    print("Core periphery decomposition completed")
    plt.figure(figsize=(10, 7))
    plt.title(f"Core periphery decomposition, {name} algorithm, {G.name} graph")
    ax = plt.gca()
    ax, pos = cpnet.draw(G, c, x, ax)
    plt.show()

    graph_degs = [G.degree[node] for node in G.nodes()]
    periphery_degs = [G.degree[node] for node in G.nodes() if x[node] == 0]
    core_degs = [G.degree[node] for node in G.nodes() if x[node] == 1]

    graph_dist = degree_distribution(graph_degs, n)
    periphery_dist = degree_distribution(periphery_degs, len(periphery_degs))
    core_dist = degree_distribution(core_degs, len(core_degs))

    plt.figure(figsize=(12, 7))
    plt.plot(graph_dist.keys(), graph_dist.values(), 'o', color="firebrick", label=f"Graph dist.")
    plt.plot(periphery_dist.keys(), periphery_dist.values(), 'x', color="forestgreen", label=f"Periphery dist.")
    plt.plot(core_dist.keys(), core_dist.values(), '*', color="goldenrod", label=f"Core dist.")
    plt.xlabel("Degrees")
    plt.ylabel("Degree distributions")
    plt.xscale("log")
    plt.yscale("log")
    plt.title(f"Distributions for {name} algorithm, {G.name} graph")
    plt.legend()
    plt.show()

# example()
plot("java", False)