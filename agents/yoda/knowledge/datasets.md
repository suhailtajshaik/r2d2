# Datasets

## [2026-03-16 00:00] Source: Initial Knowledge (dataset documentation, HuggingFace, research papers)

### ABO (Amazon Berkeley Objects)

- **Size**: ~147,000 product listings with metadata; approximately 398,000 unique catalog images across 576 product categories.
- **Content**: Multi-view product images (front, back, side, detail), 3D models for a subset, rich metadata (title, description, brand, color, dimensions, material, bullet-point features).
- **License**: CC BY-NC 4.0 -- suitable for research, not commercial deployment without relicensing.
- **Source**: https://amazon-berkeley-objects.s3.amazonaws.com/index.html
- **VL-JEPA relevance**: Excellent for vision-language pre-training -- each product has multiple images paired with natural-language descriptions. Multi-view images let the model learn view-invariant representations.
- **Preprocessing notes**: Images vary in resolution (typically 1000-2000px on the long side). Resize to 224x224 for ViT-patch16. White/neutral backgrounds are common; consider background augmentation if downstream tasks involve in-context product photos.

### Home Depot Product Dataset

- **Source**: HuggingFace (`huggingface.co/datasets/home-depot-product-authority/home-depot-product-catalog` -- verify exact path).
- **Content**: Product titles, descriptions, images, and category labels for home improvement products.
- **Size**: ~100K+ items (varies by version).
- **VL-JEPA relevance**: Complements ABO with a different product domain. Useful for evaluating cross-domain transfer.

### Products-10K

- **Size**: 10,000 product SKUs, roughly 150,000 images total.
- **Content**: Product images with fine-grained category labels; designed for product retrieval benchmarks.
- **VL-JEPA relevance**: Good held-out evaluation set for retrieval metrics (Recall@K, mAP).

### ImageNet (ILSVRC 2012)

- **Size**: 1.28M training images, 50K validation images across 1,000 classes.
- **VL-JEPA relevance**: Standard pre-training dataset for the vision encoder before domain-specific fine-tuning. I-JEPA pre-trained on ImageNet achieves strong linear-probe accuracy (73-76% for ViT-B/16 at 300 epochs).
- **Note**: ImageNet pre-trained weights can be used to initialize the context/target encoders, giving a warm start before switching to the JEPA + alignment objective on product data.

### Considerations for Product Image Datasets

- **White/studio backgrounds**: Most product photos are shot on white or neutral backgrounds. This reduces the value of background-dependent augmentations (e.g., random erasing of background regions). Focus augmentations on the foreground object.
- **Multiple views per product**: Treat different views of the same product as positive pairs for contrastive alignment, or as additional masking targets for JEPA.
- **Text quality**: Product descriptions range from rich paragraphs to sparse bullet points. Preprocessing (deduplication, lowercasing, stripping HTML entities) is important before tokenization.
- **Class imbalance**: Product catalogs are long-tailed. Consider balanced sampling or temperature-scaled sampling during training.
- **Image resolution**: Product images are often high-resolution but get downscaled to 224x224. For fine-grained detail (e.g., fabric texture, connector types), consider using 384x384 input (576 patches) at the cost of ~3.4x more compute per image.


## [2026-03-16 07:01] Source: VL-JEPA Reading List — 5 Paper Summaries (Suhail's notes)

- It learns this from data. This makes
it more flexible than CNNs — it can learn any spatial relationship, not just local ones. Mental Model
Image (224×224 pixels)
        ↓
Cut into patches (16×16 each)
        ↓
[P1][P2][P3]...[P196]  ← 196 patches, like 196 words
        ↓
Each patch → embedding vector (768 numbers)
        ↓
Add position info: P1=top-left, P196=bottom-right
        ↓
Feed into Transformer (same as language Transformer)
        ↓
