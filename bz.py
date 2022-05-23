"""
nodes labeled 1-n
u in neighbors(G, v): u is a not yet visited
    neighbor of vertex v in graph G

    we can represent G having a list of neighbors
"""
import networkx as nx

def BZ_core_decomp(graph: nx.Graph):
    n = graph.number_of_nodes()
    deg = [graph.degree[node] for node in graph.nodes]
    md = max(deg)

    vert = [0] * (n + 1) # set of vertices, sorted by degrees
    pos = [] # positions of vertices in vert are stored here
    bin = [0] * (md + 1) # for each possible degree, the position
    # of the first vertex of that degree in array vert

    for v in range(n):
        bin[graph.degree[v]] += 1

    start = 1
    for d in range(md + 1):
        num = bin[d]
        bin[d] = start
        start += num
    for v in range(n):
        pos.append(bin[graph.degree[v]])
        vert[pos[v]] = v
        bin[graph.degree[v]] += 1

    for d in range(md, 0, -1):
        bin[d] = bin[d-1]
    bin[0] = 1

    for i in range(n):
        v = vert[i]
        for u in graph[v]:
            if graph.degree[u] > graph.degree[v]:
                du = graph.degree[u]
                pu = pos[u]
                pw = bin[du]
                w = vert[pw]
                if u != w:
                    pos[u] = pw
                    vert[pu] = w
                    pos[w] = pu
                    vert[pw] = u
                bin[du] += 1
                deg[u] -= 1
    return deg