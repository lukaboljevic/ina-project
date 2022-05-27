import networkx as nx
import numpy as np
from utils import read_net

"""
Rich-core CP algorithm from:
https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0119678
"""

def rich_core_decomp_undir(g : nx.Graph):
    """
    Rich-core CP algorithm for undirected networks
    """
    
    # Unique degrees of the network, sorted in descending order
    unique_deg = np.unique(np.array([g.degree[node] for node in g.nodes]))[::-1]
    # Save indices of descending sorted degrees
    ranking_map = {}
    for i in range(len(unique_deg)):
        ranking_map[unique_deg[i]] = i

    # Nodes are ranked according to degree in descending order, node of highest degree
    # has the highest rank. If two nodes have the same degree, their rank is the same
    node_rank = {}
    for node in g.nodes:
        node_rank[node] = ranking_map[g.degree[node]]
    
    # For a node r, k_{r}^{+} is the number of links from r to a node of higher rank
    kr_plus = {node : 0 for node in g.nodes}
    for edge in g.edges():
        u = edge[0]
        v = edge[1]

        if node_rank[u] < node_rank[v]:
            kr_plus[v] += 1

        elif node_rank[v] > node_rank[u]:
            kr_plus[u] += 1
    
    # r^{*} = max_{r} k_{r}^{+}
    r_star = max(kr_plus.items(), key = lambda x : x[1])
    # Undirected rich core is defined as {r : rank[r] > rank[r*]}
    core_indicator = {key : 1 if value < node_rank[r_star[0]] else 0 for key, value in node_rank.items()}
    return core_indicator

def rich_core_decomp_dir(g : nx.DiGraph):
    """
    Rich-core CP algorithm for undirected networks
    """
    
    # Unique in-degrees of the network, sorted in descending order
    unique_in_deg = np.unique(np.array([g.in_degree[node] for node in g.nodes]))[::-1]
    # Save indices of descending sorted degrees
    ranking_map = {}
    for i in range(len(unique_in_deg)):
        ranking_map[unique_in_deg[i]] = i

    # Nodes are ranked according to degree in descending order, node of highest degree
    # has the highest rank. If two nodes have the same degree, their rank is the same
    node_rank = {}
    for node in g.nodes:
        node_rank[node] = ranking_map[g.in_degree[node]]
    
    sigma_plus_r_in, sigma_plus_r_out = {node : 0 for node in g.nodes()}, {node : 0 for node in g.nodes()}

    for edge in g.edges():
        u = edge[0]
        v = edge[1]

        if node_rank[g.in_degree[u]] > node_rank[g.in_degree[v]]:
            sigma_plus_r_out[u] += 1

        elif node_rank[g.in_degree[u]] > node_rank[g.in_degree[v]]:
            sigma_plus_r_in[v] += 1

    sigma_plus_total = {node : sigma_plus_r_in[node] + sigma_plus_r_out[node] for node in g.nodes}
    r_star = max(sigma_plus_total.items(), key = lambda x : x[1])
    core_indicator = {key : 1 if value < node_rank[r_star[0]] else 0 for key, value in node_rank.items()}
    return core_indicator

# if __name__ == "__main__":
#     g = nx.karate_club_graph() # testing for rich core undirected version
#     # g = read_amazon() # testing for rich core directed version
#     print(sum(rich_core_decomp_undir(g).values()) / g.number_of_nodes())

