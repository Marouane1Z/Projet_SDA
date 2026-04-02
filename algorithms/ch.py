# Contraction Hierarchies — squelette pour Saad
# TODO : implémenter la phase de contraction et la phase de query bidirectionnelle


def preprocess_ch(graph):
    """
    Phase de prétraitement : contracte les noeuds par ordre d'importance croissante.
    Ajoute des raccourcis (shortcuts) pour préserver les plus courts chemins.

    Returns:
        ch_graph  : graphe augmenté avec les shortcuts
        node_order : ordre de contraction des noeuds
    """
    raise NotImplementedError("CH preprocess non implémenté")


def query_ch(ch_graph, node_order, source, target):
    """
    Phase de requête bidirectionnelle sur le graphe contracté.

    Returns:
        distance : float
        path     : list[int]
    """
    raise NotImplementedError("CH query non implémenté")
