# Automatic Evaluation and Analysis of Idioms in Neural Machine Translation

| Field | Value |
|---|---|
| **Authors** | Christos Baziotis, Prashant Mathur, Eva Hasler |
| **Venue** | EACL 2023 |
| **Year** | 2023 |
| **URL** | https://aclanthology.org/2023.eacl-main.267/ |
| **arXiv** | https://arxiv.org/abs/2210.04545 |
| **Topic** | Evaluation metrics; Span annotation for idioms |

## Abstract / Key Contribution

Proposed **LitTER** (Literal Translation Error Rate), an automatic metric that uses bilingual word
dictionaries and annotated source spans to detect and quantify literal translation errors without
human involvement. Showed that monolingual pretraining yields substantial improvements in idiomatic
translation even without test-set idiom exposure. Pretrained models are more context-sensitive and
less "myopic" than randomly initialized ones.

## Methods

- LitTER: computes token-level overlap between source span tokens (translated word-for-word) and
  the hypothesis translation within the annotated target span region
- Controlled training experiments: random init vs. pretrained encoder/decoder ablations
- Manual annotation of source idiom spans used as evaluation signal

## Relevance to IdiomTranslate30

- **Most directly applicable paper**: LitTER relies on exactly the kind of source span + translation
  pairs that IdiomTranslate30 provides via `span_creatively`, `span_analogy`, `span_author`
- Can implement a LitTER-inspired analysis to measure how "literal" each strategy's span is
- Methodology for measuring span-level translation quality can be directly applied to the dataset
