"""
Local knowledge extractor — works without an API key.
Uses rule-based + keyword extraction to pull structured insights from papers.
Falls back gracefully when Anthropic API key is not available.
"""
from __future__ import annotations
import re
from typing import Dict, List

JEPA_KEYWORDS = {
    "concepts": ["embedding", "representation", "self-supervised", "masked", "patch",
                 "attention", "transformer", "encoder", "decoder", "contrastive",
                 "zero-shot", "fine-tuning", "EMA", "momentum", "predictive"],
    "architecture": ["context encoder", "target encoder", "predictor", "ViT",
                    "vision transformer", "BERT", "language encoder", "cross-modal",
                    "patch embedding", "positional encoding", "CLS token", "multi-head"],
    "training": ["loss", "MSE", "InfoNCE", "learning rate", "batch size", "epoch",
                "warmup", "cosine", "gradient", "backprop", "momentum", "EMA",
                "masking ratio", "rectangular", "block masking"],
    "datasets": ["ImageNet", "COCO", "ABO", "Amazon Berkeley", "CC12M", "LAION",
                "Home Depot", "Products-10K", "Open Images"],
}

def extract_sentences_with_keywords(text: str, keywords: List[str], context_window: int = 2) -> List[str]:
    sentences = re.split(r'(?<=[.!?])\s+', text)
    results = []
    for i, sent in enumerate(sentences):
        if any(kw.lower() in sent.lower() for kw in keywords):
            start = max(0, i - context_window)
            end = min(len(sentences), i + context_window + 1)
            snippet = " ".join(sentences[start:end]).strip()
            if len(snippet) > 50 and snippet not in results:
                results.append(snippet)
    return results[:10]

def extract_knowledge_local(content: str, source: str) -> Dict:
    """Extract structured knowledge using local heuristics."""
    results = {
        "source": source,
        "concepts": [],
        "architecture": [],
        "training": [],
        "datasets": [],
        "code_improvements": [],
        "summary": "",
    }

    for category, keywords in JEPA_KEYWORDS.items():
        snippets = extract_sentences_with_keywords(content, keywords)
        results[category] = snippets

    # Extract summary from first 1000 chars
    clean = re.sub(r'\s+', ' ', content[:2000]).strip()
    results["summary"] = clean[:500] + "..." if len(clean) > 500 else clean

    # Code improvement suggestions based on keywords found
    if any(kw in content.lower() for kw in ["rectangular", "block masking", "multi-block"]):
        results["code_improvements"].append(
            "Consider using multi-block rectangular masking instead of random patch masking in src/training/masking.py"
        )
    if "ema" in content.lower() or "exponential moving average" in content.lower():
        results["code_improvements"].append(
            "Verify EMA momentum is set to 0.996 and updates correctly in src/models/vl_jepa.py"
        )
    if "infonce" in content.lower() or "contrastive" in content.lower():
        results["code_improvements"].append(
            "Cross-modal alignment loss in src/training/losses.py should use InfoNCE/NT-Xent formulation"
        )
    if "layer norm" in content.lower() or "layernorm" in content.lower():
        results["code_improvements"].append(
            "Ensure LayerNorm is applied before attention (pre-norm) in all transformer blocks"
        )

    return results