196 output embeddings — each patch now "knows" about all other patches
Paper 3: Learning Transferable Visual Models From Natural Language Supervision
(CLIP, 2021)
Authors: Radford et al. (OpenAI) Link: https://arxiv.org/abs/2103.00020 Read: Sections 1, 2, 3.1, 3.2, and Figure 1. Skip
sections 4–5.
- Time: 45 minutes
Why You Need This

VL-JEPA's cross-modal alignment (connecting vision and language) is inspired directly by CLIP. CLIP showed the world that you
can train a model to understand both images and text together, using only natural image-caption pairs from the internet — no
manual labels needed. Plain English Summary
The problem it solved: Training vision models traditionally required massive labeled datasets — ImageNet has 14 million
images, each manually labeled by humans. This is expensive, slow, and limits what the model can recognize (only what's in the
labels). The big idea — Learn from image-text pairs: The internet is full of images with captions — news articles, product listings,
social media, Wikipedia.
- EMA prevents this: - Target encoder is updated slowly (momentum = 0.996 means it only
changes 0.4% per step) - Context encoder updates fast - There's always a gap between them — the predictor is always chasing a
moving target
The masking strategy: - Divide image into 196 patches (14×14 grid) - Select 4 random rectangular "target blocks" to mask
(roughly 50% of patches) - Context = remaining visible patches - The model must predict the target blocks given the context
Rectangular blocks are harder than random patches — the model can't reconstruct a rectangular region just from adjacent
context patches. It must understand the global content. What I-JEPA learns: Without any labels, without any augmentations, trained only to predict masked representations: -
Semantic understanding: similar objects cluster in embedding space - Spatial understanding: knows what "should" be at
different positions - Transfer learning: fine-tunes well on ImageNet classification, object detection, semantic segmentation
Performance: - Matches or beats DINO, MAE, SimCLR on downstream tasks - Trains 2–3× faster than MAE (processes fewer
patches, simpler loss) - Better semantic representations than generative methods
VL-JEPA Extension
VL-JEPA takes I-JEPA and adds:
1. Language Tower: A text encoder (BERT-style) processes product descriptions → text embeddings
2. Cross-Modal Loss: Pull image embeddings and matching text embeddings together in shared space (like CLIP)
3.


## [2026-03-16 07:01] Source: VL-JEPA Learning Path — Senior ML Researcher structured guide

- Its central breakthrough: instead of
teaching an AI to generate words one-by-one like a typewriter, it teaches the AI to predict the
meaning of a sentence as a continuous vector in abstract space. Think of the difference this way:
A classical language model says: "Given this image, the next word is 'a', then 'dog', then 'is'..."
— it reconstructs surface text. VL-JEPA says: "Given this image, the semantic embedding of what a correct description would
look like is approximately here in meaning-space." — it reasons about concepts. The result: 50% fewer trainable parameters than token-generating VLMs with the same vision
encoder and training data, native zero-shot classification, and a selective decoding mechanism
that cuts inference operations by 2.85×. To understand why this works, you need the five papers below.
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
- The positional encodings are how
VL-JEPA's predictor knows where the masked patches are located — it uses position tokens to
tell the predictor "predict what's at grid position (3,7)" even without seeing that region. : i-th flattened image patch (a raw vector of pixel values)
: Patch embedding matrix (learnable, projects patch → hidden dimension)
: Classification token (special learnable vector prepended to the sequence)
: Positional embedding (adds spatial location information to each token)
: Initial sequence fed into the Transformer (the starting representation)
Mental model: Imagine cutting a photograph into a 14×14 grid of tiles, writing the tile's grid
coordinates on the back of each one, then handing the pile to a Transformer — that's exactly
what this equation does. ViT just classifies images using labels — it requires massive labeled datasets (ImageNet-21k or
JFT-300M) to work well. Labels are expensive to create. What if you could train a ViT on
completely unlabeled images and still get rich, useful representations?
- VL-JEPA's core innovation is to predict in this joint embedding space rather than decode
tokens. Without understanding CLIP's contrastive alignment objective, you won't understand
what VL-JEPA's language tower is trying to do or why predicting in semantic space is
fundamentally different from predicting tokens. The problem it solved:
Classical image classifiers (like ViT trained on ImageNet) are brittle. They learn to recognize
1,000 specific categories, and if you show them a class they weren't trained on, they fail
completely — even if the new class is just "a photo of a golden retriever in the snow" when they
trained on "golden retriever." The model never learned language — it just learned label numbers. There was no bridge between visual and textual understanding.
- CLIP's loss says: "The person in this photo should end up standing right next to the person
[8] [7]
[1]
Key Equation

