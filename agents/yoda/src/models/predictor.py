"""JEPA predictor module.

A lightweight transformer that takes *context* patch embeddings together
with learnable *target position* embeddings and predicts the
representations that the target encoder would produce for the masked
(target) patches.  This is the core component that turns V-JEPA / VL-JEPA
into a non-contrastive self-supervised learner in representation space.
"""

from __future__ import annotations

import math
from typing import Any, Dict, Optional

import torch
import torch.nn as nn


DEFAULT_PREDICTOR_CONFIG: Dict[str, Any] = {
    "embed_dim": 384,
    "num_heads": 6,
    "depth": 3,
    "mlp_ratio": 4.0,
    "dropout": 0.0,
    "max_target_positions": 196,   # 14x14 patch grid for 224-px images
}


class Predictor(nn.Module):
    """Transformer predictor that maps context patches to target patches.

    Architecture
    ------------
    * **Target query tokens** are learnable position embeddings looked up by
      the spatial index of each target patch.
    * Each of the ``depth`` layers is an ``nn.TransformerDecoderLayer``
      that performs self-attention among the query tokens and then
      cross-attention from queries into the context embeddings.
    * A final linear head maps back to ``embed_dim`` so that the output
      can be directly compared with the target encoder's patch embeddings.

    Args:
        config: Dictionary whose keys override
            :data:`DEFAULT_PREDICTOR_CONFIG`.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        super().__init__()
        cfg = {**DEFAULT_PREDICTOR_CONFIG, **(config or {})}

        self.embed_dim: int = cfg["embed_dim"]
        self.num_heads: int = cfg["num_heads"]
        self.depth: int = cfg["depth"]
        self.max_target_positions: int = cfg["max_target_positions"]

        dim_feedforward = int(self.embed_dim * cfg["mlp_ratio"])

        # ----------------------------------------------------------
        # Learnable position embeddings for target patch queries
        # ----------------------------------------------------------
        self.target_pos_embed = nn.Embedding(
            self.max_target_positions, self.embed_dim
        )
        self._init_pos_embed()

        # ----------------------------------------------------------
        # Context projection (optional dim alignment)
        # ----------------------------------------------------------
        self.context_proj = nn.Linear(self.embed_dim, self.embed_dim)

        # ----------------------------------------------------------
        # Transformer decoder layers (cross-attention from target to context)
        # ----------------------------------------------------------
        decoder_layer = nn.TransformerDecoderLayer(
            d_model=self.embed_dim,
            nhead=self.num_heads,
            dim_feedforward=dim_feedforward,
            dropout=cfg["dropout"],
            activation="gelu",
            batch_first=True,
            norm_first=True,
        )
        self.transformer_decoder = nn.TransformerDecoder(
            decoder_layer,
            num_layers=self.depth,
        )

        # ----------------------------------------------------------
        # Output head
        # ----------------------------------------------------------
        self.output_norm = nn.LayerNorm(self.embed_dim)
        self.output_head = nn.Linear(self.embed_dim, self.embed_dim)

    # ------------------------------------------------------------------
    # Initialisation helpers
    # ------------------------------------------------------------------

    def _init_pos_embed(self) -> None:
        """Initialise target position embeddings with truncated normal."""
        nn.init.trunc_normal_(
            self.target_pos_embed.weight, std=0.02, a=-0.04, b=0.04
        )

    # ------------------------------------------------------------------
    # Forward
    # ------------------------------------------------------------------

    def forward(
        self,
        context_emb: torch.Tensor,
        target_positions: torch.Tensor,
    ) -> torch.Tensor:
        """Predict target patch embeddings from context patches.

        Args:
            context_emb: Embeddings of the *visible* (context) patches,
                shape ``(B, C, D)`` where ``C`` is the number of context
                patches and ``D = embed_dim``.
            target_positions: Long tensor of shape ``(B, T)`` giving the
                spatial indices of the patches to predict
                (``0 <= idx < max_target_positions``).

        Returns:
            Predicted embeddings for the target patches, shape
            ``(B, T, embed_dim)``.
        """
        # Build query tokens from position embeddings  -------------------
        # target_positions: (B, T) -> target_queries: (B, T, D)
        target_queries = self.target_pos_embed(target_positions)

        # Project context  -----------------------------------------------
        memory = self.context_proj(context_emb)  # (B, C, D)

        # Transformer decoder  -------------------------------------------
        # ``tgt`` = target queries, ``memory`` = context (keys/values)
        decoded = self.transformer_decoder(
            tgt=target_queries,
            memory=memory,
        )  # (B, T, D)

        # Output head  ---------------------------------------------------
        predicted = self.output_head(self.output_norm(decoded))  # (B, T, D)
        return predicted
