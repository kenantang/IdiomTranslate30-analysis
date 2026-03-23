# SemEval-2022 Task 2: Multilingual Idiomaticity Detection and Sentence Embedding

| Field | Value |
|---|---|
| **Authors** | Harish Tayyar Madabushi, Edward Gow-Smith, Marcos Garcia, Carolina Scarton, Marco Idiart, Aline Villavicencio |
| **Venue** | SemEval 2022 |
| **Year** | 2022 |
| **URL** | https://aclanthology.org/2022.semeval-1.13/ |
| **arXiv** | https://arxiv.org/abs/2204.10050 |
| **Topic** | Multilingual idiom datasets; Span annotation for idioms |

## Abstract / Key Contribution

Introduced a shared task with two subtasks: (a) binary idiomaticity classification in context and
(b) sentence embedding / semantic similarity for idiomatic expressions. Released annotated datasets
in English, Portuguese, and Galician. Attracted ~100 registered participants, 25 teams, 650+
submissions. Established a multilingual idiom benchmark widely used by subsequent work.

## Methods

- Zero-shot and one-shot subtask variants to test cross-lingual transfer
- Annotation: token spans of idiomatic multiword expressions (MWEs) with idiomaticity labels
- Evaluation: macro-F1 for classification; Spearman correlation for embedding similarity

## Relevance to IdiomTranslate30

- Span annotation methodology directly parallels IdiomTranslate30's `span_*` columns
- The idiomaticity detection framing could be applied to measure how often each translation strategy
  preserves or loses idiomatic meaning
- Shared evaluation infrastructure could be used to benchmark IdiomTranslate30 translations
