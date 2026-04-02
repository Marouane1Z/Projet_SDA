import heapq
import numpy as np


def dijkstra(graph, source, target=None):
    """
    Algorithme de Dijkstra sur un CSRGraph.

    Args:
        graph  : CSRGraph
        source : noeud source
        target : noeud cible (optionnel, arrête dès qu'atteint)

    Returns:
        dist : np.array de distances depuis source (inf si non atteint)
        prev : np.array des prédécesseurs (-1 si inconnu)
    """
    n = graph.n_nodes
    dist = np.full(n, np.inf, dtype=np.float64)
    prev = np.full(n, -1, dtype=np.int32)
    dist[source] = 0.0

    heap = [(0.0, source)]

    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]:
            continue
        if target is not None and u == target:
            break
        for v, w in graph.get_neighbors(u):
            nd = d + w
            if nd < dist[v]:
                dist[v] = nd
                prev[v] = u
                heapq.heappush(heap, (nd, v))

    return dist, prev


def reconstruct_path(prev, source, target):
    """Reconstruit le chemin source → target depuis le tableau prev."""
    path = []
    node = target
    while node != -1:
        path.append(int(node))
        node = prev[node]
    path.reverse()
    if path[0] != source:
        return []
    return path
