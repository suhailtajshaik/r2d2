"""Visualisation helpers for VL-JEPA debugging and analysis.

All public functions return a :class:`matplotlib.figure.Figure` so callers can
either display them interactively (``fig.show()``) or save to disk
(``fig.savefig(...)``).
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence, Union

import numpy as np
import torch
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.figure import Figure


def _to_numpy_image(image: Union[torch.Tensor, np.ndarray]) -> np.ndarray:
    """Convert an image tensor of shape ``(C, H, W)`` to a NumPy HWC array.

    Values are clipped to [0, 1] so the result can be passed directly to
    ``imshow``.
    """
    if isinstance(image, torch.Tensor):
        image = image.detach().cpu().numpy()
    if image.ndim == 3 and image.shape[0] in (1, 3):
        image = np.transpose(image, (1, 2, 0))
    return np.clip(image, 0.0, 1.0)


# ------------------------------------------------------------------
# Masking visualisation
# ------------------------------------------------------------------


def visualize_masking(
    image: Union[torch.Tensor, np.ndarray],
    mask: Union[torch.Tensor, np.ndarray],
    patch_size: int = 16,
) -> Figure:
    """Overlay a patch-level binary mask on an image.

    Args:
        image: The original image as a ``(C, H, W)`` tensor or ``(H, W, C)``
            NumPy array.
        mask: A 1-D boolean / binary tensor (or array) of length equal to the
            number of patches.  A value of ``1`` (True) means the patch is
            **masked** (hidden from the encoder).
        patch_size: Spatial size of each square patch in pixels.

    Returns:
        A :class:`~matplotlib.figure.Figure` with three panels: original
        image, mask grid, and the masked image.
    """
    img_np = _to_numpy_image(image)
    h, w, _ = img_np.shape
    gh, gw = h // patch_size, w // patch_size

    if isinstance(mask, torch.Tensor):
        mask = mask.detach().cpu().numpy()
    mask_grid = mask.reshape(gh, gw).astype(np.float32)

    # Build a per-pixel mask for the overlay
    pixel_mask = np.kron(mask_grid, np.ones((patch_size, patch_size)))
    # Ensure spatial dimensions match (crop if image size not perfectly
    # divisible by patch_size)
    pixel_mask = pixel_mask[: h, : w]

    masked_image = img_np.copy()
    # Grey out masked patches
    masked_image[pixel_mask == 1] = 0.5

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    axes[0].imshow(img_np)
    axes[0].set_title("Original")
    axes[0].axis("off")

    axes[1].imshow(mask_grid, cmap="gray", vmin=0, vmax=1)
    axes[1].set_title("Mask (white = masked)")
    axes[1].axis("off")

    axes[2].imshow(masked_image)
    axes[2].set_title("Masked image")
    axes[2].axis("off")

    fig.tight_layout()
    return fig


# ------------------------------------------------------------------
# Attention visualisation
# ------------------------------------------------------------------


def visualize_attention(
    image: Union[torch.Tensor, np.ndarray],
    attention_weights: Union[torch.Tensor, np.ndarray],
) -> Figure:
    """Visualise multi-head attention weights as a heatmap overlay.

    Args:
        image: The original image as a ``(C, H, W)`` tensor or HWC array.
        attention_weights: Attention map of shape ``(num_heads, num_patches)``
            or ``(num_patches,)``.  Each value represents how strongly a patch
            is attended to (higher = more attention).

    Returns:
        A :class:`~matplotlib.figure.Figure`.  If the attention tensor has
        multiple heads the figure contains one panel per head plus a
        mean-attention panel; otherwise a single overlay is shown.
    """
    img_np = _to_numpy_image(image)
    h, w, _ = img_np.shape

    if isinstance(attention_weights, torch.Tensor):
        attention_weights = attention_weights.detach().cpu().numpy()

    # Ensure 2-D: (num_heads, num_patches)
    if attention_weights.ndim == 1:
        attention_weights = attention_weights[np.newaxis, :]

    num_heads = attention_weights.shape[0]
    num_patches = attention_weights.shape[1]

    # Infer the spatial grid size
    grid_side = int(np.sqrt(num_patches))
    if grid_side * grid_side != num_patches:
        # Non-square grid: fall back to closest rectangle
        grid_side_h = grid_side
        grid_side_w = num_patches // grid_side_h
    else:
        grid_side_h = grid_side_w = grid_side

    # Build figure -- one column per head + 1 for the mean if >1 head
    ncols = num_heads + (1 if num_heads > 1 else 0)
    fig, axes = plt.subplots(1, max(ncols, 1), figsize=(5 * ncols, 5))
    if ncols == 1:
        axes = [axes]  # type: ignore[list-item]
    else:
        axes = list(axes)

    def _overlay(ax: matplotlib.axes.Axes, attn_1d: np.ndarray, title: str) -> None:
        attn_map = attn_1d.reshape(grid_side_h, grid_side_w)
        # Upscale to image resolution via bilinear-like repetition
        from PIL import Image as _PILImage

        attn_pil = _PILImage.fromarray(attn_map.astype(np.float32), mode="F")
        attn_resized = np.array(attn_pil.resize((w, h), resample=_PILImage.BILINEAR))
        # Normalise to [0, 1]
        attn_min = attn_resized.min()
        attn_max = attn_resized.max()
        if attn_max - attn_min > 0:
            attn_resized = (attn_resized - attn_min) / (attn_max - attn_min)

        ax.imshow(img_np)
        ax.imshow(attn_resized, cmap="jet", alpha=0.5)
        ax.set_title(title)
        ax.axis("off")

    for idx in range(num_heads):
        _overlay(axes[idx], attention_weights[idx], f"Head {idx}")

    if num_heads > 1:
        mean_attn = attention_weights.mean(axis=0)
        _overlay(axes[-1], mean_attn, "Mean")

    fig.tight_layout()
    return fig


# ------------------------------------------------------------------
# Training curves
# ------------------------------------------------------------------


def plot_training_curves(
    history: Dict[str, List[float]],
) -> Figure:
    """Plot training metrics over epochs / steps.

    Args:
        history: A mapping from metric name (e.g. ``"loss"``,
            ``"learning_rate"``, ``"recall@1"``) to a list of scalar values,
            one per recorded step.

    Returns:
        A :class:`~matplotlib.figure.Figure` with one subplot per metric.
    """
    num_metrics = len(history)
    if num_metrics == 0:
        fig, ax = plt.subplots(1, 1, figsize=(6, 4))
        ax.text(0.5, 0.5, "No metrics to plot", ha="center", va="center")
        return fig

    ncols = min(num_metrics, 3)
    nrows = (num_metrics + ncols - 1) // ncols
    fig, axes = plt.subplots(
        nrows, ncols, figsize=(6 * ncols, 4 * nrows), squeeze=False
    )

    for idx, (name, values) in enumerate(history.items()):
        row, col = divmod(idx, ncols)
        ax = axes[row][col]
        steps = list(range(1, len(values) + 1))
        ax.plot(steps, values, linewidth=1.5)
        ax.set_xlabel("Step")
        ax.set_ylabel(name)
        ax.set_title(name)
        ax.grid(True, alpha=0.3)

    # Hide unused axes
    for idx in range(num_metrics, nrows * ncols):
        row, col = divmod(idx, ncols)
        axes[row][col].set_visible(False)

    fig.tight_layout()
    return fig