holding this name tag — and as far as possible from everyone else."
CLIP learns shared representations, but it requires massive amounts of negative examples
(large batch sizes) and carefully crafted contrastive pairs to work. It also learns at the image
level — not at the patch level. It doesn't ask: "What is happening in this specific region of the
image?" There's also no mechanism for the model to reason about what's missing from an image
or to predict unobserved content. That gap — learning rich local representations without
contrastive pairs — is exactly what MAE (the next paper) addresses. BATCH of N image-text pairs:
  Image 1 → [Image Encoder] → v₁ ─┐
  Image 2 → [Image Encoder] → v₂  │   N×N Similarity Matrix
  ...
- Why it matters for VL-JEPA:
MAE demonstrates that aggressive masking forces models to learn semantic representations —
this exact intuition lives inside I-JEPA and VL-JEPA. But MAE's critical flaw is that it predicts raw
pixel values. Pixel prediction is not semantic — you can perfectly reconstruct pixel colors
without understanding anything about the meaning of what's in the image. VL-JEPA
completely abandons pixel-space prediction in favor of embedding-space prediction, where
representations encode meaning rather than appearance. Plain English Summary
[9]
[10] [9]
[9] [1]

: Set of masked patch indices (the 75% that were hidden)
: Number of masked patches (normalizes the loss)
: True pixel values of the i-th masked patch (the ground truth)
: Predicted pixel values for the i-th masked patch (decoder output)
: Squared L2 norm — measures how far the prediction is from the truth
Mental model: You cover 75% of a photograph with sticky notes, then ask someone to draw
what's behind each sticky note.
- If you understand I-JEPA
completely, VL-JEPA becomes a set of deliberate, logical extensions rather than a collection of
opaque design choices. The problem it solved:
MAE (Paper 4) predicts pixels — and that's too low-level. DINO and other contrastive SSL
methods predict in embedding space but require aggressive data augmentation (flipping,
cropping, color jittering) to generate positive pairs — and those augmentations bake in biases
about what should be invariant. I-JEPA asks: can we learn highly semantic representations
without pixel prediction and without any data augmentation at all — just by predicting
context-to-context inside a single image? The core idea — one big insight:
Take one image, no augmentations.
- The context/target
encoder duo and the EMA trick are carried forward verbatim into VL-JEPA's video encoder
architecture. : Number of target blocks sampled in this training step
: Predicted representation for target block  (output of the predictor)
: Target representation for block  (output of the EMA target encoder — the ground
truth)
: Squared L2 distance — how far the prediction is from the target in embedding space
Mental model: Imagine you can only see the left half of a painting. Your task isn't to paint the
right half in pixel-perfect detail — it's to write a semantic description that matches what an
expert art critic would write about the right half. You're judged on conceptual accuracy, not
color matching. [2] [1]
Key Equation

I-JEPA only works on static images with one modality.


## [2026-03-16 07:03] Source: VL-JEPA Reading List — 5 Paper Summaries (Suhail's notes)

- It learns this from data. This makes
it more flexible than CNNs — it can learn any spatial relationship, not just local ones. Mental Model
Image (224×224 pixels)
        ↓
Cut into patches (16×16 each)
        ↓
