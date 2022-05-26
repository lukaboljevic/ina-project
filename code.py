import glob
import cpnet
import matplotlib.pyplot as plt
from utils import read_net, read_csv, degree_distribution, degree_sequences, continuous

def plot(graphname, directed, algorithm, plot_decomp=False):
    """
    Plot degree distributions of network, core and periphery that are obtained from 
    the core periphery (CP) decomposition algorithm.

    Parameters:
    graphname: name of the graph (i.e. name of the .net or .csv file which stores the graph)
    directed: whether the graph is directed
    algorithm: which CP algorithm we are using
        (Either a cpnet algorithm, or rich core decomposition from rc.py)
    plot_decomp: whether to plot the CP decomposition of the graph
    """

    """
    NOTE: Continuous CP algorithms are not entirely deterministic,
    i.e. for the same graph, same algorithm and same (rounded) core 
    threshold value, the plots may not be EXACTLY the same. However, 
    the plots are similar enough so that we can still extract a 
    "general" result from them.
    """

    # If a figure for this graph and this algorithm already exists, don't repeat
    orientation = "directed" if directed else "undirected"
    if isinstance(algorithm, cpnet.CPAlgorithm):
        algorithm_name = algorithm.__class__.__name__
    else:
        algorithm_name = "Rich-core"
    
    fig_path = f"results/{orientation}/{graphname}-{algorithm_name}"
    if glob.glob(fig_path + "*.png"):
        print("\tPlot already exists!")
        return

    # Read the graph
    try:
        # csv's are more common so try that first
        G = read_csv(graphname, directed)
    except FileNotFoundError:
        G = read_net(graphname, directed)

    print(f"\tGraph read!")
    
    # Do the CP decomposition
    n = G.number_of_nodes()
    if isinstance(algorithm, cpnet.CPAlgorithm):
        algorithm.detect(G)
        c = algorithm.get_pair_id()
        x = algorithm.get_coreness()
    else:
        c = None # TODO: for now
        x = algorithm(G)
    print("\tCP decomposition completed!")

    # Set core_threshold to 70, 80, 85 or whatever% of max coreness value returned by algo,
    # since sometimes the max coreness value is like 0.61 or something, so it's a bad idea
    # to set it to a static value
    percentage = 75
    if continuous(algorithm_name):
        max_coreness_value = max(x.values())
        print(f"\tMaximum coreness: {max_coreness_value}")
        core_threshold = round(percentage / 100 * max_coreness_value, 3)
        print(f"\tThreshold ({percentage}% of maximum): {core_threshold}")
    else:
        core_threshold = 1 # unimportant, can be set to whatever

    # Plot the actual CP decomposition (slow, don't use for big graphs)
    if plot_decomp:
        plt.figure(figsize=(10, 7))
        plt.title(f"CP decomposition for {graphname} graph ({orientation}), {algorithm_name} algorithm")
        ax = plt.gca()
        ax, pos = cpnet.draw(G, c, x, ax, draw_edge=False)
        """
        pos is a dict {node_id: (x, y)} where node_id is a node id
        given by G.nodes(), and (x, y) is the (x, y) coordinate
        of that node on the plot. Useful when testing out different
        CP decomposition algorithms on the same graph.
        """
        plt.show()

    # Get degrees of the nodes in the graph, core and periphery separately
    graph_degs = [G.degree[node] for node in G.nodes()]
    periphery_degs, core_degs = degree_sequences(G, algorithm_name, x, core_threshold=core_threshold)

    # Calculate the degree distribution of the graph, core and periphery
    graph_dist = degree_distribution(graph_degs, n)
    periphery_dist = degree_distribution(periphery_degs, len(periphery_degs))
    core_dist = degree_distribution(core_degs, len(core_degs))

    # Plot the distributions and save the figure
    plt.style.use("ggplot")
    plt.figure(figsize=(12, 7))
    plt.plot(graph_dist.keys(), graph_dist.values(), 'o', color="firebrick", label=f"Graph deg. dist.")
    plt.plot(periphery_dist.keys(), periphery_dist.values(), 'x', color="forestgreen", label=f"Periphery deg. dist.")
    plt.plot(core_dist.keys(), core_dist.values(), '*', color="goldenrod", label=f"Core deg. dist.")
    plt.xlabel("Degrees (log)")
    plt.ylabel("Degree distributions (log)")
    plt.xscale("log")
    plt.yscale("log")
    title = f"Deg. dist. for \"{graphname}\" graph ({orientation}), {algorithm_name} algorithm"
    if continuous(algorithm_name):
        title += f" (threshold {core_threshold}, {percentage}% of max)"
        fig_path += f"-{core_threshold}-{percentage}"
    fig_path += ".png"
    plt.title(title)
    plt.legend() 
    plt.savefig(fig_path)
    print("\tPlot saved!")
    # plt.show()

if __name__ == "__main__":
    # For now, choose smaller graphs
    small_graphs = [
        # Undirected
        ("social", False), # social
        ("movielens", False), # informational
        ("nematode_mammal", False), # biological
        ("internet_as", False), # technological

        # Directed
        ("anybeat", True), # social
        ("cora", True), # informational
        ("genetic_multiplex", True), # biological
        ("caida", True), # technological
    ]

    # TODO: make sure to mention rich core is bad because of this and that
    
    # Chosen algorithms (cause they are fast B); at least one from every family)
    fast_algorithms = [
        # Continuous
        cpnet.MINRES(),
        cpnet.Rossa(),

        # Multiple pairs of CP (which will be converted to single)
        cpnet.KM_ER(),

        # Single pair of CP
        cpnet.Lip(),
        cpnet.LapSgnCore(),
    ]

    for algorithm in fast_algorithms:
        for graph_info in small_graphs:
            print(f"Graph: {graph_info[0]}, algorithm: {algorithm.__class__.__name__}")
            plot(*graph_info, algorithm)
        print("\n=========================================================\n")