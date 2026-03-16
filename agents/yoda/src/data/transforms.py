"""Image transforms for VL-JEPA training and evaluation.

All transforms return a ``torchvision.transforms.Compose`` pipeline that
converts a PIL image to a normalised float tensor of shape ``(3, H, W)``.
"""

from __future__ import annotations

from torchvision import transforms as T


# ImageNet channel-wise statistics
IMAGENET_MEAN: tuple[float, float, float] = (0.485, 0.456, 0.406)
IMAGENET_STD: tuple[float, float, float] = (0.229, 0.224, 0.225)


def get_train_transforms(image_size: int = 224) -> T.Compose:
    """Build the training-time augmentation pipeline.

    The pipeline applies:
      1. ``RandomResizedCrop`` to *image_size* (scale 0.2 -- 1.0).
      2. ``RandomHorizontalFlip`` with probability 0.5.
      3. ``ColorJitter`` (brightness, contrast, saturation, hue).
      4. Conversion to tensor and ImageNet normalisation.

    Args:
        image_size: Target spatial resolution of the output crop.

    Returns:
        A :class:`torchvision.transforms.Compose` instance.
    """
    return T.Compose(
        [
            T.RandomResizedCrop(image_size, scale=(0.2, 1.0)),
            T.RandomHorizontalFlip(p=0.5),
            T.ColorJitter(
                brightness=0.4,
                contrast=0.4,
                saturation=0.4,
                hue=0.1,
            ),
            T.ToTensor(),
            T.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
        ]
    )


def get_eval_transforms(image_size: int = 224) -> T.Compose:
    """Build the evaluation-time transform pipeline.

    The pipeline applies:
      1. ``Resize`` to 256 (preserving aspect ratio with bilinear
         interpolation).
      2. ``CenterCrop`` to *image_size*.
      3. Conversion to tensor and ImageNet normalisation.

    Args:
        image_size: Target spatial resolution of the output crop.

    Returns:
        A :class:`torchvision.transforms.Compose` instance.
    """
    resize_size = int(image_size * 256 / 224)
    return T.Compose(
        [
            T.Resize(resize_size, interpolation=T.InterpolationMode.BILINEAR),
            T.CenterCrop(image_size),
            T.ToTensor(),
            T.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
        ]
    )
