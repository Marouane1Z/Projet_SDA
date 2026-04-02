import numpy as np


def precompute_landmark_distances(graph, landmarks, dijkstra_fn, output_path=None):
    """
    Précalcule les distances depuis chaque landmark vers tous les noeuds.

    Retourne une matrice numpy de forme (k, n_nodes) où
    distances[i][v] = distance du landmark i au noeud v.

    Args:
        graph        : CSRGraph
        landmarks    : liste d'indices de landmarks
        dijkstra_fn  : fonction dijkstra(graph, source) -> np.array de distances
        output_path  : si fourni, sauvegarde la matrice en .npy
    """
    k = len(landmarks)
    n = graph.n_nodes
    distances = np.full((k, n), np.inf, dtype=np.float64)

    for i, lm in enumerate(landmarks):
        print(f"Précalcul landmark {i+1}/{k} (noeud {lm})")
        distances[i] = dijkstra_fn(graph, lm)

    if output_path:
        np.save(output_path, distances)
        print(f"Matrice sauvegardée dans {output_path}")

    return distances


def load_landmark_distances(path):
    """Charge la matrice de distances landmarks depuis un fichier .npy."""
    return np.load(path)
