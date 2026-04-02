def compute_stats(df):
    """
    Calcule les statistiques de benchmark par algorithme.

    Returns:
        DataFrame groupé : mean, median, min, max de time_ms
    """
    return df.groupby("algorithm")["time_ms"].agg(
        mean="mean",
        median="median",
        min="min",
        max="max",
    ).reset_index()
