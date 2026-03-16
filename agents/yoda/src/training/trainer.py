"""VL-JEPA training loop.

Provides the :class:`Trainer` class that orchestrates single-node training of
a VL-JEPA model, including:

* AdamW optimiser with cosine-annealing LR schedule
* Mixed-precision (``torch.cuda.amp``) when a CUDA device is available
* Exponential-moving-average (EMA) updates of the target encoder
* Periodic checkpoint saving
* Per-step and per-epoch loss logging via *tqdm*
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

import torch
import torch.nn as nn
from torch.optim import AdamW
from torch.optim.lr_scheduler import CosineAnnealingLR
from torch.utils.data import DataLoader

try:
    from tqdm import tqdm
except ImportError:  # graceful fallback
    tqdm = None  # type: ignore[assignment]

from src.training.losses import JEPALoss
from src.training.masking import BlockMasking


# --------------------------------------------------------------------------- #
# Default training configuration
# --------------------------------------------------------------------------- #

@dataclass
class TrainerConfig:
    """Training hyper-parameters with sensible JEPA defaults.

    Any value can be overridden by passing a plain ``dict`` to
    :class:`Trainer` instead of a ``TrainerConfig`` instance.
    """

    lr: float = 1.5e-4
    weight_decay: float = 0.05
    betas: tuple[float, float] = (0.9, 0.999)
    num_epochs: int = 100
    ema_momentum: float = 0.996
    alignment_weight: float = 0.5
    checkpoint_every: int = 10
    checkpoint_dir: str = "checkpoints"
    num_target_blocks: int = 4
    target_coverage: float = 0.5
    num_patches_h: int = 14
    num_patches_w: int = 14
    device: str = "cuda" if torch.cuda.is_available() else "cpu"
    use_amp: bool = True


# --------------------------------------------------------------------------- #
# Trainer
# --------------------------------------------------------------------------- #

class Trainer:
    """End-to-end training driver for VL-JEPA.

    Args:
        model: A ``VLJEPA`` model instance that exposes ``forward`` and
            ``update_target_encoder``.
        train_loader: A :class:`~torch.utils.data.DataLoader` yielding batches
            of ``(images, text_input_ids, text_attention_mask)``.
        config: A :class:`TrainerConfig`, a plain ``dict`` of overrides, or
            ``None`` (in which case defaults are used).

    Example::

        trainer = Trainer(model, train_loader, {"num_epochs": 50, "lr": 3e-4})
        history = trainer.train()
    """

    def __init__(
        self,
        model: nn.Module,
        train_loader: DataLoader,
        config: Optional[TrainerConfig | dict[str, Any]] = None,
    ) -> None:
        # --- config ---
        if config is None:
            self.config = TrainerConfig()
        elif isinstance(config, dict):
            self.config = TrainerConfig(**config)
        else:
            self.config = config

        self.device = torch.device(self.config.device)

        # --- model ---
        self.model = model.to(self.device)
        self.train_loader = train_loader

        # --- loss / masking ---
        self.criterion = JEPALoss()
        self.masker = BlockMasking()

        # --- optimiser & scheduler ---
        self.optimizer = AdamW(
            self.model.parameters(),
            lr=self.config.lr,
            weight_decay=self.config.weight_decay,
            betas=self.config.betas,
        )
        total_steps = self.config.num_epochs * len(self.train_loader)
        self.scheduler = CosineAnnealingLR(
            self.optimizer, T_max=max(total_steps, 1)
        )

        # --- mixed precision ---
        self._use_amp = self.config.use_amp and self.device.type == "cuda"
        self.scaler = torch.amp.GradScaler("cuda", enabled=self._use_amp)

        # --- checkpoint dir ---
        self.checkpoint_dir = Path(self.config.checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)

        # --- bookkeeping ---
        self.global_step: int = 0

    # ------------------------------------------------------------------ #
    # Masking helper
    # ------------------------------------------------------------------ #

    def _generate_mask(self) -> dict[str, torch.Tensor]:
        """Create a block mask and move tensors to the training device."""
        mask = self.masker.generate_mask(
            num_patches_h=self.config.num_patches_h,
            num_patches_w=self.config.num_patches_w,
            num_targets=self.config.num_target_blocks,
            target_coverage=self.config.target_coverage,
        )
        return {k: v.to(self.device) for k, v in mask.items()}

    # ------------------------------------------------------------------ #
    # Single epoch
    # ------------------------------------------------------------------ #

    def train_epoch(self) -> dict[str, float]:
        """Run one full pass over the training data.

        Returns:
            Dictionary with keys ``"avg_total_loss"``, ``"avg_jepa_loss"``,
            and ``"avg_alignment_loss"`` averaged over all batches.
        """
        self.model.train()

        running: dict[str, float] = {
            "total_loss": 0.0,
            "jepa_loss": 0.0,
            "alignment_loss": 0.0,
        }
        num_batches = 0

        loader_iter: Any = self.train_loader
        if tqdm is not None:
            loader_iter = tqdm(
                self.train_loader,
                desc="  batch",
                leave=False,
                dynamic_ncols=True,
            )

        for batch in loader_iter:
            images, text_input_ids, text_attention_mask = (
                batch[0].to(self.device),
                batch[1].to(self.device),
                batch[2].to(self.device),
            )

            mask = self._generate_mask()

            # ---- forward ----
            self.optimizer.zero_grad(set_to_none=True)

            with torch.amp.autocast(
                device_type=self.device.type, enabled=self._use_amp
            ):
                outputs = self.model(
                    images=images,
                    text_input_ids=text_input_ids,
                    text_attention_mask=text_attention_mask,
                    mask=mask,
                )

                losses = self.criterion(
                    predicted_emb=outputs["predicted_embeddings"],
                    target_emb=outputs["target_embeddings"],
                    image_cls_emb=outputs["image_cls_embedding"],
                    text_emb=outputs["text_embedding"],
                    alignment_weight=self.config.alignment_weight,
                )

            total_loss = losses["total_loss"]

            # ---- backward ----
            self.scaler.scale(total_loss).backward()
            self.scaler.step(self.optimizer)
            self.scaler.update()
            self.scheduler.step()

            # ---- EMA target encoder update ----
            self.model.update_target_encoder(momentum=self.config.ema_momentum)

            # ---- logging ----
            running["total_loss"] += total_loss.item()
            running["jepa_loss"] += losses["jepa_loss"].item()
            running["alignment_loss"] += losses["alignment_loss"].item()
            num_batches += 1
            self.global_step += 1

            if tqdm is not None and isinstance(loader_iter, tqdm):
                loader_iter.set_postfix(
                    loss=f"{total_loss.item():.4f}",
                    jepa=f"{losses['jepa_loss'].item():.4f}",
                    align=f"{losses['alignment_loss'].item():.4f}",
                )

        avg = {
            f"avg_{k}": v / max(num_batches, 1)
            for k, v in running.items()
        }
        return avg

    # ------------------------------------------------------------------ #
    # Checkpointing
    # ------------------------------------------------------------------ #

    def _save_checkpoint(self, epoch: int) -> Path:
        """Persist model, optimiser, and scheduler state to disk.

        Args:
            epoch: Current (0-indexed) epoch number.

        Returns:
            Path to the saved checkpoint file.
        """
        path = self.checkpoint_dir / f"checkpoint_epoch_{epoch:04d}.pt"
        torch.save(
            {
                "epoch": epoch,
                "global_step": self.global_step,
                "model_state_dict": self.model.state_dict(),
                "optimizer_state_dict": self.optimizer.state_dict(),
                "scheduler_state_dict": self.scheduler.state_dict(),
                "scaler_state_dict": self.scaler.state_dict(),
                "config": self.config,
            },
            path,
        )
        return path

    # ------------------------------------------------------------------ #
    # Full training loop
    # ------------------------------------------------------------------ #

    def train(self, num_epochs: Optional[int] = None) -> list[dict[str, float]]:
        """Run the full training loop.

        Args:
            num_epochs: Number of epochs.  Falls back to
                ``self.config.num_epochs`` when ``None``.

        Returns:
            List of per-epoch metric dictionaries (same schema as
            :meth:`train_epoch`).
        """
        num_epochs = num_epochs if num_epochs is not None else self.config.num_epochs
        history: list[dict[str, float]] = []

        epoch_iter = range(num_epochs)
        if tqdm is not None:
            epoch_iter = tqdm(epoch_iter, desc="epoch", dynamic_ncols=True)

        for epoch in epoch_iter:
            metrics = self.train_epoch()
            metrics["epoch"] = float(epoch)
            history.append(metrics)

            # Console summary
            msg = (
                f"Epoch {epoch}/{num_epochs - 1} | "
                f"total={metrics['avg_total_loss']:.4f}  "
                f"jepa={metrics['avg_jepa_loss']:.4f}  "
                f"align={metrics['avg_alignment_loss']:.4f}"
            )
            if tqdm is not None and hasattr(epoch_iter, "set_postfix_str"):
                epoch_iter.set_postfix_str(msg)  # type: ignore[union-attr]
            else:
                print(msg)

            # Checkpoint
            if (epoch + 1) % self.config.checkpoint_every == 0 or epoch == num_epochs - 1:
                ckpt_path = self._save_checkpoint(epoch)
                print(f"  -> checkpoint saved to {ckpt_path}")

        return history
