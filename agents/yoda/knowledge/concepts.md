# Core Concepts

## [2026-03-16 00:00] Source: Initial Knowledge (I-JEPA paper, VL-JEPA research)

- **Joint-Embedding Predictive Architecture (JEPA)**: A self-supervised learning framework that predicts representations of target signals from context signals in embedding space, rather than pixel/token space
- **Predictive Coding in Embedding Space**: Unlike MAE which reconstructs pixels, JEPA predicts abstract representations, encouraging semantic understanding over low-level details
- **Context Encoder**: Processes visible (unmasked) patches to produce context representations
- **Target Encoder**: Processes all patches to produce target representations; updated via Exponential Moving Average (EMA) of context encoder weights
- **Predictor Network**: A lightweight transformer that takes context embeddings and target position information to predict target embeddings
- **EMA (Exponential Moving Average)**: Target encoder weights are a slow-moving average of context encoder weights (momentum ~0.996), providing stable training targets
- **Patch Masking**: Input images are divided into patches (16x16); a subset is masked and must be predicted from the visible context
- **Self-Supervised Pre-training**: No labels needed; the model learns by predicting its own representations
- **Vision-Language Alignment**: Extending I-JEPA to multimodal by aligning visual and textual representations in a shared embedding space
- **Contrastive Learning**: InfoNCE/NT-Xent losses used to align image and text embeddings by pulling matched pairs together and pushing mismatched pairs apart


## [2026-03-16 07:01] Source: VL-JEPA Reading List — 5 Paper Summaries (Suhail's notes)

- The "Plain
English Summary" for each paper is what actually matters. Read the real paper after you understand the idea. Estimated total reading time: 6–10 hours across 2 weeks Papers: 5 core + 2 bonus Goal: By the end, you understand every
component of VL-JEPA before writing a line of code
Paper 1: Attention Is All You Need (2017)
Authors: Vaswani et al. (Google Brain) Link: https://arxiv.org/abs/1706.03762 Read: Sections 1, 2, 3, and Figure 1 only. Skip
the machine translation experiments.
- (Google Brain) Link: https://arxiv.org/abs/1706.03762 Read: Sections 1, 2, 3, and Figure 1 only. Skip
the machine translation experiments. Time: 30–45 minutes
Why You Need This
Every model in this list — ViT, CLIP, JEPA — is built on the Transformer. If you don't understand attention, nothing else will
make sense. This is the foundation of modern AI.
- Skip
the machine translation experiments. Time: 30–45 minutes
Why You Need This
Every model in this list — ViT, CLIP, JEPA — is built on the Transformer. If you don't understand attention, nothing else will
make sense. This is the foundation of modern AI. Plain English Summary
The problem it solved: Before 2017, the best models for language were Recurrent Neural Networks (RNNs).
- Problem: by the time you reached the end of a long sentence, the model had "forgotten" the
beginning. Like reading a book but forgetting chapter 1 by chapter 10. The big idea — Self-Attention: Instead of processing one word at a time, look at ALL words simultaneously and let each word
"attend to" every other word based on relevance. Example: "The animal didn't cross the street because it was too tired." - What does "it" refer to? The animal.
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
- - Self-attention
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
Mental model: Imagine a library. Q is your search query. K is the title of each book.
- (Google Brain) Link: https://arxiv.org/abs/2010.11929 Read: Sections 1, 2, 3 and Figure 1. Skip
sections 4–6 (experiments). Time: 30 minutes
Why You Need This
VL-JEPA's vision encoder IS a Vision Transformer. You need to understand how images are turned into sequences that a
Transformer can process. This is the bridge between pixels and attention.
- Skip
sections 4–6 (experiments). Time: 30 minutes
Why You Need This
VL-JEPA's vision encoder IS a Vision Transformer. You need to understand how images are turned into sequences that a
Transformer can process. This is the bridge between pixels and attention. Plain English Summary
The problem it solved: Before ViT, images were processed by Convolutional Neural Networks (CNNs).
- Time: 30 minutes
Why You Need This
VL-JEPA's vision encoder IS a Vision Transformer. You need to understand how images are turned into sequences that a
Transformer can process. This is the bridge between pixels and attention. Plain English Summary
The problem it solved: Before ViT, images were processed by Convolutional Neural Networks (CNNs). CNNs are good but
have inductive biases — they assume nearby pixels matter more than distant ones.
- Plain English Summary
The problem it solved: Before ViT, images were processed by Convolutional Neural Networks (CNNs). CNNs are good but
have inductive biases — they assume nearby pixels matter more than distant ones. Transformers make no such assumption —
but transformers need sequences, not 2D grids. How do you feed an image to a Transformer? The big idea — Patch Embeddings: Cut the image into small fixed-size patches.


