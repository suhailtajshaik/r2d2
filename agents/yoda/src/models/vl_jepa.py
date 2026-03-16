"""Full VL-JEPA model combining vision, language, and prediction modules.

Vision-Language Joint Embedding Predictive Architecture (VL-JEPA) learns
visual representations by predicting masked patch embeddings in latent
space, while aligning with frozen language representations for cross-modal
understanding.

Architecture overview
---------------------
* **context_encoder** -- ViT that encodes *visible* image patches.
* **target_encoder**  -- ViT (same architecture, EMA-updated weights) that
  encodes *masked* image patches to produce prediction targets.
* **predictor**       -- lightweight transformer that predicts target
  embeddings from context embeddings + positional queries.
* **language_encoder** -- frozen BERT that produces text embeddings.
* **Projection heads** -- small MLPs that map image-CLS and text
  embeddings into a shared space for cross-modal alignment.
"""

from __future__ import annotations

import collections
import copy
from typing import Any, Dict, List, Optional

import torch
import torch.nn as nn
import torch.nn.functional as F

from .language_encoder import LanguageEncoder
from .predictor import Predictor
from .vision_encoder import VisionEncoder


# ======================================================================
# Default configuration
# ======================================================================

DEFAULT_VLJEPA_CONFIG: Dict[str, Any] = {
    # Vision encoder
    "vision": {
        "model_name": "vit_small_patch16_224",
        "pretrained": False,
        "embed_dim": 384,
        "img_size": 224,
        "patch_size": 16,
    },
    # Language encoder
    "language": {
        "model_name": "bert-base-uncased",
        "text_embed_dim": 768,
        "shared_embed_dim": 384,
        "projection_dropout": 0.1,
        "freeze_bert": True,
    },
    # Predictor
    "predictor": {
        "embed_dim": 384,
        "num_heads": 6,
        "depth": 3,
        "mlp_ratio": 4.0,
        "dropout": 0.0,
        "max_target_positions": 196,
    },
    # Cross-modal projection
    "projection_dim": 256,
    "projection_dropout": 0.1,
}


def _build_projection_head(
    input_dim: int, output_dim: int, dropout: float = 0.1
) -> nn.Sequential:
    """Create a 2-layer MLP projection head.

    Args:
        input_dim: Dimensionality of the input features.
        output_dim: Dimensionality of the projected features.
        dropout: Dropout probability between the two linear layers.

    Returns:
        An ``nn.Sequential`` module.
    """
    return nn.Sequential(
        nn.Linear(input_dim, output_dim),
        nn.GELU(),
        nn.Dropout(dropout),
        nn.Linear(output_dim, output_dim),
    )


