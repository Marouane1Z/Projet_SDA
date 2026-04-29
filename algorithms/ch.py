import heapq
import numpy as np


def _witness_search(fwd_adj, source, max_dist, exclude, hop_limit=5):
    """Dijkstra limité depuis source, excluant le noeud contracté."""
    dist = {source: 0.0}
    heap = [(0.0, 0, source)]
    while heap:
        d, hops, u = heapq.heappop(heap)
        if d > dist.get(u, np.inf) or hops >= hop_limit or d > max_dist:
            continue
        for v, w in fwd_adj[u]:
            if v == exclude:
                continue
            nd = d + w
            if nd < dist.get(v, np.inf):
                dist[v] = nd
                heapq.heappush(heap, (nd, hops + 1, v))
    return dist


def _edge_difference(fwd_adj, bwd_adj, v, contracted):
    """Raccourcis à ajouter - arêtes supprimées si on contracte v."""
    in_nbrs = [(u, w) for u, w in bwd_adj[v] if not contracted[u]]
    out_nbrs = [(nb, w) for nb, w in fwd_adj[v] if not contracted[nb]]
    if not in_nbrs or not out_nbrs:
        return -(len(in_nbrs) + len(out_nbrs))
    max_out_w = max(w for _, w in out_nbrs)
    shortcuts = 0
    for u, w_uv in in_nbrs:
        witness = _witness_search(fwd_adj, u, w_uv + max_out_w, v)
        for nb, w_vw in out_nbrs:
            if u != nb and witness.get(nb, np.inf) > w_uv + w_vw:
                shortcuts += 1
    return shortcuts - (len(in_nbrs) + len(out_nbrs))


def preprocess_ch(graph):
    """
    Phase de prétraitement : contracte les noeuds par ordre d'importance croissante.
    Ajoute des raccourcis pour préserver les plus courts chemins.

    Returns:
        ch_data    : dict avec fwd_up, bwd_up, node_rank, n_nodes
        node_rank  : tableau des rangs de contraction (numpy int32)
    """
    n = graph.n_nodes

    fwd_adj = [list(graph.get_neighbors(u)) for u in range(n)]
    bwd_adj = [[] for _ in range(n)]
    for u in range(n):
        for v, w in fwd_adj[u]:
            bwd_adj[v].append((u, w))

    contracted = [False] * n
    node_rank = np.zeros(n, dtype=np.int32)

    print("CH : calcul des importances initiales...")
    heap = []
    for v in range(n):
        heapq.heappush(heap, (_edge_difference(fwd_adj, bwd_adj, v, contracted), v))

    rank = 0
    print("CH : contraction des noeuds...")
    while heap:
        imp, v = heapq.heappop(heap)
        if contracted[v]:
            continue

        # Lazy update : recalcule l'importance réelle au moment de la contraction
        real_imp = _edge_difference(fwd_adj, bwd_adj, v, contracted)
        if real_imp > imp:
            heapq.heappush(heap, (real_imp, v))
            continue

        # Contracter v : trouver les raccourcis nécessaires
        in_nbrs = [(u, w) for u, w in bwd_adj[v] if not contracted[u]]
        out_nbrs = [(nb, w) for nb, w in fwd_adj[v] if not contracted[nb]]

        if in_nbrs and out_nbrs:
            max_out_w = max(w for _, w in out_nbrs)
            for u, w_uv in in_nbrs:
                witness = _witness_search(fwd_adj, u, w_uv + max_out_w, v)
                for nb, w_vw in out_nbrs:
                    if u == nb:
                        continue
                    sc_dist = w_uv + w_vw
                    if witness.get(nb, np.inf) > sc_dist:
                        # Ajouter raccourci u -> nb (ou mettre à jour si existe)
                        updated = False
                        for i, (dst, _) in enumerate(fwd_adj[u]):
                            if dst == nb:
                                if fwd_adj[u][i][1] > sc_dist:
                                    fwd_adj[u][i] = (nb, sc_dist)
                                    for j, (src, _) in enumerate(bwd_adj[nb]):
                                        if src == u:
                                            bwd_adj[nb][j] = (u, sc_dist)
                                            break
                                updated = True
                                break
                        if not updated:
                            fwd_adj[u].append((nb, sc_dist))
                            bwd_adj[nb].append((u, sc_dist))

        contracted[v] = True
        node_rank[v] = rank
        rank += 1

        if rank % 10000 == 0:
            print(f"  {rank}/{n} noeuds contractés...")

    # Graphes montants pour la requête bidirectionnelle
    # fwd_up[u] : arêtes u->v avec rank(v) > rank(u)
    # bwd_up[v] : arêtes u->v inverses avec rank(u) > rank(v), utilisées pour la recherche arrière
    fwd_up = [[] for _ in range(n)]
    bwd_up = [[] for _ in range(n)]
    for u in range(n):
        for v, w in fwd_adj[u]:
            if node_rank[v] > node_rank[u]:
                fwd_up[u].append((v, w))
            else:
                bwd_up[v].append((u, w))

    ch_data = {'fwd_up': fwd_up, 'bwd_up': bwd_up, 'node_rank': node_rank, 'n_nodes': n}
    return ch_data, node_rank


def query_ch(ch_data, node_rank, source, target):
    """
    Requête bidirectionnelle sur le graphe contracté.
    Recherche avant depuis source + recherche arrière depuis target,
    restreintes aux arêtes montantes.

    Returns:
        dist_array : np.array avec dist_array[target] = distance optimale
        None       : reconstruction de chemin non supportée
    """
    if source == target:
        dist_result = np.full(ch_data['n_nodes'], np.inf)
        dist_result[target] = 0.0
        return dist_result, None

    n = ch_data['n_nodes']
    fwd_up = ch_data['fwd_up']
    bwd_up = ch_data['bwd_up']

    dist_fwd = np.full(n, np.inf)
    dist_bwd = np.full(n, np.inf)
    dist_fwd[source] = 0.0
    dist_bwd[target] = 0.0

    heap_fwd = [(0.0, source)]
    heap_bwd = [(0.0, target)]
    settled_fwd = set()
    settled_bwd = set()
    mu = np.inf

    while heap_fwd or heap_bwd:
        d_top_fwd = heap_fwd[0][0] if heap_fwd else np.inf
        d_top_bwd = heap_bwd[0][0] if heap_bwd else np.inf

        if d_top_fwd + d_top_bwd >= mu:
            break

        if d_top_fwd <= d_top_bwd:
            d, u = heapq.heappop(heap_fwd)
            if u in settled_fwd or d > dist_fwd[u]:
                continue
            settled_fwd.add(u)
            if dist_bwd[u] < np.inf:
                mu = min(mu, dist_fwd[u] + dist_bwd[u])
            for v, w in fwd_up[u]:
                nd = dist_fwd[u] + w
                if nd < dist_fwd[v]:
                    dist_fwd[v] = nd
                    heapq.heappush(heap_fwd, (nd, v))
        else:
            d, u = heapq.heappop(heap_bwd)
            if u in settled_bwd or d > dist_bwd[u]:
                continue
            settled_bwd.add(u)
            if dist_fwd[u] < np.inf:
                mu = min(mu, dist_fwd[u] + dist_bwd[u])
            for v, w in bwd_up[u]:
                nd = dist_bwd[u] + w
                if nd < dist_bwd[v]:
                    dist_bwd[v] = nd
                    heapq.heappush(heap_bwd, (nd, v))

    dist_result = np.full(n, np.inf)
    dist_result[target] = mu
    return dist_result, None
