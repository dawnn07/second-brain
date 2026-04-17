from __future__ import annotations

from pathlib import Path

import pytest


SAMPLE_ARTICLES: dict[str, str] = {
    "ml/transformers.md": """---
Title: Transformers
Sources: Vaswani et al. (2017-06-12)
Raw: [attention-is-all-you-need](../../raw/ml/attention-is-all-you-need.md)
Updated: 2026-04-10
Confidence: 0.9
Decay: slow
Relationships: supersedes:[RNN Encoders](rnn-encoders.md); related-to:[Attention](attention.md)
---

## Summary

Transformers are attention-based sequence models that replaced recurrent architectures for most NLP tasks.

## Key Points

Self-attention lets every token see every other token in a single step. Positional encodings preserve order.
""",
    "ml/attention.md": """---
Title: Attention
Sources: Bahdanau et al. (2014-09-01)
Raw: [neural-mt-align-translate](../../raw/ml/neural-mt-align-translate.md)
Updated: 2026-04-09
Confidence: 0.85
Decay: slow
Relationships: related-to:[Transformers](transformers.md)
---

## Summary

Attention is a mechanism that lets a model weigh different parts of an input when producing each output.

## Key Points

Soft attention is differentiable. Hard attention requires reinforcement learning.
""",
    "ml/rnn-encoders.md": """---
Title: RNN Encoders
Sources: Cho et al. (2014-06-03)
Raw: [rnn-encoder-decoder](../../raw/ml/rnn-encoder-decoder.md)
Updated: 2024-01-15
Confidence: 0.6
Decay: medium
---

## Summary

RNN encoder-decoder models were the pre-transformer standard for sequence-to-sequence tasks.

## Key Points

They struggle with long-range dependencies because gradients decay through time.
""",
}


@pytest.fixture()
def sample_wiki(tmp_path: Path) -> Path:
    """Build a tiny wiki/ tree on disk and return its root."""
    wiki = tmp_path / "wiki"
    for rel, body in SAMPLE_ARTICLES.items():
        path = wiki / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8")
    (wiki / "index.md").write_text("# Knowledge Base Index\n", encoding="utf-8")
    (wiki / "log.md").write_text("# Wiki Log\n", encoding="utf-8")
    return wiki
