import numpy as np


def select_landmarks_random(graph, k, seed=42):
    """Sélectionne k landmarks aléatoirement parmi les noeuds du graphe."""
    rng = np.random.default_rng(seed)
    return list(rng.choice(graph.n_nodes, size=k, replace=False))


def select_landmarks_farthest(graph, k, dijkstra_fn, start=0):
    """
    Sélectionne k landmarks par la méthode 'farthest point' :
    chaque nouveau landmark est le noeud le plus éloigné des landmarks existants.

    Args:
        graph       : CSRGraph
        k           : nombre de landmarks
        dijkstra_fn : fonction dijkstra(graph, source) -> distances (array numpy)
        start       : noeud de départ du premier landmark
    """
    landmarks = [start]
    min_dists = dijkstra_fn(graph, start)

    for _ in range(k - 1):
        next_lm = int(np.argmax(min_dists))
        landmarks.append(next_lm)
        new_dists = dijkstra_fn(graph, next_lm)
        min_dists = np.minimum(min_dists, new_dists)

    return landmarks
