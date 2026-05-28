"""Lightweight 2-layer GCN encoder used by the Graph Autoencoder (GAE).

This is *unsupervised* link prediction: we never need a labelled \"is risky\"
ground truth, which is exactly the design choice that lets us defend the AI
layer at the competition. The encoder maps every ingredient node to a
``out_channels``-dim vector; ``GAE.recon_loss`` then teaches it that
contraindicated pairs should sit close while random pairs should not.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    import torch


def build_encoder(
    in_channels: int,
    hidden_channels: int = 64,
    out_channels: int = 32,
) -> "torch.nn.Module":
    """Construct the 2-layer GCN encoder.

    Kept as a builder function (rather than a class definition at module top
    level) so the file is safe to import without ``torch`` installed.
    """
    import torch
    from torch import nn
    from torch_geometric.nn import GCNConv

    class GCNEncoder(nn.Module):
        def __init__(self) -> None:
            super().__init__()
            self.conv1 = GCNConv(in_channels, hidden_channels)
            self.conv2 = GCNConv(hidden_channels, out_channels)

        def forward(self, x: torch.Tensor, edge_index: torch.Tensor) -> torch.Tensor:
            x = self.conv1(x, edge_index).relu()
            return self.conv2(x, edge_index)

    return GCNEncoder()


def build_gae(in_channels: int, hidden_channels: int = 64, out_channels: int = 32):
    """Return a ``torch_geometric.nn.GAE`` wrapping the 2-layer GCN encoder."""
    from torch_geometric.nn import GAE

    return GAE(build_encoder(in_channels, hidden_channels, out_channels))
