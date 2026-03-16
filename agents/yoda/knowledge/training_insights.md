# Training Insights

## [2026-03-16 00:00] Source: Initial Knowledge (I-JEPA paper, BYOL, VL-JEPA research, empirical best practices)

### EMA Schedule

- **Momentum range**: Start at 0.996 and anneal to 1.0 following a cosine schedule over the course of training. Early in training, faster target encoder updates (lower momentum) help the target track the rapidly-changing context encoder. Later, near-frozen targets provide increasingly stable objectives.
- **Formula**: `tau = 1 - (1 - tau_base) * (1 + cos(pi * step / total_steps)) / 2`

### Masking Strategy

- **Rectangular block masking outperforms random masking.** Blocks of contiguous patches (aspect ratio sampled uniformly in [0.75, 1.5], area ratio in [0.15, 0.2] per block) force the model to reason about spatial structure rather than trivially interpolating from nearby visible patches.
- **Multi-block targets**: 4 target blocks are sampled per image; the context is everything outside those blocks. This gives the model a harder prediction task and improves downstream performance.
- **Context ratio**: Approximately 60-75% of patches remain visible as context after masking.

### Loss Functions

- **JEPA predictive loss**: Mean Squared Error (MSE) between predictor output embeddings and target encoder output embeddings, averaged over all masked positions. Smooth-L1 loss is a viable alternative but MSE has shown more stable training in practice.
- **Cross-modal alignment loss** (VL-JEPA): Symmetric InfoNCE (NT-Xent) between vision and text projection head outputs. Temperature parameter `tau = 0.07` (learnable or fixed).
- **Combined loss**: `L = L_jepa + lambda_align * L_align` where `lambda_align` is tuned (start at 0.5, sweep [0.1, 1.0]). Too high and the alignment signal dominates, collapsing JEPA quality; too low and cross-modal transfer suffers.

### Optimizer and Schedule

- **Optimizer**: AdamW with `lr = 1.5e-4`, `weight_decay = 0.05`, `betas = (0.9, 0.95)`.
- **Learning rate schedule**: Linear warmup for the first 40 epochs (or 10% of total steps), then cosine decay to `1e-6`.
- **Layer-wise LR decay**: Optional -- apply a decay factor of 0.65-0.75 per layer for the ViT encoder when fine-tuning.
- **Gradient clipping**: Max norm 1.0 to prevent training instabilities.

### Mixed Precision Training

- **AMP (Automatic Mixed Precision)**: Use `torch.cuda.amp` with `GradScaler`. Forward pass in float16, loss computation and backward in float32 master weights. Reduces memory ~40% and speeds training ~1.5x on Ampere+ GPUs.
- **BFloat16**: Preferred over float16 on A100/H100 -- wider dynamic range means `GradScaler` is unnecessary.

### Augmentation

- **Multi-crop**: Two global crops (224x224, scale [0.4, 1.0]) and several local crops (96x96, scale [0.05, 0.4]). JEPA applies masking to the global crops.
- **Standard augmentations**: RandomResizedCrop, RandomHorizontalFlip. Color jitter and Gaussian blur are optional -- I-JEPA is less reliant on heavy augmentation than contrastive methods because the prediction task itself provides a strong learning signal.
- **Product-image note**: For product datasets with white backgrounds, aggressive color jitter can be counterproductive. Prefer geometric augmentations (rotation, perspective) and cutout.

### Batch Size Considerations

- **Sweet spot**: 256-1024 per GPU. Larger batches (2048+) benefit the contrastive alignment loss (more negatives) but are not critical for the JEPA prediction loss.
- **Scaling rule**: When increasing batch size by factor `k`, scale learning rate by `sqrt(k)` (linear scaling also works for moderate increases).

### Practical Tips

