# Creative and Context-Aware Translation of East Asian Idioms with GPT-4

| Field | Value |
|---|---|
| **Authors** | Kenan Tang, Peiyang Song, Yao Qin, Xifeng Yan |
| **Venue** | arXiv preprint; EMNLP 2024 Findings |
| **Year** | 2024 |
| **URL** | https://arxiv.org/abs/2410.00988 |
| **Topic** | Creative/figurative language translation; Evaluation metrics |

## Abstract / Key Contribution

The **companion paper** for IdiomTranslate30. Investigated GPT-4's ability to generate creative
and culturally sensitive translations of East Asian idioms (Chinese, Japanese, Korean). Identified
Pareto-optimal prompting strategies that outperform commercial translation engines on a joint
faithfulness × creativity evaluation. Context-aware prompting generates substantially more
high-quality candidate translations per idiom than human baselines.

## Methods

- Three prompting strategies: zero-shot creative (→ `translate_creatively`),
  analogy-based creative (→ `translate_analogy`), author-voice (→ `translate_author`)
- Automatic evaluation: LLM-as-judge scoring on faithfulness (1–5) and creativity (1–5)
- Pareto frontier analysis: identify strategies that are non-dominated on both axes
- Span annotation: GPT-4 identifies the target span that corresponds to the idiom

## Relevance to IdiomTranslate30

- **Primary reference** — directly describes how the dataset was built
- Defines the evaluation criteria (faithfulness, creativity) that should guide all downstream analysis
- Explains the rationale for the three translation columns and the span annotation design
- Motivates analysis of Pareto optimality across language pairs and idiom types
