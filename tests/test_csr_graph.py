from graph.csr_graph import CSRGraph


def test_basic_graph():
    # Graphe simple : 0->1 (1.0), 0->2 (4.0), 1->2 (2.0)
    indptr  = [0, 2, 3, 3]
    indices = [1, 2, 2]
    weights = [1.0, 4.0, 2.0]
    g = CSRGraph(indptr, indices, weights)

    assert g.n_nodes == 3
    assert g.n_edges == 3
    assert g.get_neighbors(0) == [(1, 1.0), (2, 4.0)]
    assert g.get_neighbors(1) == [(2, 2.0)]
    assert g.get_neighbors(2) == []


def test_no_coords():
    g = CSRGraph([0], [], [])
    assert g.get_coords(0) is None


if __name__ == "__main__":
    test_basic_graph()
    test_no_coords()
    print("Tous les tests passent.")
