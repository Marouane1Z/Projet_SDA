import numpy as np


class CSRGraph:
    """
    Graphe orienté pondéré en format Compressed Sparse Row (CSR).

    Attributs :
        n_nodes    : nombre de noeuds
        n_edges    : nombre d'arêtes
        indptr     : tableau de taille (n_nodes + 1), indptr[i]..indptr[i+1] = arêtes de i
        indices    : tableau des noeuds destination
        weights    : tableau des poids (distances en mètres)
        coords     : tableau (n_nodes, 2) de coordonnées (lat, lon), optionnel
    """

    def __init__(self, indptr, indices, weights, coords=None):
        self.indptr = np.array(indptr, dtype=np.int32)
        self.indices = np.array(indices, dtype=np.int32)
        self.weights = np.array(weights, dtype=np.float64)
        self.coords = np.array(coords, dtype=np.float64) if coords is not None else None
        self.n_nodes = len(self.indptr) - 1
        self.n_edges = len(self.indices)

    def get_neighbors(self, node):
        """Retourne les voisins et poids d'un noeud sous forme d'itérateur de (voisin, poids)."""
        start = int(self.indptr[node])
        end = int(self.indptr[node + 1])
        return zip(self.indices[start:end], self.weights[start:end])

    def get_coords(self, node):
        """Retourne (lat, lon) du noeud, ou None si pas de coordonnées."""
        if self.coords is None:
            return None
        return self.coords[node]

    def __repr__(self):
        return f"CSRGraph(n_nodes={self.n_nodes}, n_edges={self.n_edges})"