- **Warmup is critical**: Skipping warmup leads to early divergence, especially with the combined JEPA + alignment loss.
- **Monitor target encoder similarity**: If cosine similarity between context and target encoder representations saturates at 1.0 too early, the EMA momentum is too high -- lower `tau_base`.
- **Checkpoint the EMA encoder**: At evaluation time, the target (EMA) encoder typically outperforms the context encoder on linear probing and retrieval benchmarks.


## [2026-03-16 07:01] Source: VL-JEPA Reading List — 5 Paper Summaries (Suhail's notes)

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
- Feed 196
patch embeddings into a standard Transformer 7. The Transformer produces 196 output embeddings — one per patch 8. Add a
special [CLS] token at position 0 → its output embedding = the whole image representation
What the model learns: Without any explicit instruction, ViT learns to attend to semantically meaningful regions. Show it a
dog → it attends to the dog's face and paws. Show it a shelf → it attends to the products, not the background.
- What if you trained a model on 400 million such pairs? The caption is a free label — no human
annotation needed. The architecture: Two encoders trained together: - Image Encoder (ViT or ResNet): image → 512-dimensional vector - Text
Encoder (Transformer): caption → 512-dimensional vector
The training objective — Contrastive Loss: For a batch of N image-text pairs: - Match each image to its correct caption →
push their vectors close together - Push each image away from all N-1 wrong captions - Do the same for each text
After training on 400M pairs: the image of a dog and the text "a dog" end up as nearly identical vectors in 512-dimensional
space. What CLIP can do: - Zero-shot classification: never seen a "labrador" example → still classifies it correctly because it
understands the word - Image search by text query - Text-to-image retrieval
Why it matters for VL-JEPA: VL-JEPA takes CLIP's cross-modal alignment idea + combines it with JEPA's predictive coding: -
CLIP: align image embeddings with text embeddings (what CLIP does) - JEPA: predict masked image regions in embedding
space (what JEPA adds) - VL-JEPA: do both at the same time on product images + descriptions
The key limitation of CLIP (why we need JEPA): CLIP is discriminative — it learns to match pairs, but doesn't build a deep
understanding of the visual world. It can tell you "this image matches the text 'red chair'" but can't tell you "there are 3 chairs in
this image." JEPA's predictive objective teaches deeper structure.
- Show only 25% of patches to the encoder 4. A decoder tries to reconstruct the original pixel values of all
masked patches 5. Loss = difference between predicted pixels and actual pixels
The model must learn rich visual representations to reconstruct masked regions. You can't reconstruct a hidden product image
region without understanding what the product looks like. Why masking 75% works: - Too little masking → easy task → model doesn't learn much - 75% masking → hard task → model
must deeply understand structure - The model can't "cheat" by looking at nearby unmasked patches
The asymmetric encoder-decoder design: - Encoder: Only sees 25% of patches (the visible ones).
- Small, lightweight. - Result: 3× faster training
because encoder only processes 25% of patches. What MAE learns: Masking and reconstructing images teaches the model to understand: - Local texture (what does metal look
like?) - Global structure (where would the handle of this tool be?) - Semantic context (this is a shelf, so there should be products
here)
The limitation MAE has (why JEPA is better): MAE reconstructs raw pixels. Pixels are noisy, redundant, and low-level. Reconstructing the exact RGB value of each pixel wastes model capacity on irrelevant details (lighting, shadows, JPEG artifacts).
- The model must predict what the
target encoder would output for the masked region, given only the context patches. The four components:
1. Context Encoder (θ) - A ViT that processes only the visible (unmasked) patches - Outputs context embeddings — rich
representations of what it can see - Updated by gradient descent (learns actively)
2. Target Encoder (θ̄) - Identical architecture to context encoder - Processes ALL patches (visible + masked) - Produces the
"ground truth" target embeddings - Updated via Exponential Moving Average (EMA) — NOT by gradients - Update rule: θ̄ ← m ×
θ̄ + (1-m) × θ, where m ≈ 0.996
3. Predictor - A small 3-layer Transformer that sits between context encoder and target encoder - Input: context embeddings +
positional queries for masked patches - Output: predicted embeddings for each masked position - "Given what I can see, what
should the masked region look like in embedding space?"
4.
- The four components:
1. Context Encoder (θ) - A ViT that processes only the visible (unmasked) patches - Outputs context embeddings — rich
representations of what it can see - Updated by gradient descent (learns actively)
2. Target Encoder (θ̄) - Identical architecture to context encoder - Processes ALL patches (visible + masked) - Produces the
"ground truth" target embeddings - Updated via Exponential Moving Average (EMA) — NOT by gradients - Update rule: θ̄ ← m ×
θ̄ + (1-m) × θ, where m ≈ 0.996
3. Predictor - A small 3-layer Transformer that sits between context encoder and target encoder - Input: context embeddings +
positional queries for masked patches - Output: predicted embeddings for each masked position - "Given what I can see, what
should the masked region look like in embedding space?"
4. Loss Function
L = MSE(predicted_embeddings, target_embeddings)
  = mean((predictor(context_enc(visible)) - target_enc(masked))²)