## [2026-03-16 07:01] Source: VL-JEPA Learning Path — Senior ML Researcher structured guide

- Learner profile: Suhail is a software engineer with Python experience but limited ML
theory background. He learns best through plain-English explanations, concrete
analogies, and visual mental models — not dense math. End goal: By the end of 2 weeks, Suhail can explain every architectural component of VL-
JEPA (context encoder, target encoder, predictor, language tower, cross-modal alignment)
without referencing any notes. Scope: 5 core papers + 2 bonus papers, in dependency order. Each paper builds on the last.
- Total reading time: 6–10 hours across 2 weeks. Papers to cover (in order):
1. Attention Is All You Need — Vaswani et al., 2017
2. An Image is Worth 16x16 Words (ViT) — Dosovitskiy et al., 2020
3. CLIP: Learning Transferable Visual Models From Natural Language Supervision —
Radford et al., 2021
4.
- An Image is Worth 16x16 Words (ViT) — Dosovitskiy et al., 2020
3. CLIP: Learning Transferable Visual Models From Natural Language Supervision —
Radford et al., 2021
4. Masked Autoencoders Are Scalable Vision Learners (MAE) — He et al., 2021
5. Self-Supervised Learning from Images with a Joint-Embedding Predictive Architecture (I-
JEPA) — Assran et al., 2023
Bonus 1: DINOv2 — Oquab et al., 2023
Bonus 2: CLIP deep-dive (re-read Section 3.2)
# Role
Objective
Context

For each of the 5 core papers, produce a section containing exactly these components in this
order:
Header: Paper number, full title, authors, year, arXiv link, sections to read, estimated reading
time
Why You Need This (2–3 sentences)
Explain how this paper connects to VL-JEPA and why skipping it would create a knowledge gap. Plain English Summary (the most important section)
Cover these four points using plain language, short paragraphs, and concrete analogies:
The problem it solved (what was broken before this paper)
The core idea (one big insight explained simply)
How it works step by step (numbered, no jargon unless immediately defined)
Why it matters for VL-JEPA (explicit connection to the architecture Suhail is building)
Key Equation (one equation maximum)
Show the single most important equation.
- CLIP: Learning Transferable Visual Models From Natural Language Supervision —
Radford et al., 2021
4. Masked Autoencoders Are Scalable Vision Learners (MAE) — He et al., 2021
5. Self-Supervised Learning from Images with a Joint-Embedding Predictive Architecture (I-
JEPA) — Assran et al., 2023
Bonus 1: DINOv2 — Oquab et al., 2023
Bonus 2: CLIP deep-dive (re-read Section 3.2)
# Role
Objective
Context

For each of the 5 core papers, produce a section containing exactly these components in this
order:
Header: Paper number, full title, authors, year, arXiv link, sections to read, estimated reading
time
Why You Need This (2–3 sentences)
Explain how this paper connects to VL-JEPA and why skipping it would create a knowledge gap. Plain English Summary (the most important section)
Cover these four points using plain language, short paragraphs, and concrete analogies:
The problem it solved (what was broken before this paper)
The core idea (one big insight explained simply)
How it works step by step (numbered, no jargon unless immediately defined)
Why it matters for VL-JEPA (explicit connection to the architecture Suhail is building)
Key Equation (one equation maximum)
Show the single most important equation. Define every variable in plain English on a separate
line.
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
- Skip one, and
you'll hit a conceptual gap you can't climb around. 3 — Bonus Papers
4 — 2-Week Reading Plan
5 — Key Concepts Cheat Sheet
6 — Comprehension Checklist
🧠 VL-JEPA Learning Path: From Zero to
Architecture Fluency

