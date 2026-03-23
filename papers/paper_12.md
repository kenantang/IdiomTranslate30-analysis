# Improving LLM Abilities in Idiomatic Translation

| Field | Value |
|---|---|
| **Authors** | Sundesh Donthi, Maximilian Spencer, Om Patel, Joon Doh, Eid Rodan, Kevin Zhu, Sean O'Brien |
| **Venue** | LoResLM Workshop at COLING 2025 |
| **Year** | 2025 |
| **URL** | https://arxiv.org/abs/2407.03518 |
| **Topic** | Computational approaches; Evaluation metrics; Low-resource languages |

## Abstract / Key Contribution

Proposed two methods to improve idiom translation style beyond meaning transfer: (1) Cosine
Similarity using SentenceTransformers to match source and target idioms semantically, and (2) an
LLM-generated method where the model selects an equivalent target-language idiom. Tested on
English↔Chinese; Cosine Similarity outperformed alternatives in GPT-4o evaluations. Created a new
Urdu idiom dataset to demonstrate transferability.

## Methods

- SentenceTransformer embeddings to retrieve semantically equivalent target idioms
- LLM-guided idiom selection: model proposes candidate idioms, ranked by embedding similarity
- GPT-4o evaluation: scores translations on naturalness and idiomatic appropriateness
- Cross-lingual transfer test on Urdu

## Relevance to IdiomTranslate30

- Directly addresses Chinese idiom translation (overlapping with IdiomTranslate30's largest source)
- Cosine Similarity approach between source and target idiom spans is directly testable using
  IdiomTranslate30's `span_*` columns + multilingual sentence embeddings
- Provides a baseline for measuring how often IdiomTranslate30's `translate_analogy` strategy
  successfully selects an equivalent target idiom
