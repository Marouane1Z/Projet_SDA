import time
import numpy as np
import pandas as pd


def run_benchmark(graph, queries, algorithms, landmark_dists=None):
    """
    Exécute un benchmark sur un ensemble de requêtes source/target.

    Args:
        graph         : CSRGraph
        queries       : list de (source, target)
        algorithms    : dict nom -> fonction(graph, source, target, ...)
        landmark_dists: np.array (k, n) pour ALT, sinon None

    Returns:
        DataFrame pandas avec colonnes : algorithm, query, time_ms, distance
    """
    results = []

    for algo_name, algo_fn in algorithms.items():
        for i, (src, tgt) in enumerate(queries):
            start = time.perf_counter()

            dist, _ = algo_fn(graph, src, tgt)

            elapsed_ms = (time.perf_counter() - start) * 1000
            d = dist[tgt] if not np.isinf(dist[tgt]) else None

            results.append({
                "algorithm": algo_name,
                "query": i,
                "source": src,
                "target": tgt,
                "time_ms": round(elapsed_ms, 4),
                "distance": d,
            })

    return pd.DataFrame(results)