Before you read a single paper, here's where you're going. VL-JEPA (Vision-Language Joint Embedding Predictive Architecture) is a model from Meta AI,
authored by Delong Chen, Mustafa Shukor, Yann LeCun, Pascale Fung, and colleagues,
submitted December 2025 and revised February 2026. Its central breakthrough: instead of
teaching an AI to generate words one-by-one like a typewriter, it teaches the AI to predict the
meaning of a sentence as a continuous vector in abstract space. Think of the difference this way:
A classical language model says: "Given this image, the next word is 'a', then 'dog', then 'is'..."
— it reconstructs surface text.
- Its central breakthrough: instead of
teaching an AI to generate words one-by-one like a typewriter, it teaches the AI to predict the
meaning of a sentence as a continuous vector in abstract space. Think of the difference this way:
A classical language model says: "Given this image, the next word is 'a', then 'dog', then 'is'..."
— it reconstructs surface text. VL-JEPA says: "Given this image, the semantic embedding of what a correct description would
look like is approximately here in meaning-space." — it reasons about concepts. The result: 50% fewer trainable parameters than token-generating VLMs with the same vision
encoder and training data, native zero-shot classification, and a selective decoding mechanism
that cuts inference operations by 2.85×. To understand why this works, you need the five papers below.
- Think of the difference this way:
A classical language model says: "Given this image, the next word is 'a', then 'dog', then 'is'..."
— it reconstructs surface text. VL-JEPA says: "Given this image, the semantic embedding of what a correct description would
look like is approximately here in meaning-space." — it reasons about concepts. The result: 50% fewer trainable parameters than token-generating VLMs with the same vision
encoder and training data, native zero-shot classification, and a selective decoding mechanism
that cuts inference operations by 2.85×. To understand why this works, you need the five papers below. They are not optional
background — they are the literal source code of VL-JEPA's design decisions.
- They are not optional
background — they are the literal source code of VL-JEPA's design decisions. Authors: Ashish Vaswani, Noam Shazeer, Niki Parmar et al. Year: 2017
arXiv: arxiv.org/abs/1706.03762
Sections to Read: Abstract, Section 1 (Introduction), Section 3 (Model Architecture), Section 3.1–
3.3 (Attention mechanism), Figure 1 and Figure 2. Estimated Reading Time: 60–75 minutes
VL-JEPA's context encoder, target encoder, predictor, and language tower are all Transformer-
based. If you don't understand how attention works — how a model decides which parts of an
input to focus on — you'll be building VL-JEPA blindfolded.


## [2026-03-16 07:03] Source: VL-JEPA Reading List — 5 Paper Summaries (Suhail's notes)

- The "Plain
English Summary" for each paper is what actually matters. Read the real paper after you understand the idea. Estimated total reading time: 6–10 hours across 2 weeks Papers: 5 core + 2 bonus Goal: By the end, you understand every
component of VL-JEPA before writing a line of code
Paper 1: Attention Is All You Need (2017)
Authors: Vaswani et al. (Google Brain) Link: https://arxiv.org/abs/1706.03762 Read: Sections 1, 2, 3, and Figure 1 only. Skip
the machine translation experiments.
- (Google Brain) Link: https://arxiv.org/abs/1706.03762 Read: Sections 1, 2, 3, and Figure 1 only. Skip
the machine translation experiments. Time: 30–45 minutes
Why You Need This
Every model in this list — ViT, CLIP, JEPA — is built on the Transformer. If you don't understand attention, nothing else will
make sense. This is the foundation of modern AI.
- Skip
the machine translation experiments. Time: 30–45 minutes
Why You Need This
Every model in this list — ViT, CLIP, JEPA — is built on the Transformer. If you don't understand attention, nothing else will
make sense. This is the foundation of modern AI. Plain English Summary
The problem it solved: Before 2017, the best models for language were Recurrent Neural Networks (RNNs).
- Problem: by the time you reached the end of a long sentence, the model had "forgotten" the
beginning. Like reading a book but forgetting chapter 1 by chapter 10. The big idea — Self-Attention: Instead of processing one word at a time, look at ALL words simultaneously and let each word
"attend to" every other word based on relevance. Example: "The animal didn't cross the street because it was too tired." - What does "it" refer to? The animal.
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
- - Self-attention
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
Mental model: Imagine a library. Q is your search query. K is the title of each book.
- (Google Brain) Link: https://arxiv.org/abs/2010.11929 Read: Sections 1, 2, 3 and Figure 1. Skip
sections 4–6 (experiments). Time: 30 minutes
Why You Need This
VL-JEPA's vision encoder IS a Vision Transformer. You need to understand how images are turned into sequences that a
Transformer can process. This is the bridge between pixels and attention.
- Skip
sections 4–6 (experiments). Time: 30 minutes
Why You Need This
VL-JEPA's vision encoder IS a Vision Transformer. You need to understand how images are turned into sequences that a
Transformer can process. This is the bridge between pixels and attention. Plain English Summary
The problem it solved: Before ViT, images were processed by Convolutional Neural Networks (CNNs).
- Time: 30 minutes
Why You Need This
VL-JEPA's vision encoder IS a Vision Transformer. You need to understand how images are turned into sequences that a
Transformer can process. This is the bridge between pixels and attention. Plain English Summary
The problem it solved: Before ViT, images were processed by Convolutional Neural Networks (CNNs). CNNs are good but
have inductive biases — they assume nearby pixels matter more than distant ones.
- Plain English Summary
The problem it solved: Before ViT, images were processed by Convolutional Neural Networks (CNNs). CNNs are good but
have inductive biases — they assume nearby pixels matter more than distant ones. Transformers make no such assumption —
but transformers need sequences, not 2D grids. How do you feed an image to a Transformer? The big idea — Patch Embeddings: Cut the image into small fixed-size patches.


