"""
Point d'entrée principal du projet Route Planning.

Usage :
    python main.py --mode synthetic
    python main.py --mode osm
    python main.py --mode benchmark
"""

import argparse
from data.generate_synthetic import generate_grid_graph
from graph.loader import load_graph, save_graph
from algorithms.dijkstra import dijkstra, reconstruct_path


def main():
    parser = argparse.ArgumentParser(description="Route Planning — SDA M1")
    parser.add_argument("--mode", choices=["synthetic", "osm", "benchmark"], default="synthetic")
    args = parser.parse_args()

    if args.mode == "synthetic":
        print("Génération du graphe synthétique...")
        g = generate_grid_graph(10, 10)
        print(g)
        dist, prev = dijkstra(g, source=0, target=99)
        print(f"Distance 0 -> 99 : {dist[99]:.2f} m")
        path = reconstruct_path(prev, 0, 99)
        print(f"Chemin : {path}")

    elif args.mode == "osm":
        from data.extract_osm import extract_osm
        extract_osm("Paris, France", "data/graph_paris.pkl")

    elif args.mode == "benchmark":
        import numpy as np
        from graph.loader import load_graph
        from algorithms.dijkstra import dijkstra
        from algorithms.astar import astar
        from algorithms.alt import alt
        from landmarks.selection import select_landmarks_random
        from landmarks.precompute import precompute_landmark_distances
        from benchmark.runner import run_benchmark
        from benchmark.metrics import compute_stats
        from benchmark.plots import plot_times, plot_distances

        print("Chargement du graphe Paris...")
        g = load_graph("data/graph_paris.pkl")
        print(g)

        # Génération de 50 requêtes aléatoires reproductibles
        rng = np.random.default_rng(42)
        queries = [
            (int(rng.integers(0, g.n_nodes)), int(rng.integers(0, g.n_nodes)))
            for _ in range(50)
        ]

        # Précalcul des landmarks pour ALT (16 landmarks)
        print("Précalcul des landmarks (ALT)...")
        landmarks = select_landmarks_random(g, k=16)
        def dijkstra_dist(graph, src):
            d, _ = dijkstra(graph, src)
            return d
        landmark_dists = precompute_landmark_distances(g, landmarks, dijkstra_dist)

        # Algorithmes à comparer
        algorithms = {
            "Dijkstra": lambda g, s, t, **kw: dijkstra(g, s, t),
            "A*":       lambda g, s, t, **kw: astar(g, s, t),
            "ALT":      lambda g, s, t, **kw: alt(g, s, t, landmark_dists),
        }

        print("Lancement du benchmark (50 requetes x 3 algorithmes)...")
        df = run_benchmark(g, queries, algorithms)

        # Affichage des stats
        print()
        print("=== Resultats ===")
        print(compute_stats(df).to_string(index=False))

        # Vérification cohérence des distances
        print()
        print("=== Verification coherence distances ===")
        pivot = df.pivot(index="query", columns="algorithm", values="distance")
        ok = (pivot.nunique(axis=1) == 1).all()
        print(f"Toutes les distances identiques : {ok}")
        if not ok:
            print(pivot[pivot.nunique(axis=1) > 1].head())

        # Graphiques
        plot_times(df)
        plot_distances(df)
        print()
        print("Figures sauvegardees dans results/figures/")


if __name__ == "__main__":
    main()
