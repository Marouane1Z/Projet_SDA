import pickle
from graph.csr_graph import CSRGraph


def load_graph(path):
    """Charge un CSRGraph depuis un fichier pickle."""
    with open(path, "rb") as f:
        return pickle.load(f)


def save_graph(graph, path):
    """Sauvegarde un CSRGraph dans un fichier pickle."""
    with open(path, "wb") as f:
        pickle.dump(graph, f)