## [2026-03-16 07:03] Source: VL-JEPA Learning Path — Senior ML Researcher structured guide

- Learner profile: Suhail is a software engineer with Python experience but limited ML
theory background. He learns best through plain-English explanations, concrete
analogies, and visual mental models — not dense math. End goal: By the end of 2 weeks, Suhail can explain every architectural component of VL-
JEPA (context encoder, target encoder, predictor, language tower, cross-modal alignment)
without referencing any notes. Scope: 5 core papers + 2 bonus papers, in dependency order. Each paper builds on the last.
- Total reading time: 6–10 hours across 2 weeks. Papers to cover (in order):
1. Attention Is All You Need — Vaswani et al., 2017
2. An Image is Worth 16x16 Words (ViT) — Dosovitskiy et al., 2020
3. CLIP: Learning Transferable Visual Models From Natural Language Supervision —
Radford et al., 2021
4.
- An Image is Worth 16x16 Words (ViT) — Dosovitskiy et al., 2020
3. CLIP: Learning Transferable Visual Models From Natural Language Supervision —
Radford et al., 2021
4. Masked Autoencoders Are Scalable Vision Learners (MAE) — He et al., 2021
5. Self-Supervised Learning from Images with a Joint-Embedding Predictive Architecture (I-
JEPA) — Assran et al., 2023
Bonus 1: DINOv2 — Oquab et al., 2023
Bonus 2: CLIP deep-dive (re-read Section 3.2)
# Role
Objective
Context

For each of the 5 core papers, produce a section containing exactly these components in this
order:
Header: Paper number, full title, authors, year, arXiv link, sections to read, estimated reading
time
Why You Need This (2–3 sentences)
Explain how this paper connects to VL-JEPA and why skipping it would create a knowledge gap. Plain English Summary (the most important section)
Cover these four points using plain language, short paragraphs, and concrete analogies:
The problem it solved (what was broken before this paper)
The core idea (one big insight explained simply)
How it works step by step (numbered, no jargon unless immediately defined)
Why it matters for VL-JEPA (explicit connection to the architecture Suhail is building)
Key Equation (one equation maximum)
Show the single most important equation.
- CLIP: Learning Transferable Visual Models From Natural Language Supervision —
Radford et al., 2021
4. Masked Autoencoders Are Scalable Vision Learners (MAE) — He et al., 2021
5. Self-Supervised Learning from Images with a Joint-Embedding Predictive Architecture (I-
JEPA) — Assran et al., 2023
Bonus 1: DINOv2 — Oquab et al., 2023
Bonus 2: CLIP deep-dive (re-read Section 3.2)
# Role
Objective
Context

For each of the 5 core papers, produce a section containing exactly these components in this
order:
Header: Paper number, full title, authors, year, arXiv link, sections to read, estimated reading
time
Why You Need This (2–3 sentences)
Explain how this paper connects to VL-JEPA and why skipping it would create a knowledge gap. Plain English Summary (the most important section)
Cover these four points using plain language, short paragraphs, and concrete analogies:
The problem it solved (what was broken before this paper)
The core idea (one big insight explained simply)
How it works step by step (numbered, no jargon unless immediately defined)
Why it matters for VL-JEPA (explicit connection to the architecture Suhail is building)
Key Equation (one equation maximum)
Show the single most important equation. Define every variable in plain English on a separate
line.
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
- Skip one, and
you'll hit a conceptual gap you can't climb around. 3 — Bonus Papers
4 — 2-Week Reading Plan
5 — Key Concepts Cheat Sheet
6 — Comprehension Checklist
🧠 VL-JEPA Learning Path: From Zero to
Architecture Fluency