Simple mean squared error between predicted and actual target embeddings.
- Target Encoder (θ̄) - Identical architecture to context encoder - Processes ALL patches (visible + masked) - Produces the
"ground truth" target embeddings - Updated via Exponential Moving Average (EMA) — NOT by gradients - Update rule: θ̄ ← m ×
θ̄ + (1-m) × θ, where m ≈ 0.996
3. Predictor - A small 3-layer Transformer that sits between context encoder and target encoder - Input: context embeddings +
positional queries for masked patches - Output: predicted embeddings for each masked position - "Given what I can see, what
should the masked region look like in embedding space?"
4. Loss Function
L = MSE(predicted_embeddings, target_embeddings)
  = mean((predictor(context_enc(visible)) - target_enc(masked))²)
Simple mean squared error between predicted and actual target embeddings. No contrastive loss. No augmentations.
- Predictor - A small 3-layer Transformer that sits between context encoder and target encoder - Input: context embeddings +
positional queries for masked patches - Output: predicted embeddings for each masked position - "Given what I can see, what
should the masked region look like in embedding space?"
4. Loss Function
L = MSE(predicted_embeddings, target_embeddings)
  = mean((predictor(context_enc(visible)) - target_enc(masked))²)
Simple mean squared error between predicted and actual target embeddings. No contrastive loss. No augmentations. No
negative pairs.
- No augmentations. No
negative pairs. Why EMA prevents collapse: If both encoders were updated by gradients toward the same loss, they'd find the trivial solution:
output all zeros (then loss = 0 forever). EMA prevents this: - Target encoder is updated slowly (momentum = 0.996 means it only
changes 0.4% per step) - Context encoder updates fast - There's always a gap between them — the predictor is always chasing a
moving target
The masking strategy: - Divide image into 196 patches (14×14 grid) - Select 4 random rectangular "target blocks" to mask
(roughly 50% of patches) - Context = remaining visible patches - The model must predict the target blocks given the context
Rectangular blocks are harder than random patches — the model can't reconstruct a rectangular region just from adjacent
context patches. It must understand the global content.


## [2026-03-16 07:01] Source: VL-JEPA Learning Path — Senior ML Researcher structured guide

- Limitation / What Comes Next
One short paragraph explaining what this paper cannot do — which directly motivates the next
paper in the sequence. Mental Model Diagram
A simple ASCII or text-based flow diagram showing the paper's core pipeline (input → process
→ output). After Paper 4 and Paper 5 are complete, insert a side-by-side comparison table with these rows:
What gets predicted
Loss function
Requires augmentations? What the model learns
Main weakness
Instructions
1 — Paper Entry Structure
2 — Comparison Table: MAE vs. I-JEPA

