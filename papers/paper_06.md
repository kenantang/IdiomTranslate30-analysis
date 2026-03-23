# FLUTE: Figurative Language Understanding through Textual Explanations

| Field | Value |
|---|---|
| **Authors** | Tuhin Chakrabarty, Arkadiy Saakyan, Debanjan Ghosh, Smaranda Muresan |
| **Venue** | EMNLP 2022 |
| **Year** | 2022 |
| **URL** | https://aclanthology.org/2022.emnlp-main.481/ |
| **Topic** | Creative/figurative language; Multilingual idiom datasets |

## Abstract / Key Contribution

Introduced **FLUTE**, a 9,000-instance NLI dataset covering sarcasm, simile, metaphor, and idioms,
each paired with a textual explanation of why the inference holds. Used a human-AI collaborative
annotation framework (GPT-3 + crowdworkers + experts). T5 fine-tuned on FLUTE generates better
explanations for figurative language. Standard benchmark for figurative language comprehension.

## Methods

- NLI framing: premise (figurative sentence) → hypothesis, with entailment/contradiction label
  + free-text explanation
- Human-AI pipeline: GPT-3 drafts explanations; crowdworkers validate; experts adjudicate
- Fine-tuning T5 on FLUTE for explanation generation

## Relevance to IdiomTranslate30

- The explanation-generation paradigm parallels how IdiomTranslate30's creative strategies
  must "explain" idiom meaning through the translated span
- FLUTE's idiom subset could serve as an external benchmark to test whether IdiomTranslate30
  translations preserve inference relationships
- Methodology for distinguishing figurative vs. literal processing is applicable to span analysis
