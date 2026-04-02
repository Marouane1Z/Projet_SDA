import heapq
import numpy as np


def alt(graph, source, target, landmark_dists):
    """
    Algorithme ALT (A* + Landmarks + Triangle inequality).

    Utilise les distances précalculées depuis les landmarks pour construire
    une heuristique admissible plus précise que haversine.

    Heuristique : h(u) = max sur landmarks l de max(0, d(l, target) - d(l, u))

    Sur graphe dirigé, la valeur absolue n'est pas admissible car d(l,u) - d(l,target)
    peut surestimer d(u, target). On garde seulement d(l,target) - d(l,u) >= 0.

    Args:
        graph           : CSRGraph
        source          : noeud source
        target          : noeud cible
        landmark_dists  : np.array (k, n_nodes) — distances landmarks précalculées

    Returns:
        dist : np.array de distances depuis source
        prev : np.array des prédécesseurs
    """
    n = graph.n_nodes
    dist = np.full(n, np.inf, dtype=np.float64)
    prev = np.full(n, -1, dtype=np.int32)
    dist[source] = 0.0

    def h(u):
        return float(np.max(np.maximum(0.0, landmark_dists[:, target] - landmark_dists[:, u])))

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
