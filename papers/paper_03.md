# Crossing the Threshold: Idiomatic Machine Translation through Retrieval Augmentation and Loss Weighting

| Field | Value |
|---|---|
| **Authors** | Emmy Liu, Aditi Chaudhary, Graham Neubig |
| **Venue** | EMNLP 2023 |
| **Year** | 2023 |
| **URL** | https://aclanthology.org/2023.emnlp-main.933/ |
| **arXiv** | https://arxiv.org/abs/2310.07081 |
| **Topic** | Computational approaches; Multilingual idiom datasets |

## Abstract / Key Contribution

Identified a **tipping-point threshold** at which transformer MT models default to idiomatic over
literal translations. Compiled ~4,000 natural sentences with idioms across French, Finnish, and
Japanese. Proposed two techniques: (1) loss upweighting on potentially idiomatic training sentences,
and (2) retrieval-augmented generation (RAG) using example-based learning. Achieved up to 13%
absolute accuracy improvement on idiomatic sentences.

## Methods

- Frequency threshold analysis: counts above which models flip from literal to idiomatic translation
- RAG: at inference time, retrieve similar idiom-in-context examples from training corpus
- Loss weighting: upweight training examples identified as idiomatic via dictionary lookup
- Evaluation on held-out idiom sentences with human annotators

## Relevance to IdiomTranslate30

- IdiomTranslate30's `translate_analogy` strategy uses example-based (retrieval-like) reasoning —
  this paper validates that approach empirically
- The threshold analysis concept could be applied to study how idiom frequency correlates with
  translation strategy differences in IdiomTranslate30
- Japanese is an overlapping source language
