import heapq
import numpy as np
from graph.haversine import haversine


def astar(graph, source, target):
    """
    Algorithme A* sur un CSRGraph avec heuristique haversine.

    Nécessite que graph.coords soit défini (lat, lon par noeud).

    Args:
        graph  : CSRGraph avec coords
        source : noeud source
        target : noeud cible

    Returns:
        dist : np.array de distances depuis source
        prev : np.array des prédécesseurs
    """
    assert graph.coords is not None, "A* requiert des coordonnées GPS (graph.coords)"

    n = graph.n_nodes
    dist = np.full(n, np.inf, dtype=np.float64)
    prev = np.full(n, -1, dtype=np.int32)
    dist[source] = 0.0

    lat_t, lon_t = graph.coords[target]

    def h(u):
        lat_u, lon_u = graph.coords[u]
        return haversine(lat_u, lon_u, lat_t, lon_t)

    heap = [(h(source), 0.0, source)]

    while heap:
        _, d, u = heapq.heappop(heap)
        if d > dist[u]:
            continue
        if u == target:
            break
        for v, w in graph.get_neighbors(u):
            nd = d + w
            if nd < dist[v]:
                dist[v] = nd
                prev[v] = u
                heapq.heappush(heap, (nd + h(v), nd, v))

    return dist, prev