Before you read a single paper, here's where you're going. VL-JEPA (Vision-Language Joint Embedding Predictive Architecture) is a model from Meta AI,
authored by Delong Chen, Mustafa Shukor, Yann LeCun, Pascale Fung, and colleagues,
submitted December 2025 and revised February 2026. Its central breakthrough: instead of
teaching an AI to generate words one-by-one like a typewriter, it teaches the AI to predict the
meaning of a sentence as a continuous vector in abstract space. Think of the difference this way:
A classical language model says: "Given this image, the next word is 'a', then 'dog', then 'is'..."
— it reconstructs surface text.
- Its central breakthrough: instead of
teaching an AI to generate words one-by-one like a typewriter, it teaches the AI to predict the
meaning of a sentence as a continuous vector in abstract space. Think of the difference this way:
A classical language model says: "Given this image, the next word is 'a', then 'dog', then 'is'..."
— it reconstructs surface text. VL-JEPA says: "Given this image, the semantic embedding of what a correct description would
look like is approximately here in meaning-space." — it reasons about concepts. The result: 50% fewer trainable parameters than token-generating VLMs with the same vision
encoder and training data, native zero-shot classification, and a selective decoding mechanism
that cuts inference operations by 2.85×. To understand why this works, you need the five papers below.
- Think of the difference this way:
A classical language model says: "Given this image, the next word is 'a', then 'dog', then 'is'..."
— it reconstructs surface text. VL-JEPA says: "Given this image, the semantic embedding of what a correct description would
look like is approximately here in meaning-space." — it reasons about concepts. The result: 50% fewer trainable parameters than token-generating VLMs with the same vision
encoder and training data, native zero-shot classification, and a selective decoding mechanism
that cuts inference operations by 2.85×. To understand why this works, you need the five papers below. They are not optional
background — they are the literal source code of VL-JEPA's design decisions.
- They are not optional
background — they are the literal source code of VL-JEPA's design decisions. Authors: Ashish Vaswani, Noam Shazeer, Niki Parmar et al. Year: 2017
arXiv: arxiv.org/abs/1706.03762
Sections to Read: Abstract, Section 1 (Introduction), Section 3 (Model Architecture), Section 3.1–
3.3 (Attention mechanism), Figure 1 and Figure 2. Estimated Reading Time: 60–75 minutes
VL-JEPA's context encoder, target encoder, predictor, and language tower are all Transformer-
based. If you don't understand how attention works — how a model decides which parts of an
input to focus on — you'll be building VL-JEPA blindfolded.


## [2026-03-16 07:03] Source: Suhail's Research Summary + Mind Map

