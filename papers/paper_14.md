# It's Not a Walk in the Park! Challenges of Idiom Translation in Speech-to-Text Systems

| Field | Value |
|---|---|
| **Authors** | Iuliia Zaitova, Badr M. Abdullah, Wei Xue, Dietrich Klakow, Bernd Möbius, Tania Avgustinova |
| **Venue** | ACL 2025 |
| **Year** | 2025 |
| **URL** | https://aclanthology.org/2025.acl-long.1512/ |
| **arXiv** | https://arxiv.org/abs/2506.02995 |
| **Topic** | Computational approaches; Span annotation; Evaluation metrics |

## Abstract / Key Contribution

First systematic evaluation of idiom translation in speech-to-text (SLT) systems vs. text-to-text
MT, covering German→English and Russian→English. Compared end-to-end SLT (SeamlessM4T, Whisper),
MT systems, and LLMs (DeepSeek, LLaMA) alongside cascaded pipelines. SLT systems revert to
literal translations far more often than MT or LLMs. Called for idiom-specific strategies in SLT.

## Methods

- Parallel corpora of audio + text with idiom span annotations
- Automatic idiom detection using dictionary + span matching
- LitTER-inspired evaluation of literal vs. idiomatic output rate
- Ablation: end-to-end vs. cascaded (ASR → MT) SLT pipelines

## Relevance to IdiomTranslate30

- Validates the importance of span annotations as an evaluation signal — IdiomTranslate30's
  `span_*` columns are essential for this kind of literal-vs-idiomatic analysis
- The literal translation detection methodology (span-based) can be adapted for IdiomTranslate30
- Comparison across model types provides a benchmark context for Gemini-generated translations