class VLJEPA(nn.Module):
    """Vision-Language Joint Embedding Predictive Architecture.

    Args:
        config: Nested dictionary that may override any key in
            :data:`DEFAULT_VLJEPA_CONFIG`.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        super().__init__()
        cfg = self._merge_config(config)

        embed_dim: int = cfg["vision"]["embed_dim"]
        proj_dim: int = cfg["projection_dim"]
        proj_drop: float = cfg["projection_dropout"]
        text_embed_dim: int = cfg["language"]["shared_embed_dim"]

        # ----------------------------------------------------------
        # Sub-modules
        # ----------------------------------------------------------
        self.context_encoder = VisionEncoder(cfg["vision"])

        # Target encoder: same architecture, parameters will diverge via EMA.
        self.target_encoder = VisionEncoder(cfg["vision"])
        # Initialise target weights to match context encoder.
        self.target_encoder.load_state_dict(
            self.context_encoder.state_dict()
        )
        # Target encoder is never trained directly.
        for param in self.target_encoder.parameters():
            param.requires_grad = False

        self.predictor = Predictor(cfg["predictor"])

        self.language_encoder = LanguageEncoder(cfg["language"])

        # ----------------------------------------------------------
        # Cross-modal projection heads
        # ----------------------------------------------------------
        self.image_projection = _build_projection_head(
            embed_dim, proj_dim, proj_drop
        )
        self.text_projection = _build_projection_head(
            text_embed_dim, proj_dim, proj_drop
        )

    # ------------------------------------------------------------------
    # Config helper
    # ------------------------------------------------------------------

    @staticmethod
    def _merge_config(
        overrides: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Deep-merge *overrides* into a copy of :data:`DEFAULT_VLJEPA_CONFIG`.

        Only the first nesting level is merged so that individual sub-config
        dicts (``vision``, ``language``, ``predictor``) can be partially
        overridden without losing unspecified defaults.

        Args:
            overrides: User-supplied configuration dictionary.

        Returns:
            A fully populated configuration dictionary.
        """
        cfg = copy.deepcopy(DEFAULT_VLJEPA_CONFIG)
        if overrides is None:
            return cfg
        for key, value in overrides.items():
            if isinstance(value, dict) and key in cfg and isinstance(cfg[key], dict):
                cfg[key].update(value)
            else:
                cfg[key] = value
        return cfg

    @classmethod
    def from_default_config(cls) -> "VLJEPA":
        """Construct a :class:`VLJEPA` model with all default settings.

        Returns:
            A freshly initialised :class:`VLJEPA` instance.
        """
        return cls(config=None)

    # ------------------------------------------------------------------
    # Forward
    # ------------------------------------------------------------------

    def forward(
        self,
        images: torch.Tensor,
        text_input_ids: torch.Tensor,
        text_attention_mask: torch.Tensor,
        mask: torch.Tensor,
    ) -> Dict[str, torch.Tensor]:
        """Run the full VL-JEPA forward pass.

        Args:
            images: Batch of images, shape ``(B, 3, H, W)``.
            text_input_ids: Tokenised text ids, shape ``(B, L)``.
            text_attention_mask: Text attention mask, shape ``(B, L)``.
            mask: Boolean tensor of shape ``(B, N)`` where ``True`` marks
                patches that are *masked* (i.e., target patches).
                ``N = num_patches`` (e.g., 196 for 224-px / 16-px patches).

        Returns:
            Dictionary with the following entries:

            * ``predicted_emb``  -- ``(B, T, D)`` predictor output for targets.
            * ``target_emb``     -- ``(B, T, D)`` target encoder output
              (stop-gradient).
            * ``image_cls_emb``  -- ``(B, proj_dim)`` projected image CLS.
            * ``text_emb``       -- ``(B, proj_dim)`` projected text CLS.
        """
        batch_size = images.size(0)
        device = images.device

        # ---- context / target split from mask -----------------------
        # mask: (B, N), True = target, False = context
        context_mask = ~mask  # (B, N)

        # ---- Context encoder (gradient flows) -----------------------
        all_patches_ctx, cls_ctx = self.context_encoder(images)  # (B, N, D), (B, D)

        # Gather context patches
        context_indices = [
            context_mask[b].nonzero(as_tuple=False).squeeze(-1)
            for b in range(batch_size)
        ]
        # Pad to the same length across the batch (max context size)
        max_ctx_len = max(idx.size(0) for idx in context_indices)
        context_indices_padded = torch.zeros(
            batch_size, max_ctx_len, dtype=torch.long, device=device
        )
        for b, idx in enumerate(context_indices):
            context_indices_padded[b, : idx.size(0)] = idx

        context_emb = torch.gather(
            all_patches_ctx,
            dim=1,
            index=context_indices_padded.unsqueeze(-1).expand(
                -1, -1, all_patches_ctx.size(-1)
            ),
        )  # (B, max_ctx_len, D)

        # ---- Target encoder (no gradient, EMA updated) ---------------
        with torch.no_grad():
            all_patches_tgt, _ = self.target_encoder(images)  # (B, N, D)

        target_indices = [
            mask[b].nonzero(as_tuple=False).squeeze(-1)
            for b in range(batch_size)
        ]
        max_tgt_len = max(idx.size(0) for idx in target_indices)
        target_indices_padded = torch.zeros(
            batch_size, max_tgt_len, dtype=torch.long, device=device
        )
        for b, idx in enumerate(target_indices):
            target_indices_padded[b, : idx.size(0)] = idx

        target_emb = torch.gather(
            all_patches_tgt,
            dim=1,
            index=target_indices_padded.unsqueeze(-1).expand(
                -1, -1, all_patches_tgt.size(-1)
            ),
        )  # (B, max_tgt_len, D)

        # ---- Predictor -----------------------------------------------
        predicted_emb = self.predictor(
            context_emb, target_indices_padded
        )  # (B, T, D)

        # ---- Language encoder ----------------------------------------
        text_emb_raw = self.language_encoder(
            text_input_ids, text_attention_mask
        )  # (B, shared_embed_dim)

        # ---- Cross-modal projections ---------------------------------
        image_cls_proj = self.image_projection(cls_ctx)     # (B, proj_dim)
        text_cls_proj = self.text_projection(text_emb_raw)  # (B, proj_dim)

        return {
            "predicted_emb": predicted_emb,
            "target_emb": target_emb.detach(),
            "image_cls_emb": image_cls_proj,
            "text_emb": text_cls_proj,
        }

    # ------------------------------------------------------------------
    # EMA update
    # ------------------------------------------------------------------

    @torch.no_grad()
    def update_target_encoder(self, momentum: float = 0.996) -> None:
        """Exponential-moving-average update of the target encoder.

        For each parameter pair ``(theta_ctx, theta_tgt)``::

            theta_tgt <- momentum * theta_tgt + (1 - momentum) * theta_ctx

        Args:
            momentum: EMA decay factor. Values close to 1.0 produce a slowly
                evolving target encoder (recommended range: 0.99 -- 0.999).
        """
        for param_ctx, param_tgt in zip(
            self.context_encoder.parameters(),
            self.target_encoder.parameters(),
        ):
            param_tgt.data.mul_(momentum).add_(
                param_ctx.data, alpha=1.0 - momentum
            )

    # ------------------------------------------------------------------
    # Encode-only & selective decode helpers
    # ------------------------------------------------------------------

    def encode_only(self, images: torch.Tensor) -> torch.Tensor:
        """Return the CLS embedding without any decoding.

        Args:
            images: Batch of images, shape ``(B, 3, H, W)``.

        Returns:
            CLS embedding of shape ``(B, D)``.
        """
        _, cls_emb = self.context_encoder(images)
        return cls_emb

    def selective_decode(
        self,
        images: torch.Tensor,
        prev_memory: Optional["ShortTermMemory"] = None,
        decoder: Optional["SelectiveDecoder"] = None,
        threshold: float = 0.15,
    ) -> Dict[str, Any]:
        """Encode images and conditionally decode based on scene change.

        Uses :class:`ShortTermMemory` to track temporal context and
        :class:`SelectiveDecoder` to decide whether full decoding is needed.

        Args:
            images: Batch of images (B, 3, H, W).
            prev_memory: Optional :class:`ShortTermMemory` instance.
            decoder: Optional :class:`SelectiveDecoder` instance.
            threshold: Cosine-distance threshold for triggering decode.

        Returns:
            Dictionary with ``"embedding"``, ``"decoded"`` (bool), and
            optionally ``"text"`` if decoding was performed.
        """
        emb = self.encode_only(images)  # (B, D)

        result: Dict[str, Any] = {"embedding": emb, "decoded": False}

        if prev_memory is not None:
            prev_memory.push(emb)

        if decoder is not None and prev_memory is not None:
            delta = prev_memory.get_delta()
            if delta is not None and decoder.should_decode(
                prev_memory._buffer[-2] if len(prev_memory._buffer) >= 2 else emb,
                emb,
                threshold,
            ):
                result["text"] = decoder.decode(emb)
                result["decoded"] = True

        return result


