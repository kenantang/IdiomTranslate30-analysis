# Can Transformer be Too Compositional? Analysing Idiom Processing in Neural Machine Translation

| Field | Value |
|---|---|
| **Authors** | Verna Dankers, Christopher Lucas, Ivan Titov |
| **Venue** | ACL 2022 |
| **Year** | 2022 |
| **URL** | https://aclanthology.org/2022.acl-long.252/ |
| **Topic** | Computational approaches to idiom translation |

## Abstract / Key Contribution

Analyzed Transformer hidden states and attention patterns across English-to-seven-European-language
models to understand why NMT systems tend to produce literal translations of idioms. Found that when
models correctly identify an expression as idiomatic, the encoder processes it more as a single
lexical unit — but this mechanism is fragile and often fails. The Transformer's compositional
processing bias is identified as a root cause of literal idiom translation errors.

## Methods

- Probing classifiers on encoder hidden states to detect idiomaticity
- Attention head analysis to identify which heads contribute to holistic vs. compositional processing
- Controlled experiments varying idiom frequency in training data
- Evaluation across 7 target languages (French, German, Italian, Dutch, Polish, Russian, Finnish)

## Relevance to IdiomTranslate30

- Provides theoretical grounding for why literal translations occur — relevant when comparing
  `translate_creatively` vs `translate_author` failure modes
- The 7-language evaluation setup is methodologically similar to IdiomTranslate30's 10-language design
- Frequency analysis motivates studying idiom frequency effects within the dataset