For each bonus paper, provide: title, link, sections to read, estimated time, and a "Why It's
Relevant" paragraph (3–5 sentences max).
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
- Its central breakthrough: instead of
teaching an AI to generate words one-by-one like a typewriter, it teaches the AI to predict the
meaning of a sentence as a continuous vector in abstract space. Think of the difference this way:
A classical language model says: "Given this image, the next word is 'a', then 'dog', then 'is'..."
— it reconstructs surface text. VL-JEPA says: "Given this image, the semantic embedding of what a correct description would
look like is approximately here in meaning-space." — it reasons about concepts. The result: 50% fewer trainable parameters than token-generating VLMs with the same vision
encoder and training data, native zero-shot classification, and a selective decoding mechanism
that cuts inference operations by 2.85×. To understand why this works, you need the five papers below.
- A high score means "these two tokens are very relevant to each other."
4. Scale and normalize. Divide by 
 (where 
 is key dimension) to prevent vanishingly
small gradients. Apply softmax so scores sum to 1. 5.
- 6. Run multiple attention heads in parallel. Different heads learn different types of
relationships (e.g., one head tracks syntax, another tracks semantic meaning). 7. Stack many Transformer blocks.
- When the VL-JEPA predictor takes a
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
of each to blend into your answer. Transformers were designed for 1D sequences of text tokens. An image is a 2D grid of pixels —
not a sequence.
- Estimated Reading Time: 60–75 minutes
CLIP introduced the idea of cross-modal alignment — mapping images and text into the same
embedding space so that "a photo of a dog" and an actual photo of a dog land near each other as
vectors. VL-JEPA's core innovation is to predict in this joint embedding space rather than decode
tokens. Without understanding CLIP's contrastive alignment objective, you won't understand
what VL-JEPA's language tower is trying to do or why predicting in semantic space is
fundamentally different from predicting tokens. The problem it solved:
Classical image classifiers (like ViT trained on ImageNet) are brittle. They learn to recognize
1,000 specific categories, and if you show them a class they weren't trained on, they fail
completely — even if the new class is just "a photo of a golden retriever in the snow" when they
trained on "golden retriever." The model never learned language — it just learned label numbers.
- 4. Compute similarity matrix. For a batch of N pairs, compute the N×N cosine similarity matrix
between all image embeddings and all text embeddings. 5. Apply contrastive loss.
- For a batch of N pairs, compute the N×N cosine similarity matrix
between all image embeddings and all text embeddings. 5. Apply contrastive loss. The diagonal of that matrix (true pairs) should have high similarity. Everything off-diagonal (wrong pairs) should have low similarity.
- The diagonal of that matrix (true pairs) should have high similarity. Everything off-diagonal (wrong pairs) should have low similarity. The InfoNCE loss
penalizes deviations from this. 6. Zero-shot inference.


