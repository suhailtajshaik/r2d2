"""Cross-modal retrieval evaluation for VL-JEPA.

Provides :class:`RetrievalEvaluator` which extracts image and text embeddings
from a trained model, builds a cosine-similarity index, and computes recall@k.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence, Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader


class RetrievalEvaluator:
    """Evaluate a vision-language model on cross-modal retrieval.

    The evaluator performs the following workflow:

    1. Iterate over *dataloader* and extract normalised image / text
       embeddings from *model*.
    2. Compute pairwise cosine similarity between the two embedding sets.
    3. Report recall@k for configurable values of *k*.

    The model is expected to expose two methods (or callable attributes):

    * ``encode_image(images: Tensor) -> Tensor``
    * ``encode_text(input_ids: Tensor, attention_mask: Tensor) -> Tensor``

    Both should return L2-normalised embedding tensors of shape
    ``(batch, embed_dim)``.

    Args:
        model: A vision-language model with ``encode_image`` and
            ``encode_text`` methods.
        dataloader: A :class:`~torch.utils.data.DataLoader` that yields
            dicts with keys ``image``, ``input_ids``, and ``attention_mask``.
        device: Torch device for inference.
    """

    def __init__(
        self,
        model: nn.Module,
        dataloader: DataLoader,
        device: torch.device | str = "cpu",
    ) -> None:
        self.model = model
        self.dataloader = dataloader
        self.device = torch.device(device) if isinstance(device, str) else device

    # ------------------------------------------------------------------
    # Embedding extraction
    # ------------------------------------------------------------------

    @torch.no_grad()
    def extract_embeddings(
        self,
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """Run the model over the full dataloader and collect embeddings.

        Returns:
            A tuple ``(image_embeddings, text_embeddings)`` where each tensor
            has shape ``(N, embed_dim)`` and is L2-normalised along the last
            dimension.  *N* equals the total number of samples in the
            dataloader.
        """
        self.model.eval()
        self.model.to(self.device)

        image_embs: List[torch.Tensor] = []
        text_embs: List[torch.Tensor] = []

        for batch in self.dataloader:
            images = batch["image"].to(self.device)
            input_ids = batch["input_ids"].to(self.device)
            attention_mask = batch["attention_mask"].to(self.device)

            img_emb = self.model.encode_image(images)
            txt_emb = self.model.encode_text(input_ids, attention_mask)

            # Ensure L2 normalisation
            img_emb = F.normalize(img_emb, p=2, dim=-1)
            txt_emb = F.normalize(txt_emb, p=2, dim=-1)

            image_embs.append(img_emb.cpu())
            text_embs.append(txt_emb.cpu())

        image_embeddings = torch.cat(image_embs, dim=0)
        text_embeddings = torch.cat(text_embs, dim=0)
        return image_embeddings, text_embeddings

    # ------------------------------------------------------------------
    # kNN retrieval
    # ------------------------------------------------------------------

    @staticmethod
    def knn_retrieval(
        query_emb: torch.Tensor,
        gallery_emb: torch.Tensor,
        k: int = 5,
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """Retrieve the *k* nearest gallery items for every query.

        Similarity is measured by cosine similarity (dot-product of
        L2-normalised vectors).

        Args:
            query_emb: Tensor of shape ``(Q, D)`` -- the query embeddings.
            gallery_emb: Tensor of shape ``(G, D)`` -- the gallery embeddings.
            k: Number of nearest neighbours to return.

        Returns:
            A tuple ``(indices, scores)`` where:
            - *indices* has shape ``(Q, k)`` and contains gallery indices.
            - *scores* has shape ``(Q, k)`` and contains cosine similarities.
        """
        # query_emb: (Q, D), gallery_emb: (G, D) -> sim: (Q, G)
        sim = query_emb @ gallery_emb.t()
        scores, indices = sim.topk(k, dim=-1, largest=True, sorted=True)
        return indices, scores

    # ------------------------------------------------------------------
    # Full evaluation
    # ------------------------------------------------------------------

    def evaluate(
        self,
        k_values: Sequence[int] = (1, 5, 10),
    ) -> Dict[str, float]:
        """Run end-to-end retrieval evaluation.

        For both image-to-text and text-to-image retrieval the ground-truth
        match is assumed to be the sample at the *same* index (i.e. the
        dataloader must not shuffle).

        Args:
            k_values: The *k* values at which to compute recall.

        Returns:
            A dictionary mapping metric names to values, e.g.::

                {
                    "image_to_text_R@1": 0.45,
                    "image_to_text_R@5": 0.78,
                    "text_to_image_R@1": 0.42,
                    ...
                }
        """
        image_emb, text_emb = self.extract_embeddings()
        n = image_emb.size(0)
        ground_truth = torch.arange(n)

        results: Dict[str, float] = {}
        max_k = max(k_values)

        # Image -> Text retrieval
        i2t_indices, _ = self.knn_retrieval(image_emb, text_emb, k=max_k)
        for k in k_values:
            hits = (i2t_indices[:, :k] == ground_truth.unsqueeze(1)).any(dim=1)
            results[f"image_to_text_R@{k}"] = hits.float().mean().item()

        # Text -> Image retrieval
        t2i_indices, _ = self.knn_retrieval(text_emb, image_emb, k=max_k)
        for k in k_values:
            hits = (t2i_indices[:, :k] == ground_truth.unsqueeze(1)).any(dim=1)
            results[f"text_to_image_R@{k}"] = hits.float().mean().item()

        return results
