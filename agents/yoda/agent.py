"""
🧙 Yoda — Self-Evolving JEPA Learning Agent

"Feed me resources, you must. Build the model, I will."

Yoda learns from research papers, URLs, and text — extracts structured
knowledge, updates its understanding, and evolves real VL-JEPA model code.
The more you teach it, the better the model gets.

Usage examples::

    python agent.py learn --file paper.pdf
    python agent.py learn --url https://arxiv.org/abs/2301.08243
    python agent.py learn --text "JEPA uses a predictor in latent space..."
    python agent.py evolve
    python agent.py status
    python agent.py train --epochs 5
    python agent.py demo
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

# ---------------------------------------------------------------------------
# Lazy imports — heavy libraries are loaded only when the command that needs
# them is actually invoked.  This keeps ``agent.py --help`` fast.
# ---------------------------------------------------------------------------


def _import_learner_pipeline() -> tuple:
    """Import the learner pipeline components.

    Returns:
        Tuple of ``(ResourceParser, KnowledgeExtractor, KnowledgeUpdater)``.
    """
    from learner.resource_parser import ResourceParser
    from learner.knowledge_extractor import KnowledgeExtractor
    from learner.knowledge_updater import KnowledgeUpdater

    return ResourceParser, KnowledgeExtractor, KnowledgeUpdater


def _import_code_evolver() -> type:
    """Import the CodeEvolver class.

    Returns:
        The :class:`CodeEvolver` class.
    """
    from learner.code_evolver import CodeEvolver

    return CodeEvolver


def _import_evolution_tracker() -> type:
    """Import the EvolutionTracker class.

    Returns:
        The :class:`EvolutionTracker` class.
    """
    from learner.evolution_tracker import EvolutionTracker

    return EvolutionTracker


def _import_training_stack() -> tuple:
    """Import model, dataset, and trainer classes.

    Returns:
        Tuple of ``(VLJEPA, SyntheticDataset, Trainer)``.
    """
    from src.models.vl_jepa import VLJEPA
    from src.data.dataset import SyntheticDataset
    from src.training.trainer import Trainer

    return VLJEPA, SyntheticDataset, Trainer


# ---------------------------------------------------------------------------
# ANSI colour helpers
# ---------------------------------------------------------------------------

class _Colours:
    """ANSI escape sequences for terminal colours."""

    HEADER: str = "\033[95m"
    BLUE: str = "\033[94m"
    CYAN: str = "\033[96m"
    GREEN: str = "\033[92m"
    YELLOW: str = "\033[93m"
    RED: str = "\033[91m"
    BOLD: str = "\033[1m"
    DIM: str = "\033[2m"
    RESET: str = "\033[0m"


C = _Colours()


def _info(msg: str) -> None:
    """Print an informational message in cyan."""
    print(f"{C.CYAN}[INFO]{C.RESET} {msg}")


def _success(msg: str) -> None:
    """Print a success message in green."""
    print(f"{C.GREEN}[OK]{C.RESET}   {msg}")


def _warn(msg: str) -> None:
    """Print a warning message in yellow."""
    print(f"{C.YELLOW}[WARN]{C.RESET} {msg}")


def _error(msg: str) -> None:
    """Print an error message in red to stderr."""
    print(f"{C.RED}[ERR]{C.RESET}  {msg}", file=sys.stderr)


def _banner(title: str) -> None:
    """Print a bold section banner."""
    width = 60
    print()
    print(f"{C.BOLD}{C.HEADER}{'=' * width}{C.RESET}")
    print(f"{C.BOLD}{C.HEADER}  {title}{C.RESET}")
    print(f"{C.BOLD}{C.HEADER}{'=' * width}{C.RESET}")
    print()


# ---------------------------------------------------------------------------
# Config loading
# ---------------------------------------------------------------------------

def load_config(config_path: str = "config.yaml") -> Dict[str, Any]:
    """Load the project configuration from a YAML file.

    Args:
        config_path: Path to the YAML configuration file.  Resolved relative
            to the project root (the directory containing this script).

    Returns:
        Parsed configuration dictionary.

    Raises:
        FileNotFoundError: If the configuration file does not exist.
        yaml.YAMLError: If the file is not valid YAML.
    """
    project_root = Path(__file__).resolve().parent
    full_path = project_root / config_path

    if not full_path.is_file():
        raise FileNotFoundError(
            f"Configuration file not found: {full_path}\n"
            "Create a config.yaml in the project root or pass --config <path>."
        )

    with open(full_path, "r", encoding="utf-8") as fh:
        config: Dict[str, Any] = yaml.safe_load(fh)

    return config


# ---------------------------------------------------------------------------
# Sub-command handlers
# ---------------------------------------------------------------------------

def cmd_learn(args: argparse.Namespace, config: Dict[str, Any]) -> None:
    """Ingest a research resource through the learning pipeline.

    Parses the input (PDF, URL, or raw text), extracts structured knowledge
    using an LLM, and updates the persistent knowledge base.

    Args:
        args: Parsed CLI arguments.  Exactly one of ``args.file``,
            ``args.url``, or ``args.text`` must be set.
        config: Project configuration dictionary.
    """
    _banner("VL-JEPA Learn")

    ResourceParser, KnowledgeExtractor, KnowledgeUpdater = _import_learner_pipeline()

    parser = ResourceParser()
    extractor = KnowledgeExtractor()
    updater = KnowledgeUpdater(
        knowledge_dir=config.get("paths", {}).get("knowledge_dir", "knowledge"),
    )

    # ------------------------------------------------------------------
    # Step 1 — parse the resource
    # ------------------------------------------------------------------
    if args.file:
        source_label = args.file
        _info(f"Parsing PDF: {args.file}")
        document = parser.parse_pdf(args.file)
    elif args.url:
        source_label = args.url
        _info(f"Fetching URL: {args.url}")
        document = parser.parse_url(args.url)
    elif args.text:
        source_label = "direct text input"
        _info("Parsing raw text input")
        document = parser.parse_text(args.text)
    else:
        _error("Provide one of --file, --url, or --text.")
        sys.exit(1)

    content_preview = document["content"][:200].replace("\n", " ")
    _info(f"Parsed {len(document['content']):,} characters from {document['type']}")
    _info(f"Preview: {content_preview}...")

    # ------------------------------------------------------------------
    # Step 2 — extract structured knowledge
    # ------------------------------------------------------------------
    _info("Extracting knowledge via LLM...")
    try:
        knowledge = extractor.extract(document)
        _success(f"Extracted knowledge with {len(knowledge)} keys")
    except Exception as exc:
        _error(f"Knowledge extraction failed: {exc}")
        sys.exit(1)

    # ------------------------------------------------------------------
    # Step 3 — update the knowledge base
    # ------------------------------------------------------------------
    _info("Updating knowledge base...")
    try:
        updated_files = updater.update(knowledge, source=source_label)
        for fpath in updated_files:
            _success(f"Updated: {fpath}")
    except Exception as exc:
        _error(f"Knowledge update failed: {exc}")
        sys.exit(1)

    _success("Learning pipeline complete.")


def cmd_evolve(args: argparse.Namespace, config: Dict[str, Any]) -> None:
    """Trigger autonomous code evolution based on accumulated knowledge.

    The :class:`CodeEvolver` reads the current knowledge base and source code,
    identifies improvements, and applies them.

    Args:
        args: Parsed CLI arguments (currently unused for this command).
        config: Project configuration dictionary.
    """
    _banner("VL-JEPA Evolve")

    CodeEvolver = _import_code_evolver()

    evolver = CodeEvolver(
        config=config.get("learner", {}),
        knowledge_dir=config.get("paths", {}).get("knowledge_dir", "knowledge"),
        src_dir=config.get("paths", {}).get("src_dir", "src"),
    )

    _info("Analysing knowledge base and source code...")
    try:
        result = evolver.evolve()
    except Exception as exc:
        _error(f"Code evolution failed: {exc}")
        sys.exit(1)

    if result.get("changes"):
        for change in result["changes"]:
            _success(f"Applied: {change}")
    else:
        _warn("No code changes were generated.")

    if result.get("summary"):
        print()
        print(f"{C.BOLD}Summary:{C.RESET}")
        print(f"  {result['summary']}")

    _success("Evolution complete.")


def cmd_status(args: argparse.Namespace, config: Dict[str, Any]) -> None:
    """Display the current project status.

    Shows the model version from ``evolution_log.md``, a summary of knowledge
    files (line counts and last-modified timestamps), and the total model
    parameter count.

    Args:
        args: Parsed CLI arguments (currently unused for this command).
        config: Project configuration dictionary.
    """
    _banner("VL-JEPA Status")

    project_root = Path(__file__).resolve().parent

    # ------------------------------------------------------------------
    # Model version from evolution log
    # ------------------------------------------------------------------
    evolution_log_path = project_root / "evolution_log.md"
    if evolution_log_path.is_file():
        with open(evolution_log_path, "r", encoding="utf-8") as fh:
            lines = fh.readlines()

        version_line: Optional[str] = None
        for line in reversed(lines):
            stripped = line.strip()
            if stripped.startswith("## v") or stripped.startswith("## V"):
                version_line = stripped.lstrip("# ").strip()
                break

        if version_line:
            print(f"  {C.BOLD}Model version:{C.RESET}  {C.GREEN}{version_line}{C.RESET}")
        else:
            print(f"  {C.BOLD}Model version:{C.RESET}  {C.DIM}(no version header found){C.RESET}")
    else:
        print(f"  {C.BOLD}Model version:{C.RESET}  {C.DIM}evolution_log.md not found{C.RESET}")

    # ------------------------------------------------------------------
    # Knowledge files summary
    # ------------------------------------------------------------------
    knowledge_dir = project_root / config.get("paths", {}).get("knowledge_dir", "knowledge")
    print()
    print(f"  {C.BOLD}Knowledge base:{C.RESET}  {knowledge_dir}")

    if knowledge_dir.is_dir():
        knowledge_files: List[Path] = sorted(knowledge_dir.rglob("*"))
        knowledge_files = [f for f in knowledge_files if f.is_file()]

        if knowledge_files:
            for kf in knowledge_files:
                try:
                    line_count = sum(1 for _ in open(kf, "r", encoding="utf-8"))
                except (UnicodeDecodeError, PermissionError):
                    line_count = -1

                mtime = datetime.fromtimestamp(kf.stat().st_mtime)
                mtime_str = mtime.strftime("%Y-%m-%d %H:%M")
                rel = kf.relative_to(project_root)

                if line_count >= 0:
                    print(
                        f"    {C.CYAN}{rel}{C.RESET}  "
                        f"{line_count:>5} lines  "
                        f"{C.DIM}modified {mtime_str}{C.RESET}"
                    )
                else:
                    print(
                        f"    {C.CYAN}{rel}{C.RESET}  "
                        f"{C.DIM}(binary){C.RESET}  "
                        f"{C.DIM}modified {mtime_str}{C.RESET}"
                    )
        else:
            _warn("Knowledge directory is empty.")
    else:
        _warn("Knowledge directory does not exist yet.")

    # ------------------------------------------------------------------
    # Model parameter count
    # ------------------------------------------------------------------
    print()
    try:
        VLJEPA, _, _ = _import_training_stack()
        model_cfg = config.get("model", {})
        model = VLJEPA(config=model_cfg)
        total_params = sum(p.numel() for p in model.parameters())
        trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
        print(
            f"  {C.BOLD}Model parameters:{C.RESET}  "
            f"{total_params:,} total / {trainable_params:,} trainable"
        )
    except Exception as exc:
        _warn(f"Could not instantiate model to count parameters: {exc}")

    # ------------------------------------------------------------------
    # Checkpoints
    # ------------------------------------------------------------------
    ckpt_dir = project_root / config.get("paths", {}).get("checkpoints_dir", "checkpoints")
    print()
    if ckpt_dir.is_dir():
        ckpts = sorted(ckpt_dir.glob("*.pt"))
        if ckpts:
            latest = ckpts[-1]
            mtime = datetime.fromtimestamp(latest.stat().st_mtime)
            print(
                f"  {C.BOLD}Checkpoints:{C.RESET}  "
                f"{len(ckpts)} saved  |  latest: {latest.name}  "
                f"{C.DIM}({mtime.strftime('%Y-%m-%d %H:%M')}){C.RESET}"
            )
        else:
            print(f"  {C.BOLD}Checkpoints:{C.RESET}  {C.DIM}none{C.RESET}")
    else:
        print(f"  {C.BOLD}Checkpoints:{C.RESET}  {C.DIM}directory not created yet{C.RESET}")

    print()


def cmd_train(args: argparse.Namespace, config: Dict[str, Any]) -> None:
    """Train the VL-JEPA model.

    Instantiates the model, creates a dataset (synthetic by default or real
    if configured), builds a DataLoader, and runs the training loop for the
    requested number of epochs.

    Args:
        args: Parsed CLI arguments.  ``args.epochs`` overrides the config
            default.
        config: Project configuration dictionary.
    """
    _banner("VL-JEPA Train")

    import torch
    from torch.utils.data import DataLoader

    VLJEPA, SyntheticDataset, Trainer = _import_training_stack()

    model_cfg = config.get("model", {})
    train_cfg = config.get("training", {})
    data_cfg = config.get("data", {})
    paths_cfg = config.get("paths", {})

    num_epochs: int = args.epochs if args.epochs is not None else train_cfg.get("num_epochs", 100)
    batch_size: int = train_cfg.get("batch_size", 32)
    num_workers: int = data_cfg.get("num_workers", 4)
    image_size: int = data_cfg.get("image_size", model_cfg.get("image_size", 224))

    # ------------------------------------------------------------------
    # Model
    # ------------------------------------------------------------------
    _info("Building VL-JEPA model...")
    model = VLJEPA(config=model_cfg)
    total_params = sum(p.numel() for p in model.parameters())
    _success(f"Model ready: {total_params:,} parameters")

    # ------------------------------------------------------------------
    # Dataset
    # ------------------------------------------------------------------
    train_dir = data_cfg.get("train_dir")
    hf_dataset = data_cfg.get("hf_dataset")

    if train_dir and Path(train_dir).is_dir():
        _info(f"Loading real dataset from {train_dir}")
        from src.data.dataset import ProductDataset
        from src.data.transforms import get_train_transforms

        transform = get_train_transforms(image_size=image_size)
        dataset = ProductDataset(data_dir=train_dir, transform=transform)
    elif hf_dataset:
        _info(f"Loading HuggingFace dataset: {hf_dataset}")
        from src.data.dataset import ProductDataset
        from src.data.transforms import get_train_transforms

        transform = get_train_transforms(image_size=image_size)
        dataset = ProductDataset(hf_dataset=hf_dataset, transform=transform)
    else:
        _warn("No real dataset configured; falling back to synthetic data.")
        dataset = SyntheticDataset(
            num_samples=max(256, batch_size * 10),
            image_size=image_size,
        )

    _success(f"Dataset loaded: {len(dataset)} samples")

    # ------------------------------------------------------------------
    # DataLoader
    # ------------------------------------------------------------------
    def _collate_fn(batch: List[Dict[str, Any]]) -> tuple:
        """Stack batch items into (images, input_ids, attention_mask) tensors."""
        images = torch.stack([item["image"] for item in batch])
        input_ids = torch.stack([item["input_ids"] for item in batch])
        attention_mask = torch.stack([item["attention_mask"] for item in batch])
        return images, input_ids, attention_mask

    train_loader = DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers,
        pin_memory=True,
        collate_fn=_collate_fn,
        drop_last=True,
    )

    # ------------------------------------------------------------------
    # Trainer
    # ------------------------------------------------------------------
    trainer_config: Dict[str, Any] = {
        "lr": train_cfg.get("learning_rate", 1.5e-4),
        "weight_decay": train_cfg.get("weight_decay", 0.05),
        "num_epochs": num_epochs,
        "ema_momentum": train_cfg.get("ema_momentum", 0.996),
        "alignment_weight": train_cfg.get("alignment_weight", 0.5),
        "checkpoint_every": train_cfg.get("checkpoint_every", 10),
        "checkpoint_dir": paths_cfg.get("checkpoints_dir", "checkpoints"),
        "use_amp": train_cfg.get("mixed_precision", True),
    }

    _info(f"Training for {num_epochs} epoch(s), batch_size={batch_size}, lr={trainer_config['lr']}")
    trainer = Trainer(model=model, train_loader=train_loader, config=trainer_config)

    start_time = time.time()
    history = trainer.train(num_epochs=num_epochs)
    elapsed = time.time() - start_time

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    print()
    _success(f"Training complete in {elapsed:.1f}s ({num_epochs} epochs)")

    if history:
        final = history[-1]
        print(f"  Final losses:")
        print(f"    total     = {final.get('avg_total_loss', 0):.6f}")
        print(f"    jepa      = {final.get('avg_jepa_loss', 0):.6f}")
        print(f"    alignment = {final.get('avg_alignment_loss', 0):.6f}")


def cmd_demo(args: argparse.Namespace, config: Dict[str, Any]) -> None:
    """Run a quick demonstration on synthetic data.

    Loads the model (from the latest checkpoint if available, otherwise from
    scratch), generates a small batch of synthetic images, runs a forward pass,
    and prints the resulting embedding shapes and similarity scores.

    Args:
        args: Parsed CLI arguments (currently unused for this command).
        config: Project configuration dictionary.
    """
    _banner("VL-JEPA Demo")

    import torch

    VLJEPA, SyntheticDataset, _ = _import_training_stack()

    model_cfg = config.get("model", {})
    paths_cfg = config.get("paths", {})
    image_size: int = config.get("data", {}).get(
        "image_size", model_cfg.get("image_size", 224)
    )

    # ------------------------------------------------------------------
    # Model
    # ------------------------------------------------------------------
    _info("Building VL-JEPA model...")
    model = VLJEPA(config=model_cfg)
    model.eval()

    # Try loading the latest checkpoint
    ckpt_dir = Path(paths_cfg.get("checkpoints_dir", "checkpoints"))
    loaded_checkpoint = False
    if ckpt_dir.is_dir():
        ckpts = sorted(ckpt_dir.glob("*.pt"))
        if ckpts:
            latest_ckpt = ckpts[-1]
            _info(f"Loading checkpoint: {latest_ckpt.name}")
            try:
                state = torch.load(latest_ckpt, map_location="cpu", weights_only=False)
                model.load_state_dict(state["model_state_dict"])
                loaded_checkpoint = True
                _success(f"Loaded checkpoint from epoch {state.get('epoch', '?')}")
            except Exception as exc:
                _warn(f"Could not load checkpoint: {exc}")

    if not loaded_checkpoint:
        _warn("No checkpoint loaded; using randomly initialised weights.")

    total_params = sum(p.numel() for p in model.parameters())
    _success(f"Model ready: {total_params:,} parameters")

    # ------------------------------------------------------------------
    # Synthetic data
    # ------------------------------------------------------------------
    _info("Generating synthetic batch...")
    dataset = SyntheticDataset(num_samples=8, image_size=image_size)

    images_list: List[torch.Tensor] = []
    input_ids_list: List[torch.Tensor] = []
    attn_mask_list: List[torch.Tensor] = []
    captions: List[str] = []

    for i in range(min(8, len(dataset))):
        sample = dataset[i]
        images_list.append(sample["image"])
        input_ids_list.append(sample["input_ids"])
        attn_mask_list.append(sample["attention_mask"])
        captions.append(sample["caption"])

    images = torch.stack(images_list)
    input_ids = torch.stack(input_ids_list)
    attention_mask = torch.stack(attn_mask_list)

    _success(f"Batch shape: images={list(images.shape)}, tokens={list(input_ids.shape)}")

    # ------------------------------------------------------------------
    # Forward pass
    # ------------------------------------------------------------------
    _info("Running forward pass...")
    from src.training.masking import BlockMasking

    masker = BlockMasking(seed=42)
    grid_size = image_size // model_cfg.get("patch_size", 16)
    mask = masker.generate_mask(
        num_patches_h=grid_size,
        num_patches_w=grid_size,
        num_targets=4,
        target_coverage=0.5,
    )

    with torch.no_grad():
        outputs = model(
            images=images,
            text_input_ids=input_ids,
            text_attention_mask=attention_mask,
            mask=mask,
        )

    # ------------------------------------------------------------------
    # Display results
    # ------------------------------------------------------------------
    print()
    print(f"  {C.BOLD}Output embeddings:{C.RESET}")
    for key, val in outputs.items():
        if isinstance(val, torch.Tensor):
            print(f"    {key:30s}  shape={list(val.shape)}  dtype={val.dtype}")

    # Cross-modal similarity
    if "image_cls_embedding" in outputs and "text_embedding" in outputs:
        import torch.nn.functional as F

        img_emb = F.normalize(outputs["image_cls_embedding"], dim=-1)
        txt_emb = F.normalize(outputs["text_embedding"], dim=-1)
        similarity = img_emb @ txt_emb.T  # (B, B)

        print()
        print(f"  {C.BOLD}Image-text cosine similarity matrix:{C.RESET}")
        batch_size = similarity.size(0)
        header = "         " + "".join(f"  txt_{j:<3}" for j in range(batch_size))
        print(f"    {header}")
        for i in range(batch_size):
            row_vals = "  ".join(f"{similarity[i, j]:.3f}" for j in range(batch_size))
            print(f"    img_{i}   {row_vals}")

        print()
        print(f"  {C.BOLD}Captions:{C.RESET}")
        for i, cap in enumerate(captions):
            print(f"    [{i}] {cap}")

    print()
    _success("Demo complete.")


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    """Construct the CLI argument parser with subcommands.

    Returns:
        Configured :class:`argparse.ArgumentParser`.
    """
    parser = argparse.ArgumentParser(
        prog="agent.py",
        description="VL-JEPA Agent -- autonomous vision-language JEPA learner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python agent.py learn --file paper.pdf\n"
            "  python agent.py learn --url https://arxiv.org/abs/2301.08243\n"
            "  python agent.py learn --text \"JEPA uses a predictor...\"\n"
            "  python agent.py evolve\n"
            "  python agent.py status\n"
            "  python agent.py train --epochs 5\n"
            "  python agent.py demo\n"
        ),
    )
    parser.add_argument(
        "--config",
        type=str,
        default="config.yaml",
        help="Path to the YAML configuration file (default: config.yaml)",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # ---- learn ----
    learn_parser = subparsers.add_parser(
        "learn",
        help="Ingest a research resource (PDF, URL, or raw text)",
    )
    learn_group = learn_parser.add_mutually_exclusive_group(required=True)
    learn_group.add_argument("--file", type=str, help="Path to a PDF file")
    learn_group.add_argument("--url", type=str, help="URL to fetch and parse")
    learn_group.add_argument("--text", type=str, help="Raw text to ingest")

    # ---- evolve ----
    subparsers.add_parser(
        "evolve",
        help="Analyse knowledge and evolve source code",
    )

    # ---- status ----
    subparsers.add_parser(
        "status",
        help="Show knowledge summary, model version, and parameter count",
    )

    # ---- train ----
    train_parser = subparsers.add_parser(
        "train",
        help="Train the VL-JEPA model",
    )
    train_parser.add_argument(
        "--epochs",
        type=int,
        default=None,
        help="Number of training epochs (overrides config)",
    )

    # ---- demo ----
    subparsers.add_parser(
        "demo",
        help="Quick demo on synthetic data",
    )

    return parser


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def main() -> None:
    """Parse CLI arguments, load configuration, and dispatch to the
    appropriate sub-command handler."""
    parser = build_parser()
    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    # Load configuration
    try:
        config = load_config(args.config)
    except FileNotFoundError as exc:
        _error(str(exc))
        sys.exit(1)
    except yaml.YAMLError as exc:
        _error(f"Invalid YAML in configuration file: {exc}")
        sys.exit(1)

    # Dispatch
    handlers: Dict[str, Any] = {
        "learn": cmd_learn,
        "evolve": cmd_evolve,
        "status": cmd_status,
        "train": cmd_train,
        "demo": cmd_demo,
    }

    handler = handlers.get(args.command)
    if handler is None:
        _error(f"Unknown command: {args.command}")
        parser.print_help()
        sys.exit(1)

    try:
        handler(args, config)
    except KeyboardInterrupt:
        print()
        _warn("Interrupted by user.")
        sys.exit(130)
    except Exception as exc:
        _error(f"Unhandled error: {exc}")
        if os.environ.get("VLJEPA_DEBUG"):
            raise
        sys.exit(1)


if __name__ == "__main__":
    main()