## [2026-03-16 07:03] Source: VL-JEPA Reading List — 5 Paper Summaries (Suhail's notes)

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
- Feed 196
patch embeddings into a standard Transformer 7. The Transformer produces 196 output embeddings — one per patch 8. Add a
special [CLS] token at position 0 → its output embedding = the whole image representation
What the model learns: Without any explicit instruction, ViT learns to attend to semantically meaningful regions. Show it a
dog → it attends to the dog's face and paws. Show it a shelf → it attends to the products, not the background.
- What if you trained a model on 400 million such pairs? The caption is a free label — no human
annotation needed. The architecture: Two encoders trained together: - Image Encoder (ViT or ResNet): image → 512-dimensional vector - Text
Encoder (Transformer): caption → 512-dimensional vector
The training objective — Contrastive Loss: For a batch of N image-text pairs: - Match each image to its correct caption →
push their vectors close together - Push each image away from all N-1 wrong captions - Do the same for each text
After training on 400M pairs: the image of a dog and the text "a dog" end up as nearly identical vectors in 512-dimensional
space. What CLIP can do: - Zero-shot classification: never seen a "labrador" example → still classifies it correctly because it
understands the word - Image search by text query - Text-to-image retrieval
Why it matters for VL-JEPA: VL-JEPA takes CLIP's cross-modal alignment idea + combines it with JEPA's predictive coding: -
CLIP: align image embeddings with text embeddings (what CLIP does) - JEPA: predict masked image regions in embedding
space (what JEPA adds) - VL-JEPA: do both at the same time on product images + descriptions
The key limitation of CLIP (why we need JEPA): CLIP is discriminative — it learns to match pairs, but doesn't build a deep
understanding of the visual world. It can tell you "this image matches the text 'red chair'" but can't tell you "there are 3 chairs in
this image." JEPA's predictive objective teaches deeper structure.
- Show only 25% of patches to the encoder 4. A decoder tries to reconstruct the original pixel values of all
masked patches 5. Loss = difference between predicted pixels and actual pixels
The model must learn rich visual representations to reconstruct masked regions. You can't reconstruct a hidden product image
region without understanding what the product looks like. Why masking 75% works: - Too little masking → easy task → model doesn't learn much - 75% masking → hard task → model
must deeply understand structure - The model can't "cheat" by looking at nearby unmasked patches
The asymmetric encoder-decoder design: - Encoder: Only sees 25% of patches (the visible ones).
- Small, lightweight. - Result: 3× faster training
because encoder only processes 25% of patches. What MAE learns: Masking and reconstructing images teaches the model to understand: - Local texture (what does metal look
like?) - Global structure (where would the handle of this tool be?) - Semantic context (this is a shelf, so there should be products
here)
The limitation MAE has (why JEPA is better): MAE reconstructs raw pixels. Pixels are noisy, redundant, and low-level. Reconstructing the exact RGB value of each pixel wastes model capacity on irrelevant details (lighting, shadows, JPEG artifacts).
- The model must predict what the
target encoder would output for the masked region, given only the context patches. The four components:
1. Context Encoder (θ) - A ViT that processes only the visible (unmasked) patches - Outputs context embeddings — rich
representations of what it can see - Updated by gradient descent (learns actively)
2. Target Encoder (θ̄) - Identical architecture to context encoder - Processes ALL patches (visible + masked) - Produces the
"ground truth" target embeddings - Updated via Exponential Moving Average (EMA) — NOT by gradients - Update rule: θ̄ ← m ×
θ̄ + (1-m) × θ, where m ≈ 0.996
3. Predictor - A small 3-layer Transformer that sits between context encoder and target encoder - Input: context embeddings +
positional queries for masked patches - Output: predicted embeddings for each masked position - "Given what I can see, what
should the masked region look like in embedding space?"
4.
- The four components:
1. Context Encoder (θ) - A ViT that processes only the visible (unmasked) patches - Outputs context embeddings — rich
representations of what it can see - Updated by gradient descent (learns actively)
2. Target Encoder (θ̄) - Identical architecture to context encoder - Processes ALL patches (visible + masked) - Produces the
"ground truth" target embeddings - Updated via Exponential Moving Average (EMA) — NOT by gradients - Update rule: θ̄ ← m ×
θ̄ + (1-m) × θ, where m ≈ 0.996
3. Predictor - A small 3-layer Transformer that sits between context encoder and target encoder - Input: context embeddings +
positional queries for masked patches - Output: predicted embeddings for each masked position - "Given what I can see, what
should the masked region look like in embedding space?"
4. Loss Function
L = MSE(predicted_embeddings, target_embeddings)
  = mean((predictor(context_enc(visible)) - target_enc(masked))²)