[P1][P2][P3]...[P196]  ← 196 patches, like 196 words
        ↓
Each patch → embedding vector (768 numbers)
        ↓
Add position info: P1=top-left, P196=bottom-right
        ↓
Feed into Transformer (same as language Transformer)
        ↓
196 output embeddings — each patch now "knows" about all other patches
Paper 3: Learning Transferable Visual Models From Natural Language Supervision
(CLIP, 2021)
Authors: Radford et al. (OpenAI) Link: https://arxiv.org/abs/2103.00020 Read: Sections 1, 2, 3.1, 3.2, and Figure 1. Skip
sections 4–5.
- Time: 45 minutes
Why You Need This

VL-JEPA's cross-modal alignment (connecting vision and language) is inspired directly by CLIP. CLIP showed the world that you
can train a model to understand both images and text together, using only natural image-caption pairs from the internet — no
manual labels needed. Plain English Summary
The problem it solved: Training vision models traditionally required massive labeled datasets — ImageNet has 14 million
images, each manually labeled by humans. This is expensive, slow, and limits what the model can recognize (only what's in the
labels). The big idea — Learn from image-text pairs: The internet is full of images with captions — news articles, product listings,
social media, Wikipedia.
- EMA prevents this: - Target encoder is updated slowly (momentum = 0.996 means it only
changes 0.4% per step) - Context encoder updates fast - There's always a gap between them — the predictor is always chasing a
moving target
The masking strategy: - Divide image into 196 patches (14×14 grid) - Select 4 random rectangular "target blocks" to mask
(roughly 50% of patches) - Context = remaining visible patches - The model must predict the target blocks given the context
Rectangular blocks are harder than random patches — the model can't reconstruct a rectangular region just from adjacent
context patches. It must understand the global content. What I-JEPA learns: Without any labels, without any augmentations, trained only to predict masked representations: -
Semantic understanding: similar objects cluster in embedding space - Spatial understanding: knows what "should" be at
different positions - Transfer learning: fine-tunes well on ImageNet classification, object detection, semantic segmentation
Performance: - Matches or beats DINO, MAE, SimCLR on downstream tasks - Trains 2–3× faster than MAE (processes fewer
patches, simpler loss) - Better semantic representations than generative methods
VL-JEPA Extension
VL-JEPA takes I-JEPA and adds:
1. Language Tower: A text encoder (BERT-style) processes product descriptions → text embeddings
2. Cross-Modal Loss: Pull image embeddings and matching text embeddings together in shared space (like CLIP)
3.


## [2026-03-16 07:03] Source: VL-JEPA Learning Path — Senior ML Researcher structured guide

- Its central breakthrough: instead of
teaching an AI to generate words one-by-one like a typewriter, it teaches the AI to predict the
meaning of a sentence as a continuous vector in abstract space. Think of the difference this way:
A classical language model says: "Given this image, the next word is 'a', then 'dog', then 'is'..."
— it reconstructs surface text. VL-JEPA says: "Given this image, the semantic embedding of what a correct description would
look like is approximately here in meaning-space." — it reasons about concepts. The result: 50% fewer trainable parameters than token-generating VLMs with the same vision
encoder and training data, native zero-shot classification, and a selective decoding mechanism
that cuts inference operations by 2.85×. To understand why this works, you need the five papers below.
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
- The positional encodings are how
VL-JEPA's predictor knows where the masked patches are located — it uses position tokens to
tell the predictor "predict what's at grid position (3,7)" even without seeing that region. : i-th flattened image patch (a raw vector of pixel values)
: Patch embedding matrix (learnable, projects patch → hidden dimension)
: Classification token (special learnable vector prepended to the sequence)
: Positional embedding (adds spatial location information to each token)
: Initial sequence fed into the Transformer (the starting representation)
Mental model: Imagine cutting a photograph into a 14×14 grid of tiles, writing the tile's grid
coordinates on the back of each one, then handing the pile to a Transformer — that's exactly
what this equation does. ViT just classifies images using labels — it requires massive labeled datasets (ImageNet-21k or
JFT-300M) to work well. Labels are expensive to create. What if you could train a ViT on
completely unlabeled images and still get rich, useful representations?
- VL-JEPA's core innovation is to predict in this joint embedding space rather than decode
tokens. Without understanding CLIP's contrastive alignment objective, you won't understand
what VL-JEPA's language tower is trying to do or why predicting in semantic space is
fundamentally different from predicting tokens. The problem it solved:
Classical image classifiers (like ViT trained on ImageNet) are brittle. They learn to recognize
1,000 specific categories, and if you show them a class they weren't trained on, they fail
completely — even if the new class is just "a photo of a golden retriever in the snow" when they
trained on "golden retriever." The model never learned language — it just learned label numbers. There was no bridge between visual and textual understanding.
- CLIP's loss says: "The person in this photo should end up standing right next to the person
[8] [7]
[1]
Key Equation

