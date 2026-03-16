"""Block masking strategy for VL-JEPA.

Implements the rectangular block masking used in JEPA-style self-supervised
learning: several randomly-placed rectangular regions are designated as
*targets* (to be predicted), and the remaining patches form the *context*
(visible to the encoder).

Includes both the original :class:`BlockMasking` and the improved
:class:`MultiBlockMasking` with non-overlapping blocks and per-block coverage
caps.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Optional, Set, Tuple

import torch


class BlockMasking:
    """Generates rectangular block masks for JEPA-style pre-training.

    Target blocks are randomly placed rectangular regions whose union covers
    approximately ``target_coverage`` of the full patch grid.  The context
    consists of every patch index *not* covered by any target block.

    Args:
        min_aspect: Minimum aspect ratio (height / width) of each block.
        max_aspect: Maximum aspect ratio (height / width) of each block.
        seed: Optional RNG seed for reproducibility.

    Example::

        masker = BlockMasking()
        mask = masker.generate_mask(14, 14, num_targets=4, target_coverage=0.5)
        context_idx = mask["context_indices"]   # 1-D tensor of patch indices
        target_idx  = mask["target_indices"]    # 1-D tensor of patch indices
    """

    def __init__(
        self,
        min_aspect: float = 0.75,
        max_aspect: float = 1.5,
        seed: Optional[int] = None,
    ) -> None:
        self.min_aspect = min_aspect
        self.max_aspect = max_aspect
        self._rng = random.Random(seed)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _sample_block(
        self,
        num_patches_h: int,
        num_patches_w: int,
        target_area: int,
    ) -> tuple[int, int, int, int]:
        """Sample a single rectangular block (top, left, height, width).

        The block is constrained to fit within the ``(num_patches_h, num_patches_w)``
        grid and to cover approximately *target_area* patches.

        Args:
            num_patches_h: Height of the patch grid.
            num_patches_w: Width of the patch grid.
            target_area: Desired area (in patches) for this block.

        Returns:
            Tuple ``(top, left, block_h, block_w)``.
        """
        target_area = max(1, target_area)

        # Sample aspect ratio and derive height / width
        log_aspect = self._rng.uniform(
            math.log(self.min_aspect), math.log(self.max_aspect)
        )
        aspect = math.exp(log_aspect)

        block_h = int(round(math.sqrt(target_area * aspect)))
        block_w = int(round(math.sqrt(target_area / aspect)))

        # Clamp to grid dimensions (at least 1)
        block_h = max(1, min(block_h, num_patches_h))
        block_w = max(1, min(block_w, num_patches_w))

        top = self._rng.randint(0, num_patches_h - block_h)
        left = self._rng.randint(0, num_patches_w - block_w)

        return top, left, block_h, block_w

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate_mask(
        self,
        num_patches_h: int,
        num_patches_w: int,
        num_targets: int = 4,
        target_coverage: float = 0.5,
    ) -> dict[str, torch.Tensor]:
        """Generate context and target patch indices via block masking.

        Places *num_targets* random rectangular blocks whose combined area
        targets approximately ``target_coverage`` of the full patch grid.
        Because blocks may overlap the actual coverage can be slightly less
        than the requested value.

        Args:
            num_patches_h: Number of patches along the height dimension.
            num_patches_w: Number of patches along the width dimension.
            num_targets: Number of rectangular target blocks to place.
            target_coverage: Fraction of patches that should be masked
                (i.e. designated as targets).  Default ``0.5``.

        Returns:
            Dictionary with two keys:

            - ``"context_indices"``: 1-D :class:`torch.LongTensor` of flattened
              indices for the visible (context) patches, sorted ascending.
            - ``"target_indices"``: 1-D :class:`torch.LongTensor` of flattened
              indices for the masked (target) patches, sorted ascending.
        """
        total_patches = num_patches_h * num_patches_w
        target_total_area = int(round(total_patches * target_coverage))
        per_block_area = max(1, target_total_area // num_targets)

        # Boolean mask: True = target (masked)
        mask = torch.zeros(num_patches_h, num_patches_w, dtype=torch.bool)

        for _ in range(num_targets):
            top, left, bh, bw = self._sample_block(
                num_patches_h, num_patches_w, per_block_area
            )
            mask[top : top + bh, left : left + bw] = True

        flat_mask = mask.reshape(-1)  # (H * W,)

        target_indices = torch.nonzero(flat_mask, as_tuple=False).squeeze(-1)
        context_indices = torch.nonzero(~flat_mask, as_tuple=False).squeeze(-1)

        # Guarantee we always have at least one context and one target patch.
        # In degenerate cases (e.g. tiny grids) we fall back to a simple split.
        if target_indices.numel() == 0 or context_indices.numel() == 0:
            all_indices = torch.randperm(total_patches)
            split = max(1, target_total_area)
            split = min(split, total_patches - 1)
            target_indices = all_indices[:split].sort().values
            context_indices = all_indices[split:].sort().values

        return {
            "context_indices": context_indices,
            "target_indices": target_indices,
        }


# ======================================================================
# Multi-Block Masking — non-overlapping rectangular target blocks
# ======================================================================


class MultiBlockMasking:
    """Generates multiple non-overlapping rectangular target blocks.

    An improved masking strategy that places *num_blocks* rectangular blocks
    with guaranteed non-overlap and per-block coverage caps.

    Args:
        num_blocks: Number of target blocks to place.
        min_block_patches: Minimum area (in patches) of each block.
        max_block_coverage: Maximum fraction of total patches any single
            block may cover.
        min_aspect: Minimum aspect ratio (height / width).
        max_aspect: Maximum aspect ratio (height / width).
        seed: Optional RNG seed for reproducibility.
    """

    def __init__(
        self,
        num_blocks: int = 4,
        min_block_patches: int = 4,
        max_block_coverage: float = 0.30,
        min_aspect: float = 0.75,
        max_aspect: float = 1.5,
        seed: Optional[int] = None,
    ) -> None:
        self.num_blocks = num_blocks
        self.min_block_patches = min_block_patches
        self.max_block_coverage = max_block_coverage
        self.min_aspect = min_aspect
        self.max_aspect = max_aspect
        self._rng = random.Random(seed)

    def _sample_block(
        self,
        num_patches_h: int,
        num_patches_w: int,
        target_area: int,
        occupied: Set[int],
    ) -> Tuple[Set[int], bool]:
        """Try to place one non-overlapping rectangular block.

        Args:
            num_patches_h: Patch grid height.
            num_patches_w: Patch grid width.
            target_area: Desired area in patches.
            occupied: Set of already-occupied flat indices.

        Returns:
            Tuple of (set of flat indices for this block, success bool).
        """
        total = num_patches_h * num_patches_w
        max_area = int(total * self.max_block_coverage)
        target_area = max(self.min_block_patches, min(target_area, max_area))

        for _attempt in range(50):
            log_aspect = self._rng.uniform(
                math.log(self.min_aspect), math.log(self.max_aspect)
            )
            aspect = math.exp(log_aspect)
            bh = int(round(math.sqrt(target_area * aspect)))
            bw = int(round(math.sqrt(target_area / aspect)))
            bh = max(1, min(bh, num_patches_h))
            bw = max(1, min(bw, num_patches_w))

            if bh * bw < self.min_block_patches:
                continue

            top = self._rng.randint(0, num_patches_h - bh)
            left = self._rng.randint(0, num_patches_w - bw)

            indices: Set[int] = set()
            for r in range(top, top + bh):
                for c in range(left, left + bw):
                    indices.add(r * num_patches_w + c)

            if indices.isdisjoint(occupied):
                return indices, True

        return set(), False

    def generate_mask(
        self,
        num_patches_h: int,
        num_patches_w: int,
        target_coverage: float = 0.5,
    ) -> dict[str, torch.Tensor]:
        """Generate non-overlapping multi-block mask.

        Args:
            num_patches_h: Patch grid height.
            num_patches_w: Patch grid width.
            target_coverage: Desired fraction of patches to mask.

        Returns:
            Dictionary with ``"context_indices"`` and ``"target_indices"``
            (both sorted 1-D :class:`torch.LongTensor`).
        """
        total_patches = num_patches_h * num_patches_w
        per_block_area = max(
            self.min_block_patches,
            int(round(total_patches * target_coverage / self.num_blocks)),
        )

        occupied: Set[int] = set()
        for _ in range(self.num_blocks):
            block_indices, ok = self._sample_block(
                num_patches_h, num_patches_w, per_block_area, occupied
            )
            if ok:
                occupied |= block_indices

        # Fallback: if no blocks were placed, do a simple random split
        if len(occupied) == 0:
            all_idx = list(range(total_patches))
            self._rng.shuffle(all_idx)
            split = max(1, int(total_patches * target_coverage))
            split = min(split, total_patches - 1)
            target_indices = torch.tensor(sorted(all_idx[:split]), dtype=torch.long)
            context_indices = torch.tensor(sorted(all_idx[split:]), dtype=torch.long)
        else:
            target_set = occupied
            context_set = set(range(total_patches)) - target_set
            target_indices = torch.tensor(sorted(target_set), dtype=torch.long)
            context_indices = torch.tensor(sorted(context_set), dtype=torch.long)

            # Ensure at least one context patch
            if context_indices.numel() == 0:
                target_indices = target_indices[:-1]
                context_indices = torch.tensor(
                    [target_indices[-1].item() + 1], dtype=torch.long
                )

        return {
            "context_indices": context_indices,
            "target_indices": target_indices,
        }
