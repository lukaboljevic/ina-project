import glob
import cpnet
import matplotlib.pyplot as plt
from utils import read_net, read_csv, degree_distribution, degree_sequences, continuous
from rc import rich_core_decomp_undir, rich_core_decomp_dir

def plot_network(network_name, directed):
    """
    Separate, helper function, used for just plotting the 
    network's degree distribution. No CP decomposition is done here.
    Used for testing (to see if a network has a power-law degree dist.)
    """

    # Read the network
    try:
        # csv's are more common so try that first
        G = read_csv(network_name, directed)
    except FileNotFoundError:
        G = read_net(network_name, directed)

    print(f"\tNetwork read!")

    n = G.number_of_nodes()
    graph_degs = [G.degree[node] for node in G.nodes()]
    graph_dist = degree_distribution(graph_degs, n)

    plt.style.use("ggplot")
    plt.figure(figsize=(12, 7))
    plt.plot(graph_dist.keys(), graph_dist.values(), 'o', color="firebrick", label=f"Network deg. dist.")
    plt.xlabel("Degrees (log)")
    plt.ylabel("Degree distributions (log)")
    plt.xscale("log")
    plt.yscale("log")
    orientation = "directed" if directed else "undirected"
    title = f"Deg. dist. for \"{network_name}\" network ({orientation})"
    plt.title(title)
    plt.legend()
    plt.show()

def plot_all(network_name, directed, algorithm, plot_decomp=False):
    """
    Plot degree distributions of network, core and periphery that are obtained from 
    the core periphery (CP) decomposition algorithm.

    Parameters:
    network_name: name of the network (i.e. name of the .net or .csv file which stores it)
    directed: whether the network is directed
    algorithm: which CP algorithm we are using
        (Either a cpnet algorithm, or rich core decomposition from rc.py)
    plot_decomp: whether to plot the CP decomposition of the network
    """

    """
    NOTE: Continuous CP algorithms are not entirely deterministic,
    i.e. for the same network, same algorithm and same (rounded) core 
    threshold value, the plots may not be EXACTLY the same. However, 
    the plots are similar enough so that we can still extract a 
    "general" result from them.
    """

    # If a figure for this network and this algorithm already exists, don't repeat
    orientation = "directed" if directed else "undirected"
    if isinstance(algorithm, cpnet.CPAlgorithm):
        algorithm_name = algorithm.__class__.__name__
    else:
        algorithm_name = "Rich_core"
    
    fig_path = f"results/{orientation}/{network_name}-{algorithm_name}"
    if glob.glob(fig_path + "*.png"):
        print("\tPlot already exists!")
        return

    # Read the network
    try:
        # csv's are more common so try that first
        G = read_csv(network_name, directed)
    except FileNotFoundError:
        G = read_net(network_name, directed)

    print(f"\tNetwork read!")
    
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

    # Plot the actual CP decomposition (slow, don't use for big networks)
    if plot_decomp:
        plt.figure(figsize=(10, 7))
        plt.title(f"CP decomposition for {network_name} network ({orientation}), {algorithm_name} algorithm")
        ax = plt.gca()
        ax, pos = cpnet.draw(G, c, x, ax, draw_edge=False)
        """
        pos is a dict {node_id: (x, y)} where node_id is a node id
        given by G.nodes(), and (x, y) is the (x, y) coordinate
        of that node on the plot. Useful when testing out different
        CP decomposition algorithms on the same network.
        """
        plt.show()

    # Get degrees of the nodes in the network, core and periphery separately
    graph_degs = [G.degree[node] for node in G.nodes()]
    periphery_degs, core_degs = degree_sequences(G, algorithm_name, x, core_threshold=core_threshold)

    # Calculate the degree distribution of the network, core and periphery
    graph_dist = degree_distribution(graph_degs, n)
    periphery_dist = degree_distribution(periphery_degs, len(periphery_degs))
    core_dist = degree_distribution(core_degs, len(core_degs))

    # Plot the distributions and save the figure
    plt.style.use("ggplot")
    plt.figure(figsize=(12, 7))
    plt.plot(graph_dist.keys(), graph_dist.values(), 'o', color="firebrick", label=f"Network deg. dist.")
    plt.plot(periphery_dist.keys(), periphery_dist.values(), 'x', color="forestgreen", label=f"Periphery deg. dist.")
    plt.plot(core_dist.keys(), core_dist.values(), '*', color="goldenrod", label=f"Core deg. dist.")
    plt.xlabel("Degrees (log)")
    plt.ylabel("Degree distributions (log)")
    plt.xscale("log")
    plt.yscale("log")
    title = f"Deg. dist. for \"{network_name}\" network ({orientation}), {algorithm_name} algorithm"
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
    # For now, choose smaller networks
    small_networks = [
        # Undirected
        ("social", False), # social
        ("movielens", False), # informational
        ("nematode_mammal", False), # biological
        ("internet_as", False), # technological

        # Directed
        ("anybeat", True), # social
        ("cora", True), # informational
        ("genetic_multiplex", True), # biological
        ("python_dependency", True), # technological, better than caida even if bigger
    ]

    # Chosen algorithms (cause they are fast B); at least one from every family)
    fast_algorithms = [
        # Continuous
        cpnet.MINRES(),
        cpnet.Rossa(),

        # Multiple pairs of CP (which will be converted to single)
        cpnet.KM_ER(),

        # Single pair of CP
        cpnet.LapSgnCore(),
        cpnet.LapCore(),
        cpnet.Lip(),
    ]

    for algorithm in fast_algorithms:
        for network_info in small_networks:
            print(f"Network: {network_info[0]}, algorithm: {algorithm.__class__.__name__}")
            plot_all(*network_info, algorithm)
        print("\n=========================================================\n")

    for network_info in small_networks[:4]:
        # First 4 are undirected networks
        print(f"Network: {network_info[0]}, algorithm: Rich_core")
        plot_all(*network_info, rich_core_decomp_undir)

    for network_info in small_networks[4:]:
        # Second 4 are directed networks
        print(f"Network: {network_info[0]}, algorithm: Rich_core")
        plot_all(*network_info, rich_core_decomp_dir)