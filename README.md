# Route Planning — SDA M1

Moteur de calcul d'itinéraires comparant plusieurs algorithmes de plus court chemin.

## Groupe
- **Rayane** — Données & Graphe (`data/`, `graph/`, `landmarks/`)
- **Merouane** — Algorithmes (`algorithms/`) + tests
- **Saad** — Benchmark (`benchmark/`) + Contraction Hierarchies + rapport

## Structure
```
route_planning/
├── data/           # Extraction OSM et génération synthétique
├── graph/          # Structure CSR (csr_graph.py, haversine.py, loader.py)
├── algorithms/     # Dijkstra, A*, ALT, CH
├── landmarks/      # Sélection et précalcul des landmarks
├── benchmark/      # Runner, métriques, plots
├── results/        # Figures générées
├── tests/          # Tests unitaires
└── main.py
```

## Installation
```bash
pip install -r requirements.txt
```

## Utilisation
```bash
# Test rapide sur graphe synthétique
python main.py --mode synthetic

# Extraction du graphe OSM de Paris
python main.py --mode osm

# Benchmark
python main.py --mode benchmark
```
