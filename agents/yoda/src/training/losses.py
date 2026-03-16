"""Loss functions for VL-JEPA training.

Provides the combined JEPA reconstruction loss and vision-language alignment loss
used to train the VL-JEPA model.  Includes VICReg as an alternative to InfoNCE.
"""

from __future__ import annotations

from typing import Dict, Literal, Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F


# ======================================================================
# VICReg loss (standalone function)
# ======================================================================


def vicreg_loss(
    z1: torch.Tensor,
    z2: torch.Tensor,
    sim_coef: float = 25.0,
    var_coef: float = 25.0,
    cov_coef: float = 1.0,
) -> Tuple[torch.Tensor, Dict[str, torch.Tensor]]:
    """Variance-Invariance-Covariance Regularization loss.

    Args:
        z1: First set of embeddings, shape ``(B, D)``.
        z2: Second set of embeddings, shape ``(B, D)``.
        sim_coef: Weight for invariance (MSE) term.
        var_coef: Weight for variance term.
        cov_coef: Weight for covariance term.

    Returns:
        Tuple of (total_loss, component_dict) where component_dict contains
        ``"sim_loss"``, ``"var_loss"``, and ``"cov_loss"``.
    """
    # --- Invariance (similarity) ---
    sim_loss = F.mse_loss(z1, z2)

    # --- Variance ---
    std_z1 = torch.sqrt(z1.var(dim=0) + 1e-4)
    std_z2 = torch.sqrt(z2.var(dim=0) + 1e-4)
    var_loss = torch.mean(F.relu(1.0 - std_z1)) + torch.mean(F.relu(1.0 - std_z2))

    # --- Covariance ---
    batch_size, dim = z1.shape
    z1_centered = z1 - z1.mean(dim=0)
    z2_centered = z2 - z2.mean(dim=0)
    cov_z1 = (z1_centered.T @ z1_centered) / max(batch_size - 1, 1)
    cov_z2 = (z2_centered.T @ z2_centered) / max(batch_size - 1, 1)
    # Penalise off-diagonal elements
    cov_loss = (
        cov_z1.fill_diagonal_(0).pow(2).sum() / dim
        + cov_z2.fill_diagonal_(0).pow(2).sum() / dim
    )

    total = sim_coef * sim_loss + var_coef * var_loss + cov_coef * cov_loss
    return total, {
        "sim_loss": sim_loss,
        "var_loss": var_loss,
        "cov_loss": cov_loss,
    }


