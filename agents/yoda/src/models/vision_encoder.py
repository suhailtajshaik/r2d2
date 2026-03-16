"""Vision encoder module using a ViT backbone from timm.

Provides patch-level and CLS-level embeddings for image inputs,
suitable for use in a JEPA-style architecture where specific patch
representations are masked and predicted.
"""

from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

import timm
import torch
import torch.nn as nn


DEFAULT_VISION_CONFIG: Dict[str, Any] = {
    "model_name": "vit_small_patch16_224",
    "pretrained": False,
    "embed_dim": 384,
    "img_size": 224,
    "patch_size": 16,
}


class VisionEncoder(nn.Module):
    """ViT-based vision encoder that returns both patch and CLS embeddings.

    Wraps a ``timm`` ViT model so that the forward pass exposes the full
    sequence of patch embeddings in addition to the CLS token embedding.

    Args:
        config: Dictionary with keys such as ``model_name``, ``pretrained``,
            ``embed_dim``, ``img_size``, and ``patch_size``.  Missing keys
            fall back to :data:`DEFAULT_VISION_CONFIG`.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        super().__init__()
        cfg = {**DEFAULT_VISION_CONFIG, **(config or {})}
        self.embed_dim: int = cfg["embed_dim"]
        self.patch_size: int = cfg["patch_size"]
        self.img_size: int = cfg["img_size"]

        # Number of patches along one spatial dimension and total count.
        self.grid_size: int = self.img_size // self.patch_size
        self.num_patches: int = self.grid_size * self.grid_size

        # Create the ViT backbone.  ``num_classes=0`` removes the
        # classification head so that ``forward_features`` returns the raw
        # token sequence.
        self.backbone: nn.Module = timm.create_model(
            cfg["model_name"],
            pretrained=cfg["pretrained"],
            num_classes=0,
            img_size=self.img_size,
        )

    # ------------------------------------------------------------------
    # Forward
    # ------------------------------------------------------------------

    def forward(
        self, images: torch.Tensor
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """Encode images and return patch + CLS embeddings.

        Args:
            images: Batch of images with shape ``(B, 3, H, W)``.

        Returns:
            A tuple ``(patch_embeddings, cls_embedding)`` where
            *patch_embeddings* has shape ``(B, num_patches, embed_dim)`` and
            *cls_embedding* has shape ``(B, embed_dim)``.
        """
        # ``forward_features`` returns ``(B, 1 + num_patches, embed_dim)``
        # where position 0 is the CLS token.
        tokens: torch.Tensor = self.backbone.forward_features(images)

        cls_embedding = tokens[:, 0, :]           # (B, D)
        patch_embeddings = tokens[:, 1:, :]       # (B, N, D)

        return patch_embeddings, cls_embedding

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def get_patch_embeddings_at(
        self, images: torch.Tensor, patch_indices: torch.Tensor
    ) -> torch.Tensor:
        """Return embeddings for a subset of patch positions.

        Args:
            images: Batch of images with shape ``(B, 3, H, W)``.
            patch_indices: Long tensor of shape ``(B, K)`` giving the
                indices of the patches to extract (``0 <= idx < num_patches``).

        Returns:
            Tensor of shape ``(B, K, embed_dim)`` containing the selected
            patch embeddings.
        """
        patch_embeddings, _ = self.forward(images)  # (B, N, D)
        batch_size = patch_embeddings.size(0)

        # Expand indices for gather: (B, K) -> (B, K, D)
        indices_expanded = patch_indices.unsqueeze(-1).expand(
            batch_size, patch_indices.size(1), self.embed_dim
        )
        selected = torch.gather(patch_embeddings, dim=1, index=indices_expanded)
        return selected