- Joint Embedding Predictive Architecture (JEPA) represents a paradigm shift in artificial intelligence from generating raw data (like pixels or text tokens) to predicting abstract, semantic meaning. Unlike traditional generative models—such as Masked Autoencoders (MAEs) or Large Language Models (LLMs)—that waste massive computational capacity trying to reconstruct irrelevant surface-level noise or specific word choices, JEPA focuses entirely on predicting high-level representations in a latent space. The Core Architecture:
The JEPA framework teaches AI to "imagine what's missing" by utilizing three main components:
1.
- Joint Embedding Predictive Architecture (JEPA) represents a paradigm shift in artificial intelligence from generating raw data (like pixels or text tokens) to predicting abstract, semantic meaning. Unlike traditional generative models—such as Masked Autoencoders (MAEs) or Large Language Models (LLMs)—that waste massive computational capacity trying to reconstruct irrelevant surface-level noise or specific word choices, JEPA focuses entirely on predicting high-level representations in a latent space. The Core Architecture:
The JEPA framework teaches AI to "imagine what's missing" by utilizing three main components:
1. Context Encoder: A neural network (often built on Transformer self-attention mechanisms) that processes the visible, known input to extract its essential structure into a "context embedding".
- Unlike traditional generative models—such as Masked Autoencoders (MAEs) or Large Language Models (LLMs)—that waste massive computational capacity trying to reconstruct irrelevant surface-level noise or specific word choices, JEPA focuses entirely on predicting high-level representations in a latent space. The Core Architecture:
The JEPA framework teaches AI to "imagine what's missing" by utilizing three main components:
1. Context Encoder: A neural network (often built on Transformer self-attention mechanisms) that processes the visible, known input to extract its essential structure into a "context embedding". 2. Target Encoder: A parallel network that processes the hidden, missing, or future data to create a "ground truth" embedding.
- Context Encoder: A neural network (often built on Transformer self-attention mechanisms) that processes the visible, known input to extract its essential structure into a "context embedding". 2. Target Encoder: A parallel network that processes the hidden, missing, or future data to create a "ground truth" embedding. To prevent "representation collapse"—a failure mode where the model lazily outputs constants to minimize loss—the target encoder's weights are typically updated using a slow Exponential Moving Average (EMA) of the context encoder, making it a moving target. 3.
- 2. Target Encoder: A parallel network that processes the hidden, missing, or future data to create a "ground truth" embedding. To prevent "representation collapse"—a failure mode where the model lazily outputs constants to minimize loss—the target encoder's weights are typically updated using a slow Exponential Moving Average (EMA) of the context encoder, making it a moving target. 3. Predictor: A lightweight module that takes the context embedding—and occasionally a latent variable to account for multiple plausible future outcomes (uncertainty)—and attempts to predict the target embedding.
- To prevent "representation collapse"—a failure mode where the model lazily outputs constants to minimize loss—the target encoder's weights are typically updated using a slow Exponential Moving Average (EMA) of the context encoder, making it a moving target. 3. Predictor: A lightweight module that takes the context embedding—and occasionally a latent variable to account for multiple plausible future outcomes (uncertainty)—and attempts to predict the target embedding. The model is trained by minimizing the distance (or "energy") between the predicted and true target embeddings using contrastive or regularized loss functions. Key Variants and Capabilities:
- I-JEPA (Images): Predicts the embeddings of missing image blocks from a visible context block.
- 3. Predictor: A lightweight module that takes the context embedding—and occasionally a latent variable to account for multiple plausible future outcomes (uncertainty)—and attempts to predict the target embedding. The model is trained by minimizing the distance (or "energy") between the predicted and true target embeddings using contrastive or regularized loss functions. Key Variants and Capabilities:
- I-JEPA (Images): Predicts the embeddings of missing image blocks from a visible context block. By avoiding pixel-level reconstruction, it learns highly semantic image representations rapidly and without relying on hand-crafted data augmentations.
- Predictor: A lightweight module that takes the context embedding—and occasionally a latent variable to account for multiple plausible future outcomes (uncertainty)—and attempts to predict the target embedding. The model is trained by minimizing the distance (or "energy") between the predicted and true target embeddings using contrastive or regularized loss functions. Key Variants and Capabilities:
- I-JEPA (Images): Predicts the embeddings of missing image blocks from a visible context block. By avoiding pixel-level reconstruction, it learns highly semantic image representations rapidly and without relying on hand-crafted data augmentations. - VL-JEPA (Vision-Language): Eliminates the expensive, autoregressive token-by-token generation of traditional Vision-Language Models (VLMs).
- The model is trained by minimizing the distance (or "energy") between the predicted and true target embeddings using contrastive or regularized loss functions. Key Variants and Capabilities:
- I-JEPA (Images): Predicts the embeddings of missing image blocks from a visible context block. By avoiding pixel-level reconstruction, it learns highly semantic image representations rapidly and without relying on hand-crafted data augmentations. - VL-JEPA (Vision-Language): Eliminates the expensive, autoregressive token-by-token generation of traditional Vision-Language Models (VLMs). It predicts a single "thought embedding" representing the answer to a visual query.
- By avoiding pixel-level reconstruction, it learns highly semantic image representations rapidly and without relying on hand-crafted data augmentations. - VL-JEPA (Vision-Language): Eliminates the expensive, autoregressive token-by-token generation of traditional Vision-Language Models (VLMs). It predicts a single "thought embedding" representing the answer to a visual query. Text is only generated via a separate, lightweight decoder when requested. This enables selective decoding, where the model silently monitors a video stream and only outputs text when the semantic meaning of the scene actually changes.
