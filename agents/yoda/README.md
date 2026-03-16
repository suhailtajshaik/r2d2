# 🧙 Yoda — Self-Evolving JEPA Learning Agent

> *"Feed me resources, you must. Build the model, I will."*

A self-evolving AI agent that learns Vision-Language JEPA from research papers, URLs, and text you feed it — then builds and improves a real VL-JEPA model from those learnings. The more you teach it, the better the model gets.


A self-evolving learning agent that builds and improves a **Vision-Language JEPA** (Joint-Embedding Predictive Architecture) model. Feed it research papers, documentation, or datasets and it will extract knowledge, update its understanding, and evolve its own model code -- autonomously.

## Current Model Version: v0.3

- [x] **VL-JEPA core** — Context Encoder, Target Encoder (EMA), Predictor Network
- [x] **JEPAConfig** — Centralized dataclass configurator for all hyperparameters
- [x] **SelectiveDecoder** — Lightweight 2-layer transformer decoder (2.85x faster inference)
- [x] **CostModule** — Intrinsic cost (MSE prediction error) + Critic cost (learned value)
- [x] **ShortTermMemory** — Ring buffer for temporal embedding context
- [x] **VICReg loss** — Variance-Invariance-Covariance Regularization (alternative to InfoNCE)
- [x] **MultiBlockMasking** — Non-overlapping rectangular blocks (4 blocks, ~50% coverage)
- [x] **InfoNCE / NT-Xent** — Cross-modal alignment loss
- [x] **BlockMasking** — Original rectangular block masking strategy
- [x] **Language Encoder** — Frozen BERT for text embeddings
- [x] **Cross-modal projection heads** — MLP projections into shared space
- [x] **EMA target encoder updates** — Momentum 0.996

## What it does

Traditional ML pipelines are static: you write the code, tune hyperparameters, and repeat manually. This agent closes the loop. It reads resources (papers, docs, data), distills them into a structured knowledge base, and uses that knowledge to rewrite and improve its own model architecture, training procedure, and evaluation pipeline.

The core model is a **VL-JEPA** -- an extension of I-JEPA (Assran et al., 2023) to the vision-language domain. It learns visual representations by predicting masked patch embeddings and aligns them with language representations via contrastive learning.

## How it works

```
                    +------------------+
                    |  Resources       |
                    |  (papers, docs,  |
                    |   datasets)      |
                    +--------+---------+
                             |
                             v
                    +------------------+
                    | Resource Parser  |  learner/resource_parser.py
                    | (PDF, web, text) |
                    +--------+---------+
                             |
                             v
                    +------------------+
                    | Knowledge        |  knowledge/*.md
                    | Extractor        |  (timestamped, sourced entries)
                    +--------+---------+
                             |
                             v
                    +------------------+
                    | Code Evolver     |  Rewrites src/ based on
                    | (LLM-powered)    |  knowledge deltas
                    +--------+---------+
                             |
                             v
              +--------------+---------------+
              |                              |
              v                              v
    +------------------+           +------------------+
    | VL-JEPA Model    |           | Training Loop    |
    | src/models/       |           | src/training/     |
    +------------------+           +------------------+
              |                              |
              v                              v
    +------------------+           +------------------+
    | Evaluation       |           | Evolution Log    |
    | src/evaluation/   |           | knowledge/       |
    +------------------+           +------------------+
```

**Feed resources** -- The resource parser ingests PDFs (via PyMuPDF), web pages (via BeautifulSoup), or plain text and extracts structured content.

**Extract knowledge** -- An LLM-powered extractor identifies concepts, architecture details, training tricks, and dataset information, then appends them as timestamped entries to the appropriate knowledge-base file.

**Evolve model code** -- The code evolver compares the current knowledge base against the existing source code, identifies gaps or improvements, and generates code patches. Every evolution is logged in `knowledge/evolution_log.md`.

## Quick start

```bash
# 1. Clone and install
git clone <repo-url> && cd yoda
pip install -r requirements.txt

# 2. Set your Anthropic API key (used by the learner pipeline)
export ANTHROPIC_API_KEY="sk-ant-..."

# 3. Feed a research paper
python -m learner.resource_parser --input papers/ijepa.pdf --type pdf

# 4. Evolve the model based on new knowledge
python -m learner.evolve

# 5. Train the model
python -m src.training.train --config configs/default.yaml

# 6. Check agent status
python -m learner.status
```

## CLI commands

| Command | Description |
|---|---|
| `python -m learner.resource_parser --input <path> --type <pdf\|web\|text>` | Parse a resource and extract knowledge |
| `python -m learner.evolve` | Run one evolution cycle (diff knowledge vs. code, generate patches) |
| `python -m learner.status` | Show current knowledge-base stats, model version, and pending improvements |
| `python -m src.training.train --config <yaml>` | Train the VL-JEPA model |
| `python -m src.evaluation.demo --image <path> --text <query>` | Run a vision-language retrieval demo |

## Project structure

```
yoda/
|-- README.md                  This file
|-- requirements.txt           Python dependencies
|-- knowledge/                 Agent's persistent knowledge store
|   |-- README.md              How the knowledge base works
|   |-- concepts.md            Core JEPA / VL-JEPA concepts
|   |-- architecture.md        Model architecture details
|   |-- training_insights.md   Hyperparameters and training tricks
|   |-- datasets.md            Dataset descriptions and notes
|   +-- evolution_log.md       Chronological record of every evolution
|-- learner/                   Agent brain (ingestion + evolution)
|   |-- __init__.py
|   +-- resource_parser.py     Parse PDFs, web pages, and text files
|-- src/                       Model source code (evolved by agent)
|   |-- __init__.py
|   |-- models/                VL-JEPA model definitions
|   |-- training/              Training loops, losses, schedulers
|   +-- evaluation/            Metrics, probing, and demos
+-- notebooks/                 Exploration and visualization notebooks
```

## How evolution works

Each evolution cycle proceeds through four stages:

1. **Knowledge delta** -- The evolver compares the current knowledge base against a snapshot taken at the last evolution. New entries are identified as the "delta."

2. **Impact analysis** -- For each delta entry, the evolver determines which source files are affected. For example, a new masking strategy insight maps to `src/training/` and `src/models/`.

3. **Patch generation** -- An LLM generates minimal, targeted code patches for each affected file. Patches are validated for syntax correctness before application.

4. **Logging** -- A new version entry is appended to `knowledge/evolution_log.md` documenting what changed, why, and which knowledge entries triggered it.

The agent never makes destructive changes. Each evolution creates a git-friendly diff that can be reviewed, accepted, or reverted.

## License

This project is provided for research and educational purposes. The ABO dataset used for training is licensed under CC BY-NC 4.0. Model weights derived from ABO data inherit that non-commercial restriction. See individual dataset licenses before commercial use.