holding this name tag — and as far as possible from everyone else."
CLIP learns shared representations, but it requires massive amounts of negative examples
(large batch sizes) and carefully crafted contrastive pairs to work. It also learns at the image
level — not at the patch level. It doesn't ask: "What is happening in this specific region of the
image?" There's also no mechanism for the model to reason about what's missing from an image
or to predict unobserved content. That gap — learning rich local representations without
contrastive pairs — is exactly what MAE (the next paper) addresses. BATCH of N image-text pairs:
  Image 1 → [Image Encoder] → v₁ ─┐
  Image 2 → [Image Encoder] → v₂  │   N×N Similarity Matrix
  ...
- Why it matters for VL-JEPA:
MAE demonstrates that aggressive masking forces models to learn semantic representations —
this exact intuition lives inside I-JEPA and VL-JEPA. But MAE's critical flaw is that it predicts raw
pixel values. Pixel prediction is not semantic — you can perfectly reconstruct pixel colors
without understanding anything about the meaning of what's in the image. VL-JEPA
completely abandons pixel-space prediction in favor of embedding-space prediction, where
representations encode meaning rather than appearance. Plain English Summary
[9]
[10] [9]
[9] [1]

: Set of masked patch indices (the 75% that were hidden)
: Number of masked patches (normalizes the loss)
: True pixel values of the i-th masked patch (the ground truth)
: Predicted pixel values for the i-th masked patch (decoder output)
: Squared L2 norm — measures how far the prediction is from the truth
Mental model: You cover 75% of a photograph with sticky notes, then ask someone to draw
what's behind each sticky note.
- If you understand I-JEPA
completely, VL-JEPA becomes a set of deliberate, logical extensions rather than a collection of
opaque design choices. The problem it solved:
MAE (Paper 4) predicts pixels — and that's too low-level. DINO and other contrastive SSL
methods predict in embedding space but require aggressive data augmentation (flipping,
cropping, color jittering) to generate positive pairs — and those augmentations bake in biases
about what should be invariant. I-JEPA asks: can we learn highly semantic representations
without pixel prediction and without any data augmentation at all — just by predicting
context-to-context inside a single image? The core idea — one big insight:
Take one image, no augmentations.
- The context/target
encoder duo and the EMA trick are carried forward verbatim into VL-JEPA's video encoder
architecture. : Number of target blocks sampled in this training step
: Predicted representation for target block  (output of the predictor)
: Target representation for block  (output of the EMA target encoder — the ground
truth)
: Squared L2 distance — how far the prediction is from the target in embedding space
Mental model: Imagine you can only see the left half of a painting. Your task isn't to paint the
right half in pixel-perfect detail — it's to write a semantic description that matches what an
expert art critic would write about the right half. You're judged on conceptual accuracy, not
color matching. [2] [1]
Key Equation

I-JEPA only works on static images with one modality.
