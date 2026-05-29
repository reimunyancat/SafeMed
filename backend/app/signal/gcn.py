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


def _embedding_boost(drugs: list) -> dict[str, float]:
    """Per-drug boost in [0, 1]. DrugRef.ingredient_codes 를 vocab(성분코드 키) 에 lookup."""
    from app.rules.types import DrugRef
    out: dict[str, float] = {}
    for d in drugs:
        did = d.item_seq if isinstance(d, DrugRef) else str(d)
        out[did] = 0.0
    bundle = _load_embeddings()
    if bundle is None or len(drugs) < 2:
        return out
    vocab, embeddings = bundle
    try:
        import torch  # noqa: F401
    except ImportError:
        return out

    drug_idxs: list[tuple[str, list[int]]] = []
    for d in drugs:
        if isinstance(d, DrugRef):
            did = d.item_seq
            idxs = [vocab[c] for c in d.ingredient_codes if c in vocab]
        else:
            did = str(d)
            idxs = [vocab[did]] if did in vocab else []
        if idxs:
            drug_idxs.append((did, idxs))

    if len(drug_idxs) < 2:
        return out

    norms = embeddings.norm(dim=1).clamp(min=1e-9)
    for i, (drug_a, idxs_a) in enumerate(drug_idxs):
        for drug_b, idxs_b in drug_idxs[i + 1:]:
            best_sim = 0.0
            for ia in idxs_a:
                for ib in idxs_b:
                    sim = float(
                        (embeddings[ia] @ embeddings[ib])
                        / (norms[ia] * norms[ib])
                    )
                    if sim > best_sim:
                        best_sim = sim
            contribution = max(0.0, best_sim) ** 2
            out[drug_a] = max(out[drug_a], contribution)
            out[drug_b] = max(out[drug_b], contribution)
    return out


def score_drugs(
    drugs: list,
    reference_graph: nx.Graph | None = None,
) -> list[GCNScore]:
    """drugs 는 list[DrugRef] 또는 list[str]. DrugRef 면 ingredient_codes 로 vocab lookup."""
    from app.rules.types import DrugRef
    if not drugs:
        return []
    ids = [d.item_seq if isinstance(d, DrugRef) else str(d) for d in drugs]
    g = build_clique(ids)
    if reference_graph is not None:
        for u, v in g.edges():
            if reference_graph.has_edge(u, v):
                g[u][v]["weight"] = float(reference_graph[u][v].get("weight", 1.0))

    if len(ids) == 1:
        return [GCNScore(drug=ids[0], centrality=0.0, risk_amplifier=0.0)]

    centrality = nx.degree_centrality(g)
    n = len(ids)
    amp_base = min(1.0, (n - 1) / 6.0)
    boosts = _embedding_boost(drugs)
    out: list[GCNScore] = []
    for d, did in zip(drugs, ids, strict=True):
        base = float(amp_base * centrality[did])
        boost = float(boosts.get(did, 0.0))
        combined = min(1.0, base * (1.0 + 0.5 * boost))
        out.append(
            GCNScore(
                drug=did,
                centrality=float(centrality[did]),
                risk_amplifier=combined,
                embedding_boost=boost,
            )
        )
    return out