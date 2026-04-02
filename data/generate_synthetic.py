import numpy as np
from graph.csr_graph import CSRGraph


def generate_grid_graph(rows, cols, noise=0.01, seed=42):
    """
    Génère un graphe synthétique en grille perturbée.

    Chaque noeud (i, j) est connecté à ses voisins (haut, bas, gauche, droite).
    Les coordonnées sont légèrement perturbées avec du bruit aléatoire.
    Les poids = distance euclidienne entre les coordonnées.

    Args:
        rows, cols : dimensions de la grille
        noise      : amplitude du bruit aléatoire sur les coords
        seed       : graine aléatoire pour reproductibilité

    Returns:
        CSRGraph
    """
    rng = np.random.default_rng(seed)
    n = rows * cols

    # Coordonnées de base : grille uniforme [0,1] x [0,1]
    base_lat = np.linspace(48.8, 48.9, rows)
    base_lon = np.linspace(2.3, 2.4, cols)
    coords = np.zeros((n, 2))
    for i in range(rows):
        for j in range(cols):
            node = i * cols + j
            coords[node, 0] = base_lat[i] + rng.uniform(-noise, noise)
            coords[node, 1] = base_lon[j] + rng.uniform(-noise, noise)

    # Construction des arêtes
    adj = [[] for _ in range(n)]
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    for i in range(rows):
        for j in range(cols):
            u = i * cols + j
            for di, dj in directions:
                ni, nj = i + di, j + dj
                if 0 <= ni < rows and 0 <= nj < cols:
                    v = ni * cols + nj
                    dist = float(np.linalg.norm(coords[u] - coords[v])) * 111_000
                    adj[u].append((v, dist))

    # Construction CSR
    indptr = [0]
    indices = []
    weights = []
    for neighbors in adj:
        for (dst, w) in neighbors:
            indices.append(dst)
            weights.append(w)
        indptr.append(len(indices))

    return CSRGraph(indptr, indices, weights, coords)


if __name__ == "__main__":
    g = generate_grid_graph(10, 10)
    print(g)
    print("Voisins du noeud 0 :", g.get_neighbors(0))
