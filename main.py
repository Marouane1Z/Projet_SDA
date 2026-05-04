"""
Point d'entrée principal du projet Route Planning.

Usage :
    python main.py --mode synthetic
    python main.py --mode osm
    python main.py --mode benchmark
"""

import argparse
import os
import pickle
import numpy as np
from graph.loader import load_graph, save_graph
from algorithms.dijkstra import dijkstra, reconstruct_path
from algorithms.astar import astar
from algorithms.alt import alt
from algorithms.ch import preprocess_ch, query_ch
from landmarks.selection import select_landmarks_random
from landmarks.precompute import precompute_landmark_distances
from benchmark.runner import run_benchmark
from benchmark.metrics import compute_stats
from benchmark.plots import plot_times, plot_distances
from data.generate_synthetic import generate_grid_graph

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

        rng = np.random.default_rng(42)
        queries = [
            (int(rng.integers(0, g.n_nodes)), int(rng.integers(0, g.n_nodes)))
            for _ in range(50)
        ]

        landmarks = select_landmarks_random(g, k=4)
        def dijkstra_dist(graph, src):
            d, _ = dijkstra(graph, src)
            return d
        landmark_dists = precompute_landmark_distances(g, landmarks, dijkstra_dist)
        ch_data, ch_node_rank = preprocess_ch(g)

        algorithms = {
            "Dijkstra": lambda g, s, t, **kw: dijkstra(g, s, t),
            "A*":       lambda g, s, t, **kw: astar(g, s, t),
            "ALT":      lambda g, s, t, **kw: alt(g, s, t, landmark_dists),
            "CH":       lambda g, s, t, **kw: query_ch(ch_data, ch_node_rank, s, t),
        }

        print("Lancement du benchmark (50 requetes x 4 algorithmes)...")
        df = run_benchmark(g, queries, algorithms)
        print(compute_stats(df).to_string(index=False))
        os.makedirs("results", exist_ok=True)
        df.to_csv("results/benchmark_synthetic.csv", index=False)
        plot_times(df, output_dir="results/figures")
        plot_distances(df, output_dir="results/figures")
        print("Résultats sauvegardés dans results/")

    elif args.mode == "osm":
        from data.extract_osm import extract_osm
        extract_osm("Paris, France", "data/graph_paris.pkl")

    elif args.mode == "benchmark":
        print("Chargement du graphe Paris...")
        g = load_graph("data/graph_paris.pkl")
        print(g)

        rng = np.random.default_rng(42)
        queries = [
            (int(rng.integers(0, g.n_nodes)), int(rng.integers(0, g.n_nodes)))
            for _ in range(50)
        ]

        CACHE_LM   = "data/landmark_dists.npy"
        CACHE_LM_I = "data/landmark_indices.npy"
        CACHE_CH   = "data/ch_cache.pkl"

        if os.path.exists(CACHE_LM) and os.path.exists(CACHE_LM_I):
            print("Chargement landmarks depuis cache...")
            landmark_dists = np.load(CACHE_LM)
            landmarks = np.load(CACHE_LM_I).tolist()
        else:
            print("Précalcul des landmarks (ALT)...")
            landmarks = select_landmarks_random(g, k=16)
            def dijkstra_dist(graph, src):
                d, _ = dijkstra(graph, src)
                return d
            landmark_dists = precompute_landmark_distances(g, landmarks, dijkstra_dist)
            np.save(CACHE_LM, landmark_dists)
            np.save(CACHE_LM_I, np.array(landmarks, dtype=np.int32))
            print("Landmarks sauvegardés.")

        if os.path.exists(CACHE_CH):
            print("Chargement CH depuis cache...")
            with open(CACHE_CH, "rb") as f:
                ch_data, ch_node_rank = pickle.load(f)
        else:
            print("Prétraitement CH (contraction hiérarchique)...")
            ch_data, ch_node_rank = preprocess_ch(g)
            with open(CACHE_CH, "wb") as f:
                pickle.dump((ch_data, ch_node_rank), f)
            print("CH sauvegardé.")

        algorithms = {
            "Dijkstra": lambda g, s, t, **kw: dijkstra(g, s, t),
            "A*":       lambda g, s, t, **kw: astar(g, s, t),
            "ALT":      lambda g, s, t, **kw: alt(g, s, t, landmark_dists),
            "CH":       lambda g, s, t, **kw: query_ch(ch_data, ch_node_rank, s, t),
        }

        print("Lancement du benchmark (50 requetes x 4 algorithmes)...")
        df = run_benchmark(g, queries, algorithms)

        print()
        print("=== Resultats ===")
        print(compute_stats(df).to_string(index=False))

        print()
        print("=== Verification coherence distances ===")
        pivot = df.pivot(index="query", columns="algorithm", values="distance")
        ok = (pivot.nunique(axis=1) == 1).all()
        print(f"Toutes les distances identiques : {ok}")
        if not ok:
            print(pivot[pivot.nunique(axis=1) > 1].head())

        os.makedirs("results", exist_ok=True)
        df.to_csv("results/benchmark_osm.csv", index=False)
        plot_times(df, prefix="osm")
        plot_distances(df, prefix="osm")
        print()
        print("Résultats sauvegardés dans results/")


if __name__ == "__main__":
    main()
