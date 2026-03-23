# MMTE: Corpus and Metrics for Evaluating Machine Translation Quality of Metaphorical Language

| Field | Value |
|---|---|
| **Authors** | Shun Wang, Ge Zhang, Han Wu, Tyler Loakman, Wenhao Huang, Chenghua Lin |
| **Venue** | EMNLP 2024 |
| **Year** | 2024 |
| **URL** | https://aclanthology.org/2024.emnlp-main.634/ |
| **Topic** | Evaluation metrics for figurative/idiomatic translation |

## Abstract / Key Contribution

Proposed a **multi-dimensional human evaluation framework** for figurative language translation
across four axes: Metaphorical Equivalence, Emotion, Authenticity, and Overall Quality. Built a
multilingual parallel corpus of metaphorical expressions created through human post-editing.
Showed that standard fluency/factuality metrics fail to capture figurative translation quality.

## Methods

- Four-dimensional annotation rubric applied by trained annotators
- Automatic metric comparison: BLEU, METEOR, BERTScore, COMET vs. human judgments
- Human post-editing workflow to create reference translations
- Regression analysis to identify which dimension best predicts overall quality

## Relevance to IdiomTranslate30

- The four-dimensional framework is directly applicable to IdiomTranslate30's three strategies:
  Metaphorical Equivalence ↔ faithfulness; Emotion/Authenticity ↔ creativity
- Motivates a multi-dimensional scoring approach rather than a single aggregate metric
- Confirms that standard NLP metrics (BLEU, BERTScore) are insufficient for figurative translation
  evaluation — critical context for choosing analysis metrics
