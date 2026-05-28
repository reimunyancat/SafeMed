from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import networkx as nx


@dataclass(frozen=True)
class GCNScore:
    drug: str
    centrality: float
    risk_amplifier: float
    embedding_boost: float = 0.0


def build_clique(drugs: list[str]) -> nx.Graph:
    g: nx.Graph = nx.Graph()
    for d in drugs:
        g.add_node(d)
    for i, a in enumerate(drugs):
        for b in drugs[i + 1 :]:
            g.add_edge(a, b, weight=1.0)
    return g


@lru_cache(maxsize=1)
def _load_embeddings() -> tuple[dict[str, int], object] | None:
    """Try to load a trained GCN embedding bundle; return None if unavailable."""
    path_str = os.environ.get(
        "GCN_EMBEDDING_PATH", "../data/processed/gcn_embeddings.pt"
    )
    path = Path(path_str)
    if not path.exists():
        return None
    try:
        import torch
    except ImportError:
        return None
    try:
        bundle = torch.load(path, map_location="cpu", weights_only=False)
    except Exception:
        return None
    return bundle["vocab"], bundle["embeddings"]


def _embedding_boost(drugs: list[str]) -> dict[str, float]:
    """Per-drug boost in [0, 1] from cosine similarity within the regimen."""
    bundle = _load_embeddings()
    if bundle is None:
        return {d: 0.0 for d in drugs}
    vocab, embeddings = bundle
    try:
        import torch
    except ImportError:
        return {d: 0.0 for d in drugs}

    present = {d: vocab[d] for d in drugs if d in vocab}
    if len(present) < 2:
        return {d: 0.0 for d in drugs}

    norms = embeddings.norm(dim=1).clamp(min=1e-9)
    boosts: dict[str, float] = {d: 0.0 for d in drugs}
    items = list(present.items())
    for i, (drug_a, idx_a) in enumerate(items):
        for drug_b, idx_b in items[i + 1 :]:
            sim = float(
                (embeddings[idx_a] @ embeddings[idx_b])
                / (norms[idx_a] * norms[idx_b])
            )
            contribution = max(0.0, sim) ** 2
            boosts[drug_a] = max(boosts[drug_a], contribution)
            boosts[drug_b] = max(boosts[drug_b], contribution)
    return boosts


def score_drugs(
    drugs: list[str], reference_graph: nx.Graph | None = None
) -> list[GCNScore]:
    if not drugs:
        return []
    g = build_clique(drugs)
    if reference_graph is not None:
        for u, v in g.edges():
            if reference_graph.has_edge(u, v):
                g[u][v]["weight"] = float(
                    reference_graph[u][v].get("weight", 1.0)
                )

    if len(drugs) == 1:
        return [GCNScore(drug=drugs[0], centrality=0.0, risk_amplifier=0.0)]

    centrality = nx.degree_centrality(g)
    n = len(drugs)
    amp_base = min(1.0, (n - 1) / 6.0) 
    boosts = _embedding_boost(drugs)
    out: list[GCNScore] = []
    for d in drugs:
        base = float(amp_base * centrality[d])
        boost = float(boosts.get(d, 0.0))
        combined = min(1.0, base * (1.0 + 0.5 * boost))
        out.append(
            GCNScore(
                drug=d,
                centrality=float(centrality[d]),
                risk_amplifier=combined,
                embedding_boost=boost,
            )
        )
    return out