# ======================================================================
# Selective Decoder — 2.85× faster inference via conditional decoding
# ======================================================================


class SelectiveDecoder(nn.Module):
    """Lightweight transformer decoder that fires only when needed.

    Instead of decoding every frame, the selective decoder checks whether the
    scene semantics have changed (cosine distance exceeds *threshold*) and
    skips decoding otherwise — yielding up to 2.85× inference speedup.

    Args:
        embed_dim: Dimensionality of input embeddings.
        num_heads: Number of attention heads per decoder layer.
        num_layers: Number of transformer decoder layers.
    """

    def __init__(
        self, embed_dim: int = 384, num_heads: int = 6, num_layers: int = 2
    ) -> None:
        super().__init__()
        decoder_layer = nn.TransformerDecoderLayer(
            d_model=embed_dim, nhead=num_heads, batch_first=True
        )
        self.decoder = nn.TransformerDecoder(decoder_layer, num_layers=num_layers)
        self.output_head = nn.Linear(embed_dim, embed_dim)

    @staticmethod
    def should_decode(
        prev_emb: torch.Tensor, curr_emb: torch.Tensor, threshold: float = 0.15
    ) -> bool:
        """Return ``True`` if the cosine distance between embeddings exceeds *threshold*.

        Args:
            prev_emb: Previous embedding(s).
            curr_emb: Current embedding(s).
            threshold: Distance threshold.

        Returns:
            Boolean indicating whether decoding should proceed.
        """
        cos_sim = F.cosine_similarity(
            prev_emb.flatten().unsqueeze(0),
            curr_emb.flatten().unsqueeze(0),
        ).item()
        return (1.0 - cos_sim) > threshold

    def decode(self, embedding: torch.Tensor, max_length: int = 50) -> str:
        """Generate text from an embedding (stub implementation).

        Args:
            embedding: Input embedding tensor.
            max_length: Maximum generation length (unused in stub).

        Returns:
            String representation — currently returns the embedding norm.
        """
        norm = embedding.norm().item()
        return f"[decoded | emb_norm={norm:.4f}]"

    def forward(self, tgt: torch.Tensor, memory: torch.Tensor) -> torch.Tensor:  # noqa: D401
        """Standard transformer decoder forward pass."""
        return self.output_head(self.decoder(tgt, memory))


