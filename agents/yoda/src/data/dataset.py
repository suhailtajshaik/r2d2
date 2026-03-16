"""Dataset classes for VL-JEPA training and evaluation."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import torch
import torch.utils.data
from PIL import Image
from transformers import AutoTokenizer
from torchvision import transforms as T


class ProductDataset(torch.utils.data.Dataset):
    """Multi-modal dataset that pairs images with text captions.

    Supports two data sources:
      - A local directory containing ``images/`` and ``captions.json``.
      - A HuggingFace ``datasets`` dataset identifier (loaded lazily).

    Each sample is returned as a dictionary with keys ``image``, ``input_ids``,
    ``attention_mask``, and ``caption``.

    Args:
        data_dir: Path to a local data directory.  Must contain an ``images/``
            sub-directory and a ``captions.json`` file that maps filenames to
            caption strings.
        hf_dataset: HuggingFace dataset identifier, e.g.
            ``"ydshieh/coco_dataset_script"``.  Mutually exclusive with
            *data_dir*.
        split: Dataset split when loading from HuggingFace (default
            ``"train"``).
        transform: Optional torchvision transform applied to every image.
        tokenizer: A pre-instantiated HuggingFace tokenizer.  When *None*, the
            ``bert-base-uncased`` tokenizer is loaded automatically.
        max_text_length: Maximum token length for the text tokenizer.
    """

    def __init__(
        self,
        data_dir: Optional[str] = None,
        hf_dataset: Optional[str] = None,
        split: str = "train",
        transform: Optional[Any] = None,
        tokenizer: Optional[Any] = None,
        max_text_length: int = 77,
    ) -> None:
        if data_dir is None and hf_dataset is None:
            raise ValueError("Either data_dir or hf_dataset must be provided.")

        self.data_dir = Path(data_dir) if data_dir is not None else None
        self.hf_dataset_name = hf_dataset
        self.split = split
        self.transform = transform
        self.max_text_length = max_text_length

        # Tokenizer ---------------------------------------------------------
        if tokenizer is not None:
            self.tokenizer = tokenizer
        else:
            self.tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

        # Load data ----------------------------------------------------------
        self._hf_dataset: Optional[Any] = None  # lazy import guard

        if self.data_dir is not None:
            self._load_local()
        else:
            self._load_huggingface()

    # ------------------------------------------------------------------
    # Internal loaders
    # ------------------------------------------------------------------

    def _load_local(self) -> None:
        """Populate ``self.samples`` from a local directory layout.

        Expected structure::

            data_dir/
                images/
                    img_001.jpg
                    img_002.png
                    ...
                captions.json   # {"img_001.jpg": "A red shoe ...", ...}
        """
        assert self.data_dir is not None
        images_dir = self.data_dir / "images"
        captions_path = self.data_dir / "captions.json"

        if not images_dir.is_dir():
            raise FileNotFoundError(f"Image directory not found: {images_dir}")
        if not captions_path.is_file():
            raise FileNotFoundError(f"Captions file not found: {captions_path}")

        with open(captions_path, "r", encoding="utf-8") as fh:
            captions_map: Dict[str, str] = json.load(fh)

        self.samples: List[Tuple[Path, str]] = []
        for filename, caption in captions_map.items():
            img_path = images_dir / filename
            if img_path.is_file():
                self.samples.append((img_path, caption))

        if len(self.samples) == 0:
            raise RuntimeError(
                f"No valid image-caption pairs found under {self.data_dir}"
            )

    def _load_huggingface(self) -> None:
        """Load a HuggingFace ``datasets`` dataset."""
        from datasets import load_dataset  # type: ignore[import-untyped]

        self._hf_dataset = load_dataset(
            self.hf_dataset_name, split=self.split
        )

    # ------------------------------------------------------------------
    # Dataset protocol
    # ------------------------------------------------------------------

    def __len__(self) -> int:
        if self._hf_dataset is not None:
            return len(self._hf_dataset)  # type: ignore[arg-type]
        return len(self.samples)

    def __getitem__(self, index: int) -> Dict[str, Any]:
        """Return a single sample as a dictionary.

        Returns:
            A dict with keys:
            - ``image``:  float tensor of shape ``(C, H, W)``
            - ``input_ids``:  long tensor of token ids
            - ``attention_mask``:  long tensor (1 for real tokens, 0 for
              padding)
            - ``caption``:  the raw caption string
        """
        if self._hf_dataset is not None:
            return self._getitem_hf(index)
        return self._getitem_local(index)

    def _getitem_local(self, index: int) -> Dict[str, Any]:
        img_path, caption = self.samples[index]
        image = Image.open(img_path).convert("RGB")
        if self.transform is not None:
            image = self.transform(image)
        else:
            image = T.ToTensor()(image)
        return self._build_sample(image, caption)

    def _getitem_hf(self, index: int) -> Dict[str, Any]:
        row = self._hf_dataset[index]  # type: ignore[index]

        # HuggingFace image datasets typically expose an ``image`` column that
        # is already a PIL image, and a ``text`` or ``caption`` column.
        image = row.get("image") or row.get("img")
        if image is None:
            raise KeyError(
                "HuggingFace dataset row must contain an 'image' or 'img' key."
            )
        if not isinstance(image, Image.Image):
            image = Image.open(image).convert("RGB")
        else:
            image = image.convert("RGB")

        caption: str = (
            row.get("caption")
            or row.get("text")
            or row.get("sentence")
            or ""
        )

        if self.transform is not None:
            image = self.transform(image)
        else:
            image = T.ToTensor()(image)

        return self._build_sample(image, caption)

    def _build_sample(
        self, image: torch.Tensor, caption: str
    ) -> Dict[str, Any]:
        encoding = self.tokenizer(
            caption,
            padding="max_length",
            truncation=True,
            max_length=self.max_text_length,
            return_tensors="pt",
        )
        return {
            "image": image,
            "input_ids": encoding["input_ids"].squeeze(0),
            "attention_mask": encoding["attention_mask"].squeeze(0),
            "caption": caption,
        }


class SyntheticDataset(torch.utils.data.Dataset):
    """Synthetic dataset for quick testing and demos.

    Generates random RGB images and dummy text captions so that the full
    training pipeline can be exercised without real data.

    Args:
        num_samples: Number of synthetic samples in the dataset.
        image_size: Spatial resolution of generated images (square).
        max_text_length: Maximum token length for the dummy tokenizer output.
        tokenizer: Optional pre-instantiated tokenizer.  Defaults to
            ``bert-base-uncased``.
    """

    DUMMY_CAPTIONS: List[str] = [
        "a photo of a product",
        "an image showing an item on a white background",
        "a close-up of a red sneaker",
        "a blue handbag on a wooden table",
        "a pair of sunglasses on a sandy beach",
        "a laptop computer on a desk",
        "a ceramic mug with a floral pattern",
        "a silver wristwatch with a leather strap",
        "a stack of colorful books",
        "a green plant in a terracotta pot",
    ]

    def __init__(
        self,
        num_samples: int = 1000,
        image_size: int = 224,
        max_text_length: int = 77,
        tokenizer: Optional[Any] = None,
    ) -> None:
        self.num_samples = num_samples
        self.image_size = image_size
        self.max_text_length = max_text_length

        if tokenizer is not None:
            self.tokenizer = tokenizer
        else:
            self.tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

    def __len__(self) -> int:
        return self.num_samples

    def __getitem__(self, index: int) -> Dict[str, Any]:
        """Return a synthetic sample.

        The random generator is seeded per-index so that the same index always
        yields the same data (useful for reproducibility during debugging).

        Returns:
            A dict matching the :class:`ProductDataset` output schema.
        """
        rng = torch.Generator().manual_seed(index)
        image = torch.rand(
            3, self.image_size, self.image_size, generator=rng
        )
        caption = self.DUMMY_CAPTIONS[index % len(self.DUMMY_CAPTIONS)]

        encoding = self.tokenizer(
            caption,
            padding="max_length",
            truncation=True,
            max_length=self.max_text_length,
            return_tensors="pt",
        )
        return {
            "image": image,
            "input_ids": encoding["input_ids"].squeeze(0),
            "attention_mask": encoding["attention_mask"].squeeze(0),
            "caption": caption,
        }