Simple mean squared error between predicted and actual target embeddings.
- Target Encoder (θ̄) - Identical architecture to context encoder - Processes ALL patches (visible + masked) - Produces the
"ground truth" target embeddings - Updated via Exponential Moving Average (EMA) — NOT by gradients - Update rule: θ̄ ← m ×
θ̄ + (1-m) × θ, where m ≈ 0.996
3. Predictor - A small 3-layer Transformer that sits between context encoder and target encoder - Input: context embeddings +
positional queries for masked patches - Output: predicted embeddings for each masked position - "Given what I can see, what
should the masked region look like in embedding space?"
4. Loss Function
L = MSE(predicted_embeddings, target_embeddings)
  = mean((predictor(context_enc(visible)) - target_enc(masked))²)
Simple mean squared error between predicted and actual target embeddings. No contrastive loss. No augmentations.
- Predictor - A small 3-layer Transformer that sits between context encoder and target encoder - Input: context embeddings +
positional queries for masked patches - Output: predicted embeddings for each masked position - "Given what I can see, what
should the masked region look like in embedding space?"
4. Loss Function
L = MSE(predicted_embeddings, target_embeddings)
  = mean((predictor(context_enc(visible)) - target_enc(masked))²)
Simple mean squared error between predicted and actual target embeddings. No contrastive loss. No augmentations. No
negative pairs.
- No augmentations. No
negative pairs. Why EMA prevents collapse: If both encoders were updated by gradients toward the same loss, they'd find the trivial solution:
output all zeros (then loss = 0 forever). EMA prevents this: - Target encoder is updated slowly (momentum = 0.996 means it only
changes 0.4% per step) - Context encoder updates fast - There's always a gap between them — the predictor is always chasing a
moving target
The masking strategy: - Divide image into 196 patches (14×14 grid) - Select 4 random rectangular "target blocks" to mask
(roughly 50% of patches) - Context = remaining visible patches - The model must predict the target blocks given the context
Rectangular blocks are harder than random patches — the model can't reconstruct a rectangular region just from adjacent
context patches. It must understand the global content.


## [2026-03-16 07:03] Source: VL-JEPA Learning Path — Senior ML Researcher structured guide

- Limitation / What Comes Next
One short paragraph explaining what this paper cannot do — which directly motivates the next
paper in the sequence. Mental Model Diagram
A simple ASCII or text-based flow diagram showing the paper's core pipeline (input → process
→ output). After Paper 4 and Paper 5 are complete, insert a side-by-side comparison table with these rows:
What gets predicted
Loss function
Requires augmentations? What the model learns
Main weakness
Instructions
1 — Paper Entry Structure
2 — Comparison Table: MAE vs. I-JEPA

For each bonus paper, provide: title, link, sections to read, estimated time, and a "Why It's
Relevant" paragraph (3–5 sentences max).
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
- Its central breakthrough: instead of
teaching an AI to generate words one-by-one like a typewriter, it teaches the AI to predict the
meaning of a sentence as a continuous vector in abstract space. Think of the difference this way:
A classical language model says: "Given this image, the next word is 'a', then 'dog', then 'is'..."
— it reconstructs surface text. VL-JEPA says: "Given this image, the semantic embedding of what a correct description would
look like is approximately here in meaning-space." — it reasons about concepts. The result: 50% fewer trainable parameters than token-generating VLMs with the same vision
encoder and training data, native zero-shot classification, and a selective decoding mechanism
that cuts inference operations by 2.85×. To understand why this works, you need the five papers below.
- A high score means "these two tokens are very relevant to each other."
4. Scale and normalize. Divide by 
 (where 
 is key dimension) to prevent vanishingly
