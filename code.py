import cpnet
import networkx as nx
import matplotlib.pyplot as plt

# Example code taken from 
# https://github.com/skojaku/core-periphery-detection/blob/master/notebooks/example1.ipynb

algorithm = cpnet.Surprise(20)
G = nx.karate_club_graph()
algorithm.detect(G)
c = algorithm.get_pair_id()
x = algorithm.get_coreness() # core = 1, periphery = 0

fig = plt.figure(figsize=(10, 7))
ax = plt.gca()
ax, pos = cpnet.draw(G, c, x, ax) 
"""
pos is a dict {node_id: (x, y)} where node_id is a node id
given by G.nodes(), and (x, y) is the (x, y) coordinate
of that node on the plot. Useful when testing out different
core periphery decomposition algorithms on the same graph.
"""
plt.show()