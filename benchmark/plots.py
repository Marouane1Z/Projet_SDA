import matplotlib.pyplot as plt
import os


def plot_times(df, output_dir="results/figures", prefix="benchmark"):
    """Boxplot des temps d'exécution par algorithme."""
    os.makedirs(output_dir, exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, 5))

    algos = df["algorithm"].unique()
    data = [df[df["algorithm"] == a]["time_ms"].values for a in algos]

    ax.boxplot(data, labels=algos)
    ax.set_ylabel("Temps (ms)")
    ax.set_title("Comparaison des algorithmes de plus court chemin")
    ax.grid(True, linestyle="--", alpha=0.5)

    path = os.path.join(output_dir, f"{prefix}_times.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Figure sauvegardée : {path}")


def plot_distances(df, output_dir="results/figures", prefix="benchmark"):
    """Scatter plot distances calculées par algorithme (vérification cohérence)."""
    os.makedirs(output_dir, exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, 5))

    markers = ["o", "s", "^", "D"]
    algos = list(df["algorithm"].unique())
    n = len(algos)
    offsets = [(i - (n - 1) / 2) * 0.3 for i in range(n)]

    for algo, offset, marker in zip(algos, offsets, markers):
        subset = df[df["algorithm"] == algo]
        ax.scatter(subset["query"] + offset, subset["distance"],
                   label=algo, s=18, marker=marker)

    ax.set_xlabel("Requête")
    ax.set_ylabel("Distance (m)")
    ax.set_title("Distances calculées par algorithme")
    ax.legend()
    ax.grid(True, linestyle="--", alpha=0.5)

    path = os.path.join(output_dir, f"{prefix}_distances.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Figure sauvegardée : {path}")
