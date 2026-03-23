# PIE: A Parallel Idiomatic Expression Corpus for Idiomatic Sentence Generation and Paraphrasing

| Field | Value |
|---|---|
| **Authors** | Jianing Zhou, Hongyu Gong, Suma Bhat |
| **Venue** | MWE 2021 (co-located with ACL-IJCNLP 2021) |
| **Year** | 2021 |
| **URL** | https://aclanthology.org/2021.mwe-1.5/ |
| **Topic** | Multilingual idiom datasets; Span annotation for idioms |

## Abstract / Key Contribution

Curated **PIE**, a parallel corpus of 823 idiomatic expressions where each entry pairs a sentence
containing the idiom with a sentence where the idiom is replaced by its literal paraphrase.
Proposed two tasks: idiomatic sentence generation and idiomatic paraphrasing. Benchmarked deep
learning models using both automatic and manual evaluation.

## Methods

- Manual curation of idiom–paraphrase pairs from existing idiom dictionaries
- Automatic evaluation: BLEU, ROUGE against reference paraphrases
- Manual evaluation: fluency and meaning preservation scored by annotators
- Baseline models: seq2seq with attention, GPT-2 fine-tuning

## Relevance to IdiomTranslate30

- IdiomTranslate30's translation strategies are conceptually analogous to the generation/paraphrasing
  task in PIE — translating idiom meaning vs. retaining idiomatic form
- PIE's span-level paraphrase structure mirrors IdiomTranslate30's `span_*` annotation design
- The evaluation framework (fluency × meaning preservation) maps onto faithfulness × creativity
