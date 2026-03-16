"""JEPA Configuration — central dataclass for all hyperparameters.

The Configurator module from the VL-JEPA architecture mind map. Provides a
single source of truth for model, training, and inference settings.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


@dataclass
class JEPAConfig:
    """Complete hyperparameter configuration for VL-JEPA.

    Groups all tuneable knobs — vision backbone, predictor, language tower,
    EMA schedule, masking, loss selection, and selective decoding — into one
    frozen-friendly dataclass.
    """

    # Vision encoder
    img_size: int = 224
    patch_size: int = 16
    embed_dim: int = 384
    encoder_depth: int = 6
    encoder_heads: int = 6

    # Predictor
    predictor_depth: int = 3
    predictor_heads: int = 6

    # Language encoder
    language_model: str = "bert-base-uncased"
    language_embed_dim: int = 768

    # EMA / masking
    ema_momentum: float = 0.996
    mask_ratio: float = 0.5
    num_target_blocks: int = 4

    # Loss
    loss_type: Literal["infonce", "vicreg"] = "infonce"
    temperature: float = 0.07

    # Selective decoding
    selective_decoding: bool = False
    decode_threshold: float = 0.15

    @property
    def num_patches(self) -> int:
        """Total number of patches for the configured image / patch size."""
        return (self.img_size // self.patch_size) ** 2

    @property
    def num_patches_per_side(self) -> int:
        """Patches along one spatial dimension."""
        return self.img_size // self.patch_size
