import os
import cpnet
import networkx as nx
import matplotlib.pyplot as plt
from utils import read_net, read_csv, degree_distribution, degree_sequences, continuous

def plot(graphname, directed, algorithm: cpnet.CPAlgorithm, core_threshold=0.7, plot_decomp=False):
    try:
        # csv's are more common so try that first
        G = read_csv(graphname, directed)
    except FileNotFoundError:
        G = read_net(graphname, directed)

    print("Graph read!")
    
    n = G.number_of_nodes()
    name = algorithm.__class__.__name__

    algorithm.detect(G)
    c = algorithm.get_pair_id()
    x = algorithm.get_coreness()
    # print("Core periphery decomposition completed")

    # TODO: set core_threshold to like idk, 70 or 80 or whatever% of max coreness value returned by algo

    if plot_decomp:
        plt.figure(figsize=(10, 7))
        plt.title(f"Core periphery decomposition, {name} algorithm, {G.name} graph")
        ax = plt.gca()
        ax, pos = cpnet.draw(G, c, x, ax, draw_edge=False)
        """
        pos is a dict {node_id: (x, y)} where node_id is a node id
        given by G.nodes(), and (x, y) is the (x, y) coordinate
        of that node on the plot. Useful when testing out different
        core periphery decomposition algorithms on the same graph.
        """
        plt.show()

    graph_degs = [G.degree[node] for node in G.nodes()]
    periphery_degs, core_degs = degree_sequences(G, algorithm, x, core_threshold=core_threshold)

    graph_dist = degree_distribution(graph_degs, n)
    periphery_dist = degree_distribution(periphery_degs, len(periphery_degs))
    core_dist = degree_distribution(core_degs, len(core_degs))

    plt.style.use("ggplot")
    plt.figure(figsize=(12, 7))
    plt.plot(graph_dist.keys(), graph_dist.values(), 'o', color="firebrick", label=f"Graph dist.")
    plt.plot(periphery_dist.keys(), periphery_dist.values(), 'x', color="forestgreen", label=f"Periphery dist.")
    plt.plot(core_dist.keys(), core_dist.values(), '*', color="goldenrod", label=f"Core dist.")
    plt.xlabel("Degrees")
    plt.ylabel("Degree distributions")
    plt.xscale("log")
    plt.yscale("log")
    title = f"Degree distributions for \"{G.name}\" graph, {name} algorithm"
    if continuous(algorithm):
        title += f" (threshold {core_threshold})"
    plt.title(title)
    plt.legend()
    plt.show()

if __name__ == "__main__":
    graphs = [
        # Undirected
        # ("dblp", False),
        ("movielens", False),
        ("social", False),
        # ("wordnet", False),

        # Directed
        # ("anybeat", True),
        ("cora", True),
        # ("enron", True),
        ("linux", True),
        # ("nec", True),
        # ("stanford", True),
    ]

    for graph_info in graphs:
        plot(*graph_info, algorithm=cpnet.Rossa(), core_threshold=0.6)