small gradients. Apply softmax so scores sum to 1. 5.
- 6. Run multiple attention heads in parallel. Different heads learn different types of
relationships (e.g., one head tracks syntax, another tracks semantic meaning). 7. Stack many Transformer blocks.
- When the VL-JEPA predictor takes a
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
of each to blend into your answer. Transformers were designed for 1D sequences of text tokens. An image is a 2D grid of pixels —
not a sequence.
- Estimated Reading Time: 60–75 minutes
CLIP introduced the idea of cross-modal alignment — mapping images and text into the same
embedding space so that "a photo of a dog" and an actual photo of a dog land near each other as
vectors. VL-JEPA's core innovation is to predict in this joint embedding space rather than decode
tokens. Without understanding CLIP's contrastive alignment objective, you won't understand
what VL-JEPA's language tower is trying to do or why predicting in semantic space is
fundamentally different from predicting tokens. The problem it solved:
Classical image classifiers (like ViT trained on ImageNet) are brittle. They learn to recognize
1,000 specific categories, and if you show them a class they weren't trained on, they fail
completely — even if the new class is just "a photo of a golden retriever in the snow" when they
trained on "golden retriever." The model never learned language — it just learned label numbers.
- 4. Compute similarity matrix. For a batch of N pairs, compute the N×N cosine similarity matrix
between all image embeddings and all text embeddings. 5. Apply contrastive loss.
- For a batch of N pairs, compute the N×N cosine similarity matrix
between all image embeddings and all text embeddings. 5. Apply contrastive loss. The diagonal of that matrix (true pairs) should have high similarity. Everything off-diagonal (wrong pairs) should have low similarity.
- The diagonal of that matrix (true pairs) should have high similarity. Everything off-diagonal (wrong pairs) should have low similarity. The InfoNCE loss
penalizes deviations from this. 6. Zero-shot inference.


## [2026-03-16 07:03] Source: Suhail's Research Summary + Mind Map

- Joint Embedding Predictive Architecture (JEPA) represents a paradigm shift in artificial intelligence from generating raw data (like pixels or text tokens) to predicting abstract, semantic meaning. Unlike traditional generative models—such as Masked Autoencoders (MAEs) or Large Language Models (LLMs)—that waste massive computational capacity trying to reconstruct irrelevant surface-level noise or specific word choices, JEPA focuses entirely on predicting high-level representations in a latent space. The Core Architecture:
The JEPA framework teaches AI to "imagine what's missing" by utilizing three main components:
1.
- 2. Target Encoder: A parallel network that processes the hidden, missing, or future data to create a "ground truth" embedding. To prevent "representation collapse"—a failure mode where the model lazily outputs constants to minimize loss—the target encoder's weights are typically updated using a slow Exponential Moving Average (EMA) of the context encoder, making it a moving target. 3. Predictor: A lightweight module that takes the context embedding—and occasionally a latent variable to account for multiple plausible future outcomes (uncertainty)—and attempts to predict the target embedding.
- 3. Predictor: A lightweight module that takes the context embedding—and occasionally a latent variable to account for multiple plausible future outcomes (uncertainty)—and attempts to predict the target embedding. The model is trained by minimizing the distance (or "energy") between the predicted and true target embeddings using contrastive or regularized loss functions. Key Variants and Capabilities:
- I-JEPA (Images): Predicts the embeddings of missing image blocks from a visible context block. By avoiding pixel-level reconstruction, it learns highly semantic image representations rapidly and without relying on hand-crafted data augmentations.
- The model is trained by minimizing the distance (or "energy") between the predicted and true target embeddings using contrastive or regularized loss functions. Key Variants and Capabilities:
- I-JEPA (Images): Predicts the embeddings of missing image blocks from a visible context block. By avoiding pixel-level reconstruction, it learns highly semantic image representations rapidly and without relying on hand-crafted data augmentations. - VL-JEPA (Vision-Language): Eliminates the expensive, autoregressive token-by-token generation of traditional Vision-Language Models (VLMs). It predicts a single "thought embedding" representing the answer to a visual query.
- It predicts a single "thought embedding" representing the answer to a visual query. Text is only generated via a separate, lightweight decoder when requested. This enables selective decoding, where the model silently monitors a video stream and only outputs text when the semantic meaning of the scene actually changes. This yields up to 2.85x faster inference with 50% fewer parameters. - Domain Extensions: V-JEPA (video), T-JEPA (tabular data), EchoJEPA (medical imaging/echocardiography).
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
