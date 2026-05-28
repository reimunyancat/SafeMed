"""GCN co-medication graph training & embedding utilities.

This subpackage is optional: it is only needed to (re)train the GCN encoder
that backs ``app.signal.gcn``'s neighbour search. The runtime API (``analyze``)
works without it because ``signal/gcn.py`` falls back to a NetworkX degree
centrality heuristic when no trained embedding file is found.

Install extras with ``pip install -e \".[ml]\"`` to pull in torch + PyG.
"""

from .graph_builder import (
    build_drug_graph,
    load_combo_pairs,
    NODE_FEATURE_DIM,
)

__all__ = [
    "build_drug_graph",
    "load_combo_pairs",
    "NODE_FEATURE_DIM",
]
