"""Evaluate a trained SafeMed GCN embedding file.

Run:
    python -m app.ml.evaluate --emb ../data/processed/gcn_embeddings.pt \\
        --query 아세트아미노펜 --topk 10

Prints the top-K cosine-nearest ingredients in embedding space, which is what
``app.signal.gcn`` uses to surface \"similar ingredient\" warnings in the
safety report.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Inspect SafeMed GCN embeddings")
    p.add_argument("--emb", type=Path, required=True)
    p.add_argument("--query", required=True, help="Ingredient name/code to look up")
    p.add_argument("--topk", type=int, default=10)
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    try:
        import torch
    except ImportError as e:
        sys.stderr.write(f"[evaluate.py] missing torch: {e}\n")
        return 2

    bundle = torch.load(args.emb, map_location="cpu", weights_only=False)
    vocab: dict[str, int] = bundle["vocab"]
    embeddings: torch.Tensor = bundle["embeddings"]

    if args.query not in vocab:
        # try case-insensitive fallback
        lower = {k.lower(): k for k in vocab}
        if args.query.lower() in lower:
            key = lower[args.query.lower()]
        else:
            sys.stderr.write(
                f"[evaluate.py] query {args.query!r} not in vocab (size={len(vocab)})\n"
            )
            return 1
    else:
        key = args.query

    idx = vocab[key]
    target = embeddings[idx]
    norm = embeddings.norm(dim=1).clamp(min=1e-9)
    target_norm = target.norm().clamp(min=1e-9)
    sims = (embeddings @ target) / (norm * target_norm)

    top = sims.argsort(descending=True)[: args.topk + 1]
    inv_vocab = {v: k for k, v in vocab.items()}
    print(f"top-{args.topk} neighbours of {key!r}:")
    rank = 0
    for i in top.tolist():
        if i == idx:
            continue
        rank += 1
        print(f"  {rank:2d}. {inv_vocab[i]:<30s} cos={sims[i].item():+.4f}")
        if rank >= args.topk:
            break
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
