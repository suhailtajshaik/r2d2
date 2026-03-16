# Evolution Log

## v0.1 — 2026-03-16 00:00
**Trigger:** Yoda v0.1 — Initial scaffold built from I-JEPA paper + VL-JEPA research. Named Yoda by Suhail.
**Changes:**
- Built complete VL-JEPA model architecture (ViT encoder, BERT language tower, predictor)
- Implemented JEPA predictive loss + cross-modal alignment loss
- Created block masking strategy
- Set up training loop with EMA updates
- Built learner pipeline (resource parser, knowledge extractor, code evolver)
- Seeded knowledge base with I-JEPA and VL-JEPA research insights

**Reason:** Foundation scaffold based on I-JEPA paper (Assran et al., 2023) and VL-JEPA research for vision-language self-supervised learning


## [2026-03-16 07:01] Learning Event
**Source:** VL-JEPA Reading List — 5 Paper Summaries (Suhail's notes)
**Content size:** 20,570 chars
**Concepts extracted:** 10
**Architecture insights:** 10
**Code improvements suggested:** 3
**Improvements:**
- Consider using multi-block rectangular masking instead of random patch masking in src/training/masking.py
- Verify EMA momentum is set to 0.996 and updates correctly in src/models/vl_jepa.py
- Cross-modal alignment loss in src/training/losses.py should use InfoNCE/NT-Xent formulation


## [2026-03-16 07:01] Learning Event
**Source:** VL-JEPA Learning Path — Senior ML Researcher structured guide
**Content size:** 44,362 chars
**Concepts extracted:** 10
**Architecture insights:** 10
**Code improvements suggested:** 4
**Improvements:**
- Consider using multi-block rectangular masking instead of random patch masking in src/training/masking.py
- Verify EMA momentum is set to 0.996 and updates correctly in src/models/vl_jepa.py
- Cross-modal alignment loss in src/training/losses.py should use InfoNCE/NT-Xent formulation
- Ensure LayerNorm is applied before attention (pre-norm) in all transformer blocks


## [2026-03-16 07:03] Learning Event
**Source:** VL-JEPA Reading List — 5 Paper Summaries (Suhail's notes)
**Content size:** 20,570 chars
**Concepts extracted:** 10
**Architecture insights:** 10
**Code improvements suggested:** 3
**Improvements:**
- Consider using multi-block rectangular masking instead of random patch masking in src/training/masking.py
- Verify EMA momentum is set to 0.996 and updates correctly in src/models/vl_jepa.py
- Cross-modal alignment loss in src/training/losses.py should use InfoNCE/NT-Xent formulation


## [2026-03-16 07:03] Learning Event
**Source:** VL-JEPA Learning Path — Senior ML Researcher structured guide
**Content size:** 44,362 chars
**Concepts extracted:** 10
**Architecture insights:** 10
**Code improvements suggested:** 4
**Improvements:**
- Consider using multi-block rectangular masking instead of random patch masking in src/training/masking.py
- Verify EMA momentum is set to 0.996 and updates correctly in src/models/vl_jepa.py
- Cross-modal alignment loss in src/training/losses.py should use InfoNCE/NT-Xent formulation
- Ensure LayerNorm is applied before attention (pre-norm) in all transformer blocks


## [2026-03-16 07:03] Major Learning Event — Suhail's Research Summary
**Source:** Suhail's personal JEPA research summary + NotebookLM mind map
**Key new knowledge:**
- VL-JEPA: 2.85x faster inference, 50% fewer parameters
- Selective decoding mechanism — only decode when scene semantics change
- Support modules: Cost Module, Actor, Short-Term Memory (world model components)
- Training: VICReg, Non-Contrastive SSL as alternatives to InfoNCE
- Domain variants: T-JEPA (tabular), EchoJEPA (medical imaging)
- Authors: Delong Chen, Mustafa Shukor, Yann LeCun, Pascale Fung (Dec 2025)


## [2026-03-16] v0.3 — Architecture upgrade from Suhail research + mind map
**Trigger:** Suhail shared research summary, mind map (NotebookLM), and 2 PDFs
**Changes:**
- Added SelectiveDecoder (2.85x inference speedup mechanism)
- Added CostModule (intrinsic + critic costs for world model planning)
- Added ShortTermMemory (temporal embedding buffer)
- Added VICReg loss alternative to InfoNCE
- Added MultiBlockMasking (rectangular, 4 blocks, ~50% coverage)
- Added JEPAConfig dataclass (Configurator from mind map)
**Knowledge gained:** Full JEPA architecture including support modules, selective decoding, VICReg training
