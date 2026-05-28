"""Build a PyTorch Geometric ``Data`` object from the MFDS contraindication CSV.

The public file `병용금기약물.csv` from the Korea Institute of Drug Safety &
Risk Management lists ~540k contraindicated ingredient pairs. We treat the
ingredient set as nodes and contraindicated pairs as edges, then train a
Graph Autoencoder so structurally similar ingredients land near each other in
embedding space. Those embeddings are later used by ``app.signal.gcn`` to do
\"similar ingredient\" lookups for the safety report.

Usage:
    >>> data, vocab = build_drug_graph(\"data/raw/dur_combo.csv\")
    >>> data.num_nodes, data.num_edges, data.x.shape

File format expected (case-insensitive header lookup):
    성분코드A, 성분명A, 성분코드B, 성분명B
Additional columns (e.g. 금기사유, ATC) are tolerated.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import TYPE_CHECKING

import pandas as pd

if TYPE_CHECKING:  # pragma: no cover - typing only
    import torch
    from torch_geometric.data import Data

NODE_FEATURE_DIM = 64  # hashed bag-of-character features; replaced with ATC if available

_COLUMN_ALIASES = {
    "ingredient_a_code": ["성분코드A", "성분코드_A", "ingredient_code_a", "ingr_code_a"],
    "ingredient_a_name": ["성분명A", "성분명_A", "ingredient_a", "ingr_a"],
    "ingredient_b_code": ["성분코드B", "성분코드_B", "ingredient_code_b", "ingr_code_b"],
    "ingredient_b_name": ["성분명B", "성분명_B", "ingredient_b", "ingr_b"],
}


def _resolve_column(df: pd.DataFrame, logical: str) -> str:
    candidates = _COLUMN_ALIASES[logical]
    lower_map = {c.lower(): c for c in df.columns}
    for cand in candidates:
        if cand.lower() in lower_map:
            return lower_map[cand.lower()]
    raise KeyError(
        f"could not find a column for {logical!r}; tried {candidates}; "
        f"actual columns: {list(df.columns)}"
    )


def load_combo_pairs(csv_path: str | Path) -> pd.DataFrame:
    """Load the contraindication CSV and normalise the two ingredient columns.

    Returns a DataFrame with two string columns: ``ingredient_a`` and
    ``ingredient_b``. Ingredient codes are preferred over names; names are used
    as a fallback.
    """
    df = pd.read_csv(csv_path, dtype=str).fillna("")
    try:
        col_a = _resolve_column(df, "ingredient_a_code")
        col_b = _resolve_column(df, "ingredient_b_code")
    except KeyError:
        col_a = _resolve_column(df, "ingredient_a_name")
        col_b = _resolve_column(df, "ingredient_b_name")
    out = pd.DataFrame({
        "ingredient_a": df[col_a].str.strip(),
        "ingredient_b": df[col_b].str.strip(),
    })
    out = out[(out["ingredient_a"] != "") & (out["ingredient_b"] != "")]
    out = out[out["ingredient_a"] != out["ingredient_b"]]
    return out.drop_duplicates().reset_index(drop=True)


def _hash_features(token: str, dim: int = NODE_FEATURE_DIM) -> list[float]:
    """Cheap deterministic node feature: hashed char-bigrams onto ``dim`` buckets.

    Replace with ATC one-hot or RDKit descriptors when those are available;
    GCN training works fine with the hashed init because the graph topology
    carries most of the signal.
    """
    feats = [0.0] * dim
    padded = f" {token} "
    for i in range(len(padded) - 1):
        bigram = padded[i : i + 2]
        h = int.from_bytes(
            hashlib.blake2b(bigram.encode("utf-8"), digest_size=4).digest(), "big"
        )
        feats[h % dim] += 1.0
    # L2 normalise so deeper bigrams don't dominate
    norm = sum(v * v for v in feats) ** 0.5 or 1.0
    return [v / norm for v in feats]


def build_drug_graph(
    csv_path: str | Path,
) -> tuple["Data", dict[str, int]]:
    """Read the combo CSV and emit a PyG ``Data`` graph plus the node vocab.

    Importing torch lazily keeps the API package importable without the ``[ml]``
    extras installed (relevant for the FastAPI runtime image).
    """
    import torch
    from torch_geometric.data import Data

    df = load_combo_pairs(csv_path)
    nodes: list[str] = sorted({*df["ingredient_a"], *df["ingredient_b"]})
    vocab: dict[str, int] = {name: i for i, name in enumerate(nodes)}

    src = df["ingredient_a"].map(vocab).to_numpy()
    dst = df["ingredient_b"].map(vocab).to_numpy()
    # undirected: include both directions
    edge_index = torch.tensor(
        [list(src) + list(dst), list(dst) + list(src)], dtype=torch.long
    )

    x = torch.tensor(
        [_hash_features(n) for n in nodes], dtype=torch.float
    )
    data = Data(x=x, edge_index=edge_index, num_nodes=len(nodes))
    return data, vocab
