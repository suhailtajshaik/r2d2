# Architecture

## [2026-03-16 00:00] Source: Initial Knowledge (I-JEPA paper, Assran et al. 2023; VL-JEPA research)

### I-JEPA Base Architecture

- **Overall design**: Asymmetric encoder-predictor setup. A context encoder is trained via gradient descent while a target encoder is updated only through EMA -- no gradients flow into the target encoder. This asymmetry prevents representation collapse without requiring explicit negative pairs or architectural tricks like stop-gradient on only one branch.
- **Input pipeline**: Images are patchified into non-overlapping 16x16 pixel patches, linearly projected to the model dimension, and summed with learned positional embeddings. A subset of patches is masked before being fed to the context encoder.

### Vision Transformer (ViT) Encoder

- **ViT-Small/16**: 22M parameters, embedding dim 384, 6 heads, 12 transformer blocks, MLP ratio 4. Suitable for fast iteration and smaller datasets.
- **ViT-Base/16**: 86M parameters, embedding dim 768, 12 heads, 12 transformer blocks, MLP ratio 4. Recommended for production-quality representations.
- **Patch size**: 16x16 pixels. For a 224x224 image this yields 196 patches (14x14 grid). Smaller patch sizes (8x8) give finer granularity but quadratically increase sequence length and compute.
- **Positional encoding**: Learned absolute 2-D positional embeddings, one per patch position. These are shared between context and target encoders and are passed to the predictor so it knows *where* to predict.

### BERT Language Tower (VL-JEPA Extension)

- **Model**: `bert-base-uncased` (110M parameters, 768-dim, 12 layers, 12 heads). Chosen for its strong sentence-level representations and wide availability.
- **Frozen vs. fine-tuned**: During early pre-training the BERT tower is frozen to provide stable text targets. In later stages the top 4 layers can be unfrozen for task-specific adaptation.
- **[CLS] pooling**: The `[CLS]` token output serves as the global text representation, projected into the shared embedding space via a text projection head.

### Predictor Network

- **Type**: Lightweight transformer (4 blocks, same model dimension as the encoder, 6 heads for Small / 12 heads for Base).
- **Cross-attention mechanism**: The predictor receives context encoder outputs as keys/values and learned mask tokens (one per target patch position) as queries. Positional embeddings of the target positions are added to the mask tokens so the predictor knows which locations to predict.
- **Output**: One embedding per target position, trained to match the corresponding target encoder output.

### Projection Heads

- **Vision projection**: 2-layer MLP (hidden dim 2048, GELU activation, output dim 256) mapping ViT `[CLS]` or mean-pooled patch output to the shared embedding space.
- **Text projection**: 2-layer MLP (hidden dim 2048, GELU activation, output dim 256) mapping BERT `[CLS]` output to the same shared space.
- **L2 normalization**: Both projections are L2-normalized before the contrastive loss, placing all embeddings on a unit hypersphere.

### Asymmetric Architecture Summary

| Component | Trained by | Purpose |
|---|---|---|
| Context Encoder (ViT) | Gradient descent | Encode visible patches |
| Target Encoder (ViT) | EMA of context encoder | Provide prediction targets |
| Predictor | Gradient descent | Predict target embeddings from context |
| BERT Language Tower | Frozen / partial fine-tune | Encode text descriptions |
| Vision Projection Head | Gradient descent | Map vision to shared space |
| Text Projection Head | Gradient descent | Map text to shared space |


## [2026-03-16 07:01] Source: VL-JEPA Reading List — 5 Paper Summaries (Suhail's notes)

- (Google Brain) Link: https://arxiv.org/abs/1706.03762 Read: Sections 1, 2, 3, and Figure 1 only. Skip
the machine translation experiments. Time: 30–45 minutes
Why You Need This
Every model in this list — ViT, CLIP, JEPA — is built on the Transformer. If you don't understand attention, nothing else will
make sense. This is the foundation of modern AI.
- Example: "The animal didn't cross the street because it was too tired." - What does "it" refer to? The animal. - Self-attention
figures this out by letting "it" attend strongly to "animal" and weakly to "street."
How attention works (simplified): For each word, you create three vectors: - Query (Q): "What am I looking for?" - Key (K):
"What do I contain?" - Value (V): "What information do I pass along?"
Attention score = Q × K (dot product) Higher score = more attention = more information flows
Then: Output = weighted sum of all Values, weighted by attention scores
Why it matters for VL-JEPA: The Transformer's attention mechanism is the engine inside: - The Vision Encoder (reads image
patches) - The Language Encoder (reads text tokens) - The Predictor (predicts missing representations)
What changed after this paper: Every major AI model since 2017 — GPT, BERT, Claude, ViT, CLIP, DALL-E, JEPA — is built
on this architecture. It's the most important paper in modern AI history. Key Equations (Don't Fear Them)
Attention(Q, K, V) = softmax(QK^T / sqrt(d_k)) × V
Where:
- Q = query matrix
- K = key matrix  
- V = value matrix
- d_k = dimension of keys (scaling factor to prevent vanishing gradients)
- softmax = converts scores to probabilities (sum to 1)
Mental model: Imagine a library.
- V is the content inside each book. You