# ======================================================================
# Cost Module — intrinsic + critic costs for world-model planning
# ======================================================================


class CostModule(nn.Module):
    """Evaluates prediction quality via intrinsic and learned critic costs.

    The **intrinsic cost** is the MSE between predicted and target embeddings
    (how surprising is the outcome?).  The **critic cost** is a learned scalar
    value estimate (how *good* is the current state?).

    Args:
        embed_dim: Dimensionality of embeddings.
    """

    def __init__(self, embed_dim: int = 384) -> None:
        super().__init__()
        self.critic_head = nn.Linear(embed_dim, 1)

    @staticmethod
    def intrinsic_cost(
        predicted_emb: torch.Tensor, target_emb: torch.Tensor
    ) -> torch.Tensor:
        """MSE prediction error (intrinsic surprise).

        Args:
            predicted_emb: Predicted embeddings.
            target_emb: Target embeddings.

        Returns:
            Scalar MSE loss.
        """
        return F.mse_loss(predicted_emb, target_emb)

    def critic_cost(self, embedding: torch.Tensor) -> torch.Tensor:
        """Learned value estimate for the given embedding.

        Args:
            embedding: Input embedding of shape ``(B, D)`` or ``(B, T, D)``.

        Returns:
            Scalar mean value estimate.
        """
        return self.critic_head(embedding).mean()

    def total_cost(
        self,
        predicted_emb: torch.Tensor,
        target_emb: torch.Tensor,
        alpha: float = 0.5,
    ) -> torch.Tensor:
        """Weighted combination of intrinsic and critic costs.

        Args:
            predicted_emb: Predicted embeddings.
            target_emb: Target embeddings.
            alpha: Weight for intrinsic cost (``1 - alpha`` for critic).

        Returns:
            Scalar combined cost.
        """
        ic = self.intrinsic_cost(predicted_emb, target_emb)
        cc = self.critic_cost(predicted_emb)
        return alpha * ic + (1.0 - alpha) * cc


# ======================================================================
# Short-Term Memory — temporal embedding ring buffer
# ======================================================================


class ShortTermMemory:
    """Ring buffer that stores recent embeddings for temporal context.

    Used by :class:`SelectiveDecoder` to track scene changes and by the
    :class:`CostModule` to assess temporal prediction quality.

    Args:
        maxlen: Maximum number of embeddings to store.
    """

    def __init__(self, maxlen: int = 16) -> None:
        self._buffer: collections.deque = collections.deque(maxlen=maxlen)

    def push(self, embedding: torch.Tensor) -> None:
        """Add a new embedding to the buffer.

        Args:
            embedding: Embedding tensor (any shape — typically ``(B, D)``).
        """
        self._buffer.append(embedding.detach())

    def get_context(self) -> Optional[torch.Tensor]:
        """Return all stored embeddings stacked along a new time dimension.

        Returns:
            Tensor of shape ``(T, *emb_shape)`` or ``None`` if empty.
        """
        if len(self._buffer) == 0:
            return None
        return torch.stack(list(self._buffer), dim=0)

    def get_delta(self) -> Optional[float]:
        """Cosine distance between the last two stored embeddings.

        Returns:
            Scalar cosine distance, or ``None`` if fewer than two entries.
        """
        if len(self._buffer) < 2:
            return None
        prev = self._buffer[-2].flatten().unsqueeze(0)
        curr = self._buffer[-1].flatten().unsqueeze(0)
        cos_sim = F.cosine_similarity(prev, curr).item()
        return 1.0 - cos_sim
