"""Language encoder module wrapping a frozen BERT model.

Projects BERT CLS embeddings into a shared embedding space so that
text representations are aligned with vision patch embeddings in the
VL-JEPA framework.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

import torch
import torch.nn as nn
from transformers import BertModel


DEFAULT_LANGUAGE_CONFIG: Dict[str, Any] = {
    "model_name": "bert-base-uncased",
    "text_embed_dim": 768,       # BERT hidden size
    "shared_embed_dim": 384,     # target projection dimension
    "projection_dropout": 0.1,
    "freeze_bert": True,
}


class LanguageEncoder(nn.Module):
    """BERT-based language encoder with a learnable projection head.

    By default the BERT backbone is frozen (``requires_grad=False``) so that
    only the projection head is trained.  This keeps training efficient and
    prevents catastrophic forgetting of linguistic knowledge.

    Args:
        config: Dictionary whose keys override :data:`DEFAULT_LANGUAGE_CONFIG`.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        super().__init__()
        cfg = {**DEFAULT_LANGUAGE_CONFIG, **(config or {})}

        self.text_embed_dim: int = cfg["text_embed_dim"]
        self.shared_embed_dim: int = cfg["shared_embed_dim"]

        # ----------------------------------------------------------
        # BERT backbone
        # ----------------------------------------------------------
        self.bert: BertModel = BertModel.from_pretrained(cfg["model_name"])

        if cfg["freeze_bert"]:
            self._freeze_bert()

        # ----------------------------------------------------------
        # Projection head: linear -> GELU -> dropout -> linear
        # ----------------------------------------------------------
        self.projection = nn.Sequential(
            nn.Linear(self.text_embed_dim, self.shared_embed_dim),
            nn.GELU(),
            nn.Dropout(cfg["projection_dropout"]),
            nn.Linear(self.shared_embed_dim, self.shared_embed_dim),
        )

    # ------------------------------------------------------------------
    # Freeze / unfreeze helpers
    # ------------------------------------------------------------------

    def _freeze_bert(self) -> None:
        """Disable gradients for every parameter in the BERT backbone."""
        for param in self.bert.parameters():
            param.requires_grad = False

    def unfreeze_bert(self) -> None:
        """Re-enable gradients for every parameter in the BERT backbone.

        Useful if you want to fine-tune BERT after an initial frozen phase.
        """
        for param in self.bert.parameters():
            param.requires_grad = True

    # ------------------------------------------------------------------
    # Forward
    # ------------------------------------------------------------------

    def forward(
        self,
        input_ids: torch.Tensor,
        attention_mask: torch.Tensor,
    ) -> torch.Tensor:
        """Encode a batch of tokenised text and project to the shared space.

        Args:
            input_ids: Integer token ids of shape ``(B, L)``.
            attention_mask: Binary mask of shape ``(B, L)`` (``1`` for real
                tokens, ``0`` for padding).

        Returns:
            Tensor of shape ``(B, shared_embed_dim)`` -- the projected CLS
            embedding for each sentence in the batch.
        """
        bert_output = self.bert(
            input_ids=input_ids,
            attention_mask=attention_mask,
            return_dict=True,
        )

        # CLS token is the first token in the last hidden state.
        cls_hidden: torch.Tensor = bert_output.last_hidden_state[:, 0, :]  # (B, 768)

        text_embedding: torch.Tensor = self.projection(cls_hidden)  # (B, shared_embed_dim)
        return text_embedding