class JEPALoss(nn.Module):
    """Combined loss for Vision-Language JEPA training.

    Computes two losses:
    1. **JEPA loss**: Mean squared error between predicted patch embeddings and
       stop-gradient target embeddings (self-supervised reconstruction in latent space).
    2. **Alignment loss**: InfoNCE / NT-Xent contrastive loss between image CLS
       tokens and text embeddings, encouraging cross-modal alignment.

    Args:
        temperature: Softmax temperature for the contrastive alignment loss.
            Lower values sharpen the distribution. Default ``0.07``.
    """

    def __init__(self, temperature: float = 0.07) -> None:
        super().__init__()
        self.temperature = temperature
        self.mse = nn.MSELoss()

    # ------------------------------------------------------------------
    # Component losses
    # ------------------------------------------------------------------

    def jepa_loss(
        self,
        predicted_embeddings: torch.Tensor,
        target_embeddings: torch.Tensor,
    ) -> torch.Tensor:
        """Compute the JEPA reconstruction loss.

        The target embeddings are detached so that gradients only flow through
        the predictor / context encoder, not the target encoder (which is
        updated via EMA).

        Args:
            predicted_embeddings: Predictor output for masked target patches.
                Shape ``(B, N_target, D)`` or ``(B, D)``.
            target_embeddings: Target encoder output for the same patches.
                Shape must match *predicted_embeddings*.

        Returns:
            Scalar MSE loss tensor.
        """
        return self.mse(predicted_embeddings, target_embeddings.detach())

    def alignment_loss(
        self,
        image_cls_emb: torch.Tensor,
        text_emb: torch.Tensor,
    ) -> torch.Tensor:
        """Compute the InfoNCE / NT-Xent alignment loss.

        Both inputs are L2-normalised, then the symmetric cross-entropy over
        cosine similarities (scaled by ``1 / temperature``) is computed.

        Args:
            image_cls_emb: Image CLS embeddings, shape ``(B, D)``.
            text_emb: Text embeddings, shape ``(B, D)``.

        Returns:
            Scalar contrastive loss tensor.
        """
        # L2 normalise along the feature dimension
        image_norm = F.normalize(image_cls_emb, dim=-1)
        text_norm = F.normalize(text_emb, dim=-1)

        # Cosine similarity matrix scaled by temperature  (B, B)
        logits = image_norm @ text_norm.T / self.temperature

        batch_size = logits.size(0)
        labels = torch.arange(batch_size, device=logits.device)

        # Symmetric InfoNCE: image->text + text->image
        loss_i2t = F.cross_entropy(logits, labels)
        loss_t2i = F.cross_entropy(logits.T, labels)
        return (loss_i2t + loss_t2i) / 2.0

    # ------------------------------------------------------------------
    # Forward
    # ------------------------------------------------------------------

    def forward(
        self,
        predicted_emb: torch.Tensor,
        target_emb: torch.Tensor,
        image_cls_emb: torch.Tensor,
        text_emb: torch.Tensor,
        alignment_weight: float = 0.5,
    ) -> dict[str, torch.Tensor]:
        """Compute the combined VL-JEPA loss.

        Args:
            predicted_emb: Predictor output for masked patches.
            target_emb: Target encoder output for the same patches.
            image_cls_emb: Image CLS token embeddings ``(B, D)``.
            text_emb: Text embeddings ``(B, D)``.
            alignment_weight: Scalar weight for the alignment loss.  The JEPA
                loss is weighted by ``1 - alignment_weight``.  Default ``0.5``.

        Returns:
            Dictionary with keys ``"total_loss"``, ``"jepa_loss"``, and
            ``"alignment_loss"`` — each a scalar :class:`torch.Tensor`.
        """
        l_jepa = self.jepa_loss(predicted_emb, target_emb)
        l_align = self.alignment_loss(image_cls_emb, text_emb)

        total = (1.0 - alignment_weight) * l_jepa + alignment_weight * l_align

        return {
            "total_loss": total,
            "jepa_loss": l_jepa,
            "alignment_loss": l_align,
        }


# ======================================================================
# Combined loss dispatcher
# ======================================================================


def combined_loss(
    predicted_emb: torch.Tensor,
    target_emb: torch.Tensor,
    image_cls_emb: torch.Tensor,
    text_emb: torch.Tensor,
    loss_type: Literal["infonce", "vicreg"] = "infonce",
    alignment_weight: float = 0.5,
    temperature: float = 0.07,
) -> Dict[str, torch.Tensor]:
    """Compute VL-JEPA loss using the specified alignment strategy.

    Args:
        predicted_emb: Predictor output for masked patches.
        target_emb: Target encoder output (will be detached).
        image_cls_emb: Image CLS embeddings ``(B, D)``.
        text_emb: Text embeddings ``(B, D)``.
        loss_type: ``"infonce"`` for InfoNCE/NT-Xent or ``"vicreg"`` for VICReg.
        alignment_weight: Weight for the alignment loss.
        temperature: Temperature for InfoNCE (ignored for VICReg).

    Returns:
        Dictionary with ``"total_loss"`` and component losses.
    """
    # JEPA reconstruction loss (always MSE)
    jepa = F.mse_loss(predicted_emb, target_emb.detach())

    if loss_type == "vicreg":
        align_total, align_components = vicreg_loss(image_cls_emb, text_emb)
        total = (1.0 - alignment_weight) * jepa + alignment_weight * align_total
        return {
            "total_loss": total,
            "jepa_loss": jepa,
            "alignment_loss": align_total,
            **{f"vicreg_{k}": v for k, v in align_components.items()},
        }
    else:
        # Default: InfoNCE
        loss_fn = JEPALoss(temperature=temperature)
        return loss_fn(predicted_emb, target_emb, image_cls_emb, text_emb, alignment_weight)
