import osmnx as ox
import numpy as np
import pickle
from graph.csr_graph import CSRGraph


def extract_osm(place_name, output_path):
    """
    Extrait un graphe routier OSM pour une ville donnée et le convertit en CSRGraph.

    Etapes :
        1. Téléchargement du graphe via osmnx
        2. Remapping des IDs OSM (arbitraires) vers 0..n-1
        3. Extraction des arêtes avec leur longueur
        4. Construction du CSR

    Args:
        place_name  : ex. "Paris, France"
        output_path : chemin de sortie .pkl, ex. "data/graph_paris.pkl"
    """
    print(f"Téléchargement du graphe OSM pour : {place_name}")
    G = ox.graph_from_place(place_name, network_type="drive")
    G = ox.add_edge_speeds(G)
    G = ox.add_edge_travel_times(G)

    nodes, edges = ox.graph_to_gdfs(G)

    # Remapping des IDs OSM → entiers 0..n-1
    osm_ids = list(nodes.index)
    id_map = {osm_id: i for i, osm_id in enumerate(osm_ids)}
    n = len(osm_ids)

    # Coordonnées GPS
    coords = np.zeros((n, 2), dtype=np.float64)
    for osm_id, i in id_map.items():
        coords[i, 0] = nodes.loc[osm_id, "y"]  # lat
        coords[i, 1] = nodes.loc[osm_id, "x"]  # lon

    # Construction des listes d'adjacence
    adj = [[] for _ in range(n)]
    for (u, v, _), row in edges.iterrows():
        if u in id_map and v in id_map:
            weight = row.get("length", 1.0)
            adj[id_map[u]].append((id_map[v], float(weight)))

    # Construction CSR
    indptr = [0]
    indices = []
    weights = []
    for neighbors in adj:
        for (dst, w) in neighbors:
            indices.append(dst)
            weights.append(w)
        indptr.append(len(indices))

    graph = CSRGraph(indptr, indices, weights, coords)
    print(f"Graphe extrait : {graph}")

    with open(output_path, "wb") as f:
        pickle.dump(graph, f)
    print(f"Sauvegardé dans {output_path}")

    return graph


if __name__ == "__main__":
    extract_osm("Paris, France", "data/graph_paris.pkl")
