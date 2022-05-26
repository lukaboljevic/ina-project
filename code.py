import cpnet
import matplotlib.pyplot as plt
from utils import read_net, read_csv, degree_distribution, degree_sequences, continuous

def plot(graphname, directed, algorithm, plot_decomp=False):
    """
    Plot degree distributions of network, core and periphery that are obtained from 
    the core periphery decomposition algorithm.

    Parameters:
    graphname: name of the graph (i.e. name of the .net or .csv file which stores the graph)
    directed: whether the graph is directed
    algorithm: which core decomposition algorithm we are using
        (Either a cpnet algorithm, or rich core decomposition from rc.py)
    plot_decomp: whether to plot the CP decomposition of the graph
    """
    try:
        # csv's are more common so try that first
        G = read_csv(graphname, directed)
    except FileNotFoundError:
        G = read_net(graphname, directed)

    print("Graph read!")
    
    n = G.number_of_nodes()
    if isinstance(algorithm, cpnet.CPAlgorithm):
        algorithm_name = algorithm.__class__.__name__
        algorithm.detect(G)
        c = algorithm.get_pair_id()
        x = algorithm.get_coreness()
    else:
        algorithm_name = "Rich-core"
        c = None # TODO: for now
        x = algorithm(G)
    print("Core periphery decomposition completed")

    # Set core_threshold to 70, 80, 85 or whatever% of max coreness value returned by algo,
    # since sometimes the max coreness value is like 0.61 or something, so it's a bad idea
    # to set it to a static value
    if continuous(algorithm_name):
        max_coreness_value = max(x.values())
        print(max_coreness_value)
        core_threshold = round(0.80 * max_coreness_value, 4)
        print(core_threshold)
    else:
        core_threshold = 1 # unimportant, can be set to whatever

    if plot_decomp:
        plt.figure(figsize=(10, 7))
        plt.title(f"Core periphery decomposition, {algorithm_name} algorithm, {G.name} graph")
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
    periphery_degs, core_degs = degree_sequences(G, algorithm_name, x, core_threshold=core_threshold)

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
    title = f"Degree distributions for \"{G.name}\" graph, {algorithm_name} algorithm"
    if continuous(algorithm_name):
        title += f" (threshold {core_threshold})"
    plt.title(title)
    plt.legend()
    plt.show()

if __name__ == "__main__":
    graphs = [
        # Undirected
        # ("dblp", False),
        # ("movielens", False),
        # ("social", False),
        # ("wordnet", False),
        # ("nematode_mammal", False),
        ("friendships", False)

        # Directed
        # ("anybeat", True),
        # ("cora", True),
        # ("enron", True),
        # ("linux", True),
        # ("nec", True),
        # ("stanford", True),
        # ("genetic_multiplex", True),
        # ("fly_hemibrain", True)
        # ("caida", True)
        # ("genetic_multiplex", False),
    ]

    # TODO: only choosing the algos and testing remains; 
    # make sure to mention rich core is bad because of this and that

    for graph_info in graphs:
        plot(*graph_info, algorithm=cpnet.KM_ER())