search for relevant books (Q·K), then read the relevant ones (weighted V). Paper 2: An Image is Worth 16x16 Words (ViT, 2020)
Authors: Dosovitskiy et al. (Google Brain) Link: https://arxiv.org/abs/2010.11929 Read: Sections 1, 2, 3 and Figure 1. Skip
sections 4–6 (experiments).
- (Google Brain) Link: https://arxiv.org/abs/2010.11929 Read: Sections 1, 2, 3 and Figure 1. Skip
sections 4–6 (experiments). Time: 30 minutes
Why You Need This
VL-JEPA's vision encoder IS a Vision Transformer. You need to understand how images are turned into sequences that a
Transformer can process. This is the bridge between pixels and attention.
- You need to understand how images are turned into sequences that a
Transformer can process. This is the bridge between pixels and attention. Plain English Summary
The problem it solved: Before ViT, images were processed by Convolutional Neural Networks (CNNs). CNNs are good but
have inductive biases — they assume nearby pixels matter more than distant ones. Transformers make no such assumption —
but transformers need sequences, not 2D grids.
- Transformers make no such assumption —
but transformers need sequences, not 2D grids. How do you feed an image to a Transformer? The big idea — Patch Embeddings: Cut the image into small fixed-size patches. Treat each patch like a word. Feed the
sequence of patches into a standard Transformer.
- Flatten each
patch into a vector: 16 × 16 × 3 (RGB) = 768 numbers 4. Project each 768-number vector into a 768-dimensional embedding
(one linear layer) 5. Add positional encoding (so the model knows patch #1 is top-left, patch #196 is bottom-right) 6. Feed 196
patch embeddings into a standard Transformer 7. The Transformer produces 196 output embeddings — one per patch 8.
- Project each 768-number vector into a 768-dimensional embedding
(one linear layer) 5. Add positional encoding (so the model knows patch #1 is top-left, patch #196 is bottom-right) 6. Feed 196
patch embeddings into a standard Transformer 7. The Transformer produces 196 output embeddings — one per patch 8. Add a
special [CLS] token at position 0 → its output embedding = the whole image representation
What the model learns: Without any explicit instruction, ViT learns to attend to semantically meaningful regions.
- Feed 196
patch embeddings into a standard Transformer 7. The Transformer produces 196 output embeddings — one per patch 8. Add a
special [CLS] token at position 0 → its output embedding = the whole image representation
What the model learns: Without any explicit instruction, ViT learns to attend to semantically meaningful regions. Show it a
dog → it attends to the dog's face and paws. Show it a shelf → it attends to the products, not the background.
- Show it a
dog → it attends to the dog's face and paws. Show it a shelf → it attends to the products, not the background. Why it matters for VL-JEPA: - VL-JEPA uses a ViT as its Context Encoder AND Target Encoder - The 196 patch embeddings
are exactly what gets masked, predicted, and compared - The [CLS] token embedding is what gets aligned with text descriptions
Key insight: The model has no built-in knowledge that pixels next to each other are related. It learns this from data. This makes
it more flexible than CNNs — it can learn any spatial relationship, not just local ones.


## [2026-03-16 07:01] Source: VL-JEPA Learning Path — Senior ML Researcher structured guide

- Learner profile: Suhail is a software engineer with Python experience but limited ML
theory background. He learns best through plain-English explanations, concrete
analogies, and visual mental models — not dense math. End goal: By the end of 2 weeks, Suhail can explain every architectural component of VL-
JEPA (context encoder, target encoder, predictor, language tower, cross-modal alignment)
without referencing any notes. Scope: 5 core papers + 2 bonus papers, in dependency order. Each paper builds on the last.
- Papers to cover (in order):
1. Attention Is All You Need — Vaswani et al., 2017
2. An Image is Worth 16x16 Words (ViT) — Dosovitskiy et al., 2020
3. CLIP: Learning Transferable Visual Models From Natural Language Supervision —
Radford et al., 2021
4. Masked Autoencoders Are Scalable Vision Learners (MAE) — He et al., 2021
5.
- I-JEPA

For each bonus paper, provide: title, link, sections to read, estimated time, and a "Why It's
Relevant" paragraph (3–5 sentences max). No full summary needed. Produce a day-by-day schedule as a markdown table with columns: Day | Paper | Task | Focus
Activity. Week 1: Foundations (Papers 1–3)
Week 2: Self-Supervised Learning + JEPA (Papers 4–5 + Bonus)
Include one review/rest day per week
Each "Focus Activity" should be a single actionable task (e.g., "Implement scaled dot-product
attention in NumPy — no libraries")
Produce a two-column markdown table: Concept | One-Line Definition
Include at minimum these 14 terms:
Embedding, Attention, Transformer, ViT, Self-supervised learning, Contrastive learning, MAE,
JEPA, EMA, Predictor, Cross-modal alignment, VL-JEPA, Zero-shot, Fine-tuning
Produce a numbered list of 8–10
Now I have all the research needed. Here is the complete, structured VL-JEPA learning path
document for Suhail.
- No full summary needed. Produce a day-by-day schedule as a markdown table with columns: Day | Paper | Task | Focus
Activity. Week 1: Foundations (Papers 1–3)
Week 2: Self-Supervised Learning + JEPA (Papers 4–5 + Bonus)
Include one review/rest day per week
Each "Focus Activity" should be a single actionable task (e.g., "Implement scaled dot-product
attention in NumPy — no libraries")
Produce a two-column markdown table: Concept | One-Line Definition
Include at minimum these 14 terms:
Embedding, Attention, Transformer, ViT, Self-supervised learning, Contrastive learning, MAE,
JEPA, EMA, Predictor, Cross-modal alignment, VL-JEPA, Zero-shot, Fine-tuning
Produce a numbered list of 8–10
Now I have all the research needed. Here is the complete, structured VL-JEPA learning path
document for Suhail. A 2-Week Guided Study Program for Suhail
By: Senior ML Researcher & Technical Educator | Built specifically for software engineers entering
deep learning
Your North Star: In 14 days, you will be able to whiteboard every component of VL-JEPA
— context encoder, target encoder, predictor, language tower, and cross-modal
alignment — without notes.
- Week 1: Foundations (Papers 1–3)
Week 2: Self-Supervised Learning + JEPA (Papers 4–5 + Bonus)
Include one review/rest day per week
Each "Focus Activity" should be a single actionable task (e.g., "Implement scaled dot-product
attention in NumPy — no libraries")
Produce a two-column markdown table: Concept | One-Line Definition
Include at minimum these 14 terms:
Embedding, Attention, Transformer, ViT, Self-supervised learning, Contrastive learning, MAE,
JEPA, EMA, Predictor, Cross-modal alignment, VL-JEPA, Zero-shot, Fine-tuning
Produce a numbered list of 8–10
Now I have all the research needed. Here is the complete, structured VL-JEPA learning path
document for Suhail. A 2-Week Guided Study Program for Suhail
By: Senior ML Researcher & Technical Educator | Built specifically for software engineers entering
deep learning
Your North Star: In 14 days, you will be able to whiteboard every component of VL-JEPA
— context encoder, target encoder, predictor, language tower, and cross-modal
alignment — without notes. Every paper below is a rung on that ladder. Skip one, and
you'll hit a conceptual gap you can't climb around.
- Authors: Ashish Vaswani, Noam Shazeer, Niki Parmar et al. Year: 2017
arXiv: arxiv.org/abs/1706.03762
Sections to Read: Abstract, Section 1 (Introduction), Section 3 (Model Architecture), Section 3.1–
3.3 (Attention mechanism), Figure 1 and Figure 2. Estimated Reading Time: 60–75 minutes
VL-JEPA's context encoder, target encoder, predictor, and language tower are all Transformer-
based. If you don't understand how attention works — how a model decides which parts of an
input to focus on — you'll be building VL-JEPA blindfolded. This is the paper that introduced the
Transformer architecture that now underlies virtually every modern AI model, including every
component you'll implement.
- Stack many Transformer blocks. Each block applies attention then a feed-forward
network, with residual connections and layer normalization throughout. Why it matters for VL-JEPA:
Every encoder in VL-JEPA is a Vision Transformer (ViT), which is a direct descendant of this
architecture applied to image patches instead of words. When the VL-JEPA predictor takes a
context patch's encoding and tries to predict what a masked target patch's encoding should
look like, it does so using exactly the attention mechanism described in this paper. The
language tower also uses a Transformer to encode text into the embeddings VL-JEPA predicts
against.
- Each block applies attention then a feed-forward
network, with residual connections and layer normalization throughout. Why it matters for VL-JEPA:
Every encoder in VL-JEPA is a Vision Transformer (ViT), which is a direct descendant of this
architecture applied to image patches instead of words. When the VL-JEPA predictor takes a
context patch's encoding and tries to predict what a masked target patch's encoding should
look like, it does so using exactly the attention mechanism described in this paper. The
language tower also uses a Transformer to encode text into the embeddings VL-JEPA predicts
against. Plain English Summary
[4]
[3]
[2] [1]

: Query matrix — what each token is "searching for" in the sequence
: Key matrix — what each token "advertises" about itself
: Value matrix — the actual information each token carries
: Dimensionality of key vectors — used for scaling to prevent tiny gradients
: Normalizes scores so they form a probability distribution summing to 1
Mental model: Think of Q as a search query in Google, K as webpage titles, and V as the actual
webpage content — attention is the search engine deciding which pages to read and how much
of each to blend into your answer.
- That's computationally insane. The
next paper solves this by treating an image as a sequence of patches instead. INPUT TOKENS:  [The]  [cat]  [sat]  [on]  [mat]
                 ↓      ↓      ↓     ↓      ↓
              Embed → Q,K,V for each token
                         ↓
              ┌─────────────────────────────┐
              │   ATTENTION: Every token    │
              │   looks at every other      │
              │   token simultaneously      │
              └─────────────────────────────┘
                         ↓
              New contextual representations
              [The*] [cat*] [sat*] [on*] [mat*]
                         ↓
              Feed-Forward Network (per token)
                         ↓
              OUTPUT: Enriched token embeddings
Key Equation
Limitation / What Comes Next
[3]
Mental Model Diagram

Authors: Alexey Dosovitskiy, Lucas Beyer, Alexander Kolesnikov et al. Year: 2020
arXiv: arxiv.org/abs/2010.11929
Sections to Read: Abstract, Section 1, Section 3 (Method) — especially the patch embedding and
position encoding parts. Figure 1 is essential.
- The
next paper solves this by treating an image as a sequence of patches instead. INPUT TOKENS:  [The]  [cat]  [sat]  [on]  [mat]
                 ↓      ↓      ↓     ↓      ↓
              Embed → Q,K,V for each token
                         ↓
              ┌─────────────────────────────┐
              │   ATTENTION: Every token    │
              │   looks at every other      │
              │   token simultaneously      │
              └─────────────────────────────┘
                         ↓
              New contextual representations
              [The*] [cat*] [sat*] [on*] [mat*]
                         ↓
              Feed-Forward Network (per token)
                         ↓
              OUTPUT: Enriched token embeddings
Key Equation
Limitation / What Comes Next
[3]
Mental Model Diagram

Authors: Alexey Dosovitskiy, Lucas Beyer, Alexander Kolesnikov et al. Year: 2020
arXiv: arxiv.org/abs/2010.11929
Sections to Read: Abstract, Section 1, Section 3 (Method) — especially the patch embedding and
position encoding parts. Figure 1 is essential. Estimated Reading Time: 50–60 minutes
VL-JEPA's context encoder and target encoder are both Vision Transformers (ViTs).


## [2026-03-16 07:03] Source: VL-JEPA Reading List — 5 Paper Summaries (Suhail's notes)

- (Google Brain) Link: https://arxiv.org/abs/1706.03762 Read: Sections 1, 2, 3, and Figure 1 only. Skip
the machine translation experiments. Time: 30–45 minutes
Why You Need This
Every model in this list — ViT, CLIP, JEPA — is built on the Transformer. If you don't understand attention, nothing else will
make sense. This is the foundation of modern AI.
- Example: "The animal didn't cross the street because it was too tired." - What does "it" refer to? The animal. - Self-attention
figures this out by letting "it" attend strongly to "animal" and weakly to "street."
How attention works (simplified): For each word, you create three vectors: - Query (Q): "What am I looking for?" - Key (K):
"What do I contain?" - Value (V): "What information do I pass along?"
Attention score = Q × K (dot product) Higher score = more attention = more information flows
Then: Output = weighted sum of all Values, weighted by attention scores
Why it matters for VL-JEPA: The Transformer's attention mechanism is the engine inside: - The Vision Encoder (reads image
patches) - The Language Encoder (reads text tokens) - The Predictor (predicts missing representations)
What changed after this paper: Every major AI model since 2017 — GPT, BERT, Claude, ViT, CLIP, DALL-E, JEPA — is built
on this architecture. It's the most important paper in modern AI history. Key Equations (Don't Fear Them)
Attention(Q, K, V) = softmax(QK^T / sqrt(d_k)) × V
Where:
- Q = query matrix
- K = key matrix  
- V = value matrix
- d_k = dimension of keys (scaling factor to prevent vanishing gradients)
- softmax = converts scores to probabilities (sum to 1)
Mental model: Imagine a library.
- V is the content inside each book. You

search for relevant books (Q·K), then read the relevant ones (weighted V). Paper 2: An Image is Worth 16x16 Words (ViT, 2020)
Authors: Dosovitskiy et al. (Google Brain) Link: https://arxiv.org/abs/2010.11929 Read: Sections 1, 2, 3 and Figure 1. Skip
sections 4–6 (experiments).
- (Google Brain) Link: https://arxiv.org/abs/2010.11929 Read: Sections 1, 2, 3 and Figure 1. Skip
sections 4–6 (experiments). Time: 30 minutes
Why You Need This
VL-JEPA's vision encoder IS a Vision Transformer. You need to understand how images are turned into sequences that a
Transformer can process. This is the bridge between pixels and attention.
- You need to understand how images are turned into sequences that a
Transformer can process. This is the bridge between pixels and attention. Plain English Summary
The problem it solved: Before ViT, images were processed by Convolutional Neural Networks (CNNs). CNNs are good but
have inductive biases — they assume nearby pixels matter more than distant ones. Transformers make no such assumption —
but transformers need sequences, not 2D grids.
- Transformers make no such assumption —
but transformers need sequences, not 2D grids. How do you feed an image to a Transformer? The big idea — Patch Embeddings: Cut the image into small fixed-size patches. Treat each patch like a word. Feed the
sequence of patches into a standard Transformer.
- Flatten each
patch into a vector: 16 × 16 × 3 (RGB) = 768 numbers 4. Project each 768-number vector into a 768-dimensional embedding
(one linear layer) 5. Add positional encoding (so the model knows patch #1 is top-left, patch #196 is bottom-right) 6. Feed 196
patch embeddings into a standard Transformer 7. The Transformer produces 196 output embeddings — one per patch 8.
- Project each 768-number vector into a 768-dimensional embedding
(one linear layer) 5. Add positional encoding (so the model knows patch #1 is top-left, patch #196 is bottom-right) 6. Feed 196
patch embeddings into a standard Transformer 7. The Transformer produces 196 output embeddings — one per patch 8. Add a
special [CLS] token at position 0 → its output embedding = the whole image representation
What the model learns: Without any explicit instruction, ViT learns to attend to semantically meaningful regions.
- Feed 196
patch embeddings into a standard Transformer 7. The Transformer produces 196 output embeddings — one per patch 8. Add a
special [CLS] token at position 0 → its output embedding = the whole image representation
What the model learns: Without any explicit instruction, ViT learns to attend to semantically meaningful regions. Show it a
dog → it attends to the dog's face and paws. Show it a shelf → it attends to the products, not the background.
- Show it a
dog → it attends to the dog's face and paws. Show it a shelf → it attends to the products, not the background. Why it matters for VL-JEPA: - VL-JEPA uses a ViT as its Context Encoder AND Target Encoder - The 196 patch embeddings
are exactly what gets masked, predicted, and compared - The [CLS] token embedding is what gets aligned with text descriptions
Key insight: The model has no built-in knowledge that pixels next to each other are related. It learns this from data. This makes
it more flexible than CNNs — it can learn any spatial relationship, not just local ones.


## [2026-03-16 07:03] Source: VL-JEPA Learning Path — Senior ML Researcher structured guide

- Learner profile: Suhail is a software engineer with Python experience but limited ML
theory background. He learns best through plain-English explanations, concrete
analogies, and visual mental models — not dense math. End goal: By the end of 2 weeks, Suhail can explain every architectural component of VL-
JEPA (context encoder, target encoder, predictor, language tower, cross-modal alignment)
without referencing any notes. Scope: 5 core papers + 2 bonus papers, in dependency order. Each paper builds on the last.
- Papers to cover (in order):
1. Attention Is All You Need — Vaswani et al., 2017
2. An Image is Worth 16x16 Words (ViT) — Dosovitskiy et al., 2020
3. CLIP: Learning Transferable Visual Models From Natural Language Supervision —
Radford et al., 2021
4. Masked Autoencoders Are Scalable Vision Learners (MAE) — He et al., 2021
5.
- I-JEPA

For each bonus paper, provide: title, link, sections to read, estimated time, and a "Why It's
Relevant" paragraph (3–5 sentences max). No full summary needed. Produce a day-by-day schedule as a markdown table with columns: Day | Paper | Task | Focus
Activity. Week 1: Foundations (Papers 1–3)
Week 2: Self-Supervised Learning + JEPA (Papers 4–5 + Bonus)
Include one review/rest day per week
Each "Focus Activity" should be a single actionable task (e.g., "Implement scaled dot-product
attention in NumPy — no libraries")
Produce a two-column markdown table: Concept | One-Line Definition
Include at minimum these 14 terms:
Embedding, Attention, Transformer, ViT, Self-supervised learning, Contrastive learning, MAE,
JEPA, EMA, Predictor, Cross-modal alignment, VL-JEPA, Zero-shot, Fine-tuning
Produce a numbered list of 8–10
Now I have all the research needed. Here is the complete, structured VL-JEPA learning path
document for Suhail.
- No full summary needed. Produce a day-by-day schedule as a markdown table with columns: Day | Paper | Task | Focus
Activity. Week 1: Foundations (Papers 1–3)
Week 2: Self-Supervised Learning + JEPA (Papers 4–5 + Bonus)
Include one review/rest day per week
Each "Focus Activity" should be a single actionable task (e.g., "Implement scaled dot-product
attention in NumPy — no libraries")
Produce a two-column markdown table: Concept | One-Line Definition
Include at minimum these 14 terms:
Embedding, Attention, Transformer, ViT, Self-supervised learning, Contrastive learning, MAE,
JEPA, EMA, Predictor, Cross-modal alignment, VL-JEPA, Zero-shot, Fine-tuning
Produce a numbered list of 8–10
Now I have all the research needed. Here is the complete, structured VL-JEPA learning path
document for Suhail. A 2-Week Guided Study Program for Suhail
By: Senior ML Researcher & Technical Educator | Built specifically for software engineers entering
deep learning
Your North Star: In 14 days, you will be able to whiteboard every component of VL-JEPA
— context encoder, target encoder, predictor, language tower, and cross-modal
alignment — without notes.
- Week 1: Foundations (Papers 1–3)
Week 2: Self-Supervised Learning + JEPA (Papers 4–5 + Bonus)
Include one review/rest day per week
Each "Focus Activity" should be a single actionable task (e.g., "Implement scaled dot-product
attention in NumPy — no libraries")
Produce a two-column markdown table: Concept | One-Line Definition
Include at minimum these 14 terms:
Embedding, Attention, Transformer, ViT, Self-supervised learning, Contrastive learning, MAE,
JEPA, EMA, Predictor, Cross-modal alignment, VL-JEPA, Zero-shot, Fine-tuning
Produce a numbered list of 8–10
Now I have all the research needed. Here is the complete, structured VL-JEPA learning path
document for Suhail. A 2-Week Guided Study Program for Suhail
By: Senior ML Researcher & Technical Educator | Built specifically for software engineers entering
deep learning
Your North Star: In 14 days, you will be able to whiteboard every component of VL-JEPA
— context encoder, target encoder, predictor, language tower, and cross-modal
alignment — without notes. Every paper below is a rung on that ladder. Skip one, and
you'll hit a conceptual gap you can't climb around.
- Authors: Ashish Vaswani, Noam Shazeer, Niki Parmar et al. Year: 2017
arXiv: arxiv.org/abs/1706.03762
Sections to Read: Abstract, Section 1 (Introduction), Section 3 (Model Architecture), Section 3.1–
3.3 (Attention mechanism), Figure 1 and Figure 2. Estimated Reading Time: 60–75 minutes
VL-JEPA's context encoder, target encoder, predictor, and language tower are all Transformer-
based. If you don't understand how attention works — how a model decides which parts of an
input to focus on — you'll be building VL-JEPA blindfolded. This is the paper that introduced the
Transformer architecture that now underlies virtually every modern AI model, including every
component you'll implement.
- Stack many Transformer blocks. Each block applies attention then a feed-forward
network, with residual connections and layer normalization throughout. Why it matters for VL-JEPA:
Every encoder in VL-JEPA is a Vision Transformer (ViT), which is a direct descendant of this
architecture applied to image patches instead of words. When the VL-JEPA predictor takes a
context patch's encoding and tries to predict what a masked target patch's encoding should
look like, it does so using exactly the attention mechanism described in this paper. The
language tower also uses a Transformer to encode text into the embeddings VL-JEPA predicts
against.
- Each block applies attention then a feed-forward
network, with residual connections and layer normalization throughout. Why it matters for VL-JEPA:
Every encoder in VL-JEPA is a Vision Transformer (ViT), which is a direct descendant of this
architecture applied to image patches instead of words. When the VL-JEPA predictor takes a
context patch's encoding and tries to predict what a masked target patch's encoding should
look like, it does so using exactly the attention mechanism described in this paper. The
language tower also uses a Transformer to encode text into the embeddings VL-JEPA predicts
against. Plain English Summary
[4]
[3]
[2] [1]

: Query matrix — what each token is "searching for" in the sequence
: Key matrix — what each token "advertises" about itself
: Value matrix — the actual information each token carries
: Dimensionality of key vectors — used for scaling to prevent tiny gradients
: Normalizes scores so they form a probability distribution summing to 1
Mental model: Think of Q as a search query in Google, K as webpage titles, and V as the actual
webpage content — attention is the search engine deciding which pages to read and how much
of each to blend into your answer.
- That's computationally insane. The
next paper solves this by treating an image as a sequence of patches instead. INPUT TOKENS:  [The]  [cat]  [sat]  [on]  [mat]
                 ↓      ↓      ↓     ↓      ↓
              Embed → Q,K,V for each token
                         ↓
              ┌─────────────────────────────┐
              │   ATTENTION: Every token    │
              │   looks at every other      │
              │   token simultaneously      │
              └─────────────────────────────┘
                         ↓
              New contextual representations
              [The*] [cat*] [sat*] [on*] [mat*]
                         ↓
              Feed-Forward Network (per token)
                         ↓
              OUTPUT: Enriched token embeddings
Key Equation
Limitation / What Comes Next
[3]
Mental Model Diagram

Authors: Alexey Dosovitskiy, Lucas Beyer, Alexander Kolesnikov et al. Year: 2020
arXiv: arxiv.org/abs/2010.11929
Sections to Read: Abstract, Section 1, Section 3 (Method) — especially the patch embedding and
position encoding parts. Figure 1 is essential.
- The
next paper solves this by treating an image as a sequence of patches instead. INPUT TOKENS:  [The]  [cat]  [sat]  [on]  [mat]
                 ↓      ↓      ↓     ↓      ↓
              Embed → Q,K,V for each token
                         ↓
              ┌─────────────────────────────┐
              │   ATTENTION: Every token    │
              │   looks at every other      │
              │   token simultaneously      │
              └─────────────────────────────┘
                         ↓
              New contextual representations
              [The*] [cat*] [sat*] [on*] [mat*]
                         ↓
              Feed-Forward Network (per token)
                         ↓
              OUTPUT: Enriched token embeddings
Key Equation
Limitation / What Comes Next
[3]
Mental Model Diagram

Authors: Alexey Dosovitskiy, Lucas Beyer, Alexander Kolesnikov et al. Year: 2020
arXiv: arxiv.org/abs/2010.11929
Sections to Read: Abstract, Section 1, Section 3 (Method) — especially the patch embedding and
position encoding parts. Figure 1 is essential. Estimated Reading Time: 50–60 minutes
VL-JEPA's context encoder and target encoder are both Vision Transformers (ViTs).


## [2026-03-16 07:03] Source: Suhail's Research Summary + Mind Map

- Unlike traditional generative models—such as Masked Autoencoders (MAEs) or Large Language Models (LLMs)—that waste massive computational capacity trying to reconstruct irrelevant surface-level noise or specific word choices, JEPA focuses entirely on predicting high-level representations in a latent space. The Core Architecture:
The JEPA framework teaches AI to "imagine what's missing" by utilizing three main components:
1. Context Encoder: A neural network (often built on Transformer self-attention mechanisms) that processes the visible, known input to extract its essential structure into a "context embedding". 2. Target Encoder: A parallel network that processes the hidden, missing, or future data to create a "ground truth" embedding.
- Context Encoder: A neural network (often built on Transformer self-attention mechanisms) that processes the visible, known input to extract its essential structure into a "context embedding". 2. Target Encoder: A parallel network that processes the hidden, missing, or future data to create a "ground truth" embedding. To prevent "representation collapse"—a failure mode where the model lazily outputs constants to minimize loss—the target encoder's weights are typically updated using a slow Exponential Moving Average (EMA) of the context encoder, making it a moving target. 3.
- 2. Target Encoder: A parallel network that processes the hidden, missing, or future data to create a "ground truth" embedding. To prevent "representation collapse"—a failure mode where the model lazily outputs constants to minimize loss—the target encoder's weights are typically updated using a slow Exponential Moving Average (EMA) of the context encoder, making it a moving target. 3. Predictor: A lightweight module that takes the context embedding—and occasionally a latent variable to account for multiple plausible future outcomes (uncertainty)—and attempts to predict the target embedding.
- To prevent "representation collapse"—a failure mode where the model lazily outputs constants to minimize loss—the target encoder's weights are typically updated using a slow Exponential Moving Average (EMA) of the context encoder, making it a moving target. 3. Predictor: A lightweight module that takes the context embedding—and occasionally a latent variable to account for multiple plausible future outcomes (uncertainty)—and attempts to predict the target embedding. The model is trained by minimizing the distance (or "energy") between the predicted and true target embeddings using contrastive or regularized loss functions. Key Variants and Capabilities:
- I-JEPA (Images): Predicts the embeddings of missing image blocks from a visible context block.
- This yields up to 2.85x faster inference with 50% fewer parameters. - Domain Extensions: V-JEPA (video), T-JEPA (tabular data), EchoJEPA (medical imaging/echocardiography). Mind Map - Full Architecture:
Core Concepts: World Modeling, Latent Space Prediction, Abstract Representation, Self-Supervised Learning
System Architecture Core Modules: Context Encoder, Target Encoder, Predictor Network, Configurator
System Architecture Support Modules: Cost Module (Intrinsic & Critic), Actor, Short-Term Memory
Implementation Variants: I-JEPA (Masked Patch Prediction, Semantic Feature Alignment), V-JEPA (Motion Understanding, Action Anticipation), VL-JEPA (Continuous Embedding Prediction, Selective Decoding, Discriminative VQA)
Key Advantages: Computational Efficiency, Robustness to Noise, Avoidance of Representation Collapse, Hierarchical Planning Capability
Training Paradigms: Non-Contrastive SSL, VICReg (Variance-Invariance-Covariance), InfoNCE Loss, Momentum Encoders
Challenges Addressed: Handling Uncertainty, Common Sense Acquisition, Multi-scale Abstraction, Sample Inefficiency

The Ultimate Goal:
Rooted in Yann LeCun's vision for autonomous machine intelligence, JEPA serves as a foundational world model engine. Theoretical analyses show that JEPA inherently prioritizes learning "influential features" while ignoring noisy, uninformative data. This allows AI systems to efficiently understand environments, predict how the world will evolve, and reason continuously in latent space before ever translating those thoughts into language or actions.


## [2026-03-16 07:03] JEPA Full Mind Map (from Suhail)

### System Architecture
- **Core Modules:** Context Encoder, Target Encoder, Predictor Network, Configurator
- **Support Modules:** Cost Module (Intrinsic & Critic), Actor, Short-Term Memory

### Implementation Variants
- **I-JEPA:** Masked Patch Prediction, Semantic Feature Alignment
- **V-JEPA:** Motion Understanding, Action Anticipation
- **VL-JEPA:** Continuous Embedding Prediction, Selective Decoding, Discriminative VQA

### Key Advantages
- Computational Efficiency, Robustness to Noise, Avoidance of Representation Collapse, Hierarchical Planning Capability

### Training Paradigms
- Non-Contrastive SSL, VICReg (Variance-Invariance-Covariance), InfoNCE Loss, Momentum Encoders

### Challenges Addressed
- Handling Uncertainty, Common Sense Acquisition, Multi-scale Abstraction, Sample Inefficiency
