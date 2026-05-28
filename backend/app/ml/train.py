"""Train the SafeMed GCN encoder on the MFDS contraindication graph.

Run:
    python -m app.ml.train \\
        --combo-csv ../data/raw/dur_combo.csv \\
        --out ../data/processed/gcn_embeddings.pt \\
        --epochs 200

This is unsupervised link prediction (Graph Autoencoder). On the public 540k
pair CSV one epoch is ~2s on CPU and ~0.3s on a CUDA T4, so 200 epochs ~7min
CPU / ~1min GPU. The script:

1. Builds the drug graph + hashed-bigram node features (``graph_builder``).
2. Splits edges into train/val/test using ``RandomLinkSplit``.
3. Trains ``GAE(GCNEncoder)`` with negative sampling + recon_loss.
4. Reports val/test ROC-AUC and AP at the end.
5. Saves ``{ \"vocab\": {...}, \"embeddings\": Tensor[N, out_dim] }`` to disk.

The saved file is what ``app.signal.gcn`` loads at runtime (path configurable
via ``GCN_EMBEDDING_PATH`` env var).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .graph_builder import build_drug_graph


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Train SafeMed GCN embeddings")
    p.add_argument(
        "--combo-csv",
        type=Path,
        required=True,
        help="Path to the MFDS 의약품안전사용서비스 contraindication CSV",
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("../data/processed/gcn_embeddings.pt"),
        help="Where to save the trained embeddings",
    )
    p.add_argument("--epochs", type=int, default=200)
    p.add_argument("--hidden", type=int, default=64)
    p.add_argument("--out-dim", type=int, default=32)
    p.add_argument("--lr", type=float, default=1e-2)
    p.add_argument("--device", default="auto", help="cpu | cuda | auto")
    p.add_argument("--seed", type=int, default=42)
    return p.parse_args(argv)


def _resolve_device(flag: str) -> str:
    if flag != "auto":
        return flag
    try:
        import torch

        return "cuda" if torch.cuda.is_available() else "cpu"
    except ImportError:
        return "cpu"


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)

    try:
        import torch
        from torch_geometric.transforms import RandomLinkSplit
    except ImportError as e:
        sys.stderr.write(
            f"[train.py] Missing optional dependency: {e}.\n"
            "Install with: pip install -e \".[ml]\"\n"
        )
        return 2

    from .gcn_model import build_gae

    device = _resolve_device(args.device)
    torch.manual_seed(args.seed)

    print(f"[train] loading graph from {args.combo_csv}")
    data, vocab = build_drug_graph(args.combo_csv)
    print(f"[train] nodes={data.num_nodes} edges={data.edge_index.size(1) // 2}")

    splitter = RandomLinkSplit(
        num_val=0.05,
        num_test=0.10,
        is_undirected=True,
        add_negative_train_samples=False,
    )
    train_data, val_data, test_data = splitter(data)

    model = build_gae(
        in_channels=data.x.size(1),
        hidden_channels=args.hidden,
        out_channels=args.out_dim,
    ).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)

    train_data = train_data.to(device)
    val_data = val_data.to(device)
    test_data = test_data.to(device)

    def _train_epoch() -> float:
        model.train()
        optimizer.zero_grad()
        z = model.encode(train_data.x, train_data.edge_index)
        loss = model.recon_loss(z, train_data.edge_label_index)
        loss.backward()
        optimizer.step()
        return float(loss)

    @torch.no_grad()
    def _eval(split) -> tuple[float, float]:
        model.eval()
        z = model.encode(split.x, split.edge_index)
        return model.test(
            z, split.edge_label_index, split.edge_label_index[:, :0]
        ) if False else model.test(
            z,
            split.edge_label_index[:, split.edge_label.bool()],
            split.edge_label_index[:, ~split.edge_label.bool()],
        )

    print(f"[train] running {args.epochs} epochs on {device}")
    for epoch in range(1, args.epochs + 1):
        loss = _train_epoch()
        if epoch % 20 == 0 or epoch == 1:
            val_auc, val_ap = _eval(val_data)
            print(
                f"[train] epoch={epoch:4d} loss={loss:.4f} "
                f"val_auc={val_auc:.4f} val_ap={val_ap:.4f}"
            )

    test_auc, test_ap = _eval(test_data)
    print(f"[train] FINAL test_auc={test_auc:.4f} test_ap={test_ap:.4f}")

    model.eval()
    with torch.no_grad():
        embeddings = model.encode(data.x.to(device), data.edge_index.to(device)).cpu()

    args.out.parent.mkdir(parents=True, exist_ok=True)
    torch.save(
        {
            "vocab": vocab,
            "embeddings": embeddings,
            "metadata": {
                "num_nodes": int(data.num_nodes),
                "num_edges": int(data.edge_index.size(1) // 2),
                "hidden": args.hidden,
                "out_dim": args.out_dim,
                "epochs": args.epochs,
                "test_auc": float(test_auc),
                "test_ap": float(test_ap),
            },
        },
        args.out,
    )
    sidecar = args.out.with_suffix(".meta.json")
    sidecar.write_text(
        json.dumps(
            {
                "num_nodes": int(data.num_nodes),
                "num_edges": int(data.edge_index.size(1) // 2),
                "test_auc": float(test_auc),
                "test_ap": float(test_ap),
                "out_dim": args.out_dim,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    print(f"[train] saved embeddings to {args.out}")
    print(f"[train] saved metadata to {sidecar}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
