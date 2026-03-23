# Large Language Models for Persian ↔ English Idiom Translation

| Field | Value |
|---|---|
| **Authors** | Sara Rezaeimanesh, Faezeh Hosseini, Yadollah Yaghoobzadeh |
| **Venue** | NAACL 2025 |
| **Year** | 2025 |
| **URL** | https://aclanthology.org/2025.naacl-long.405/ |
| **arXiv** | https://arxiv.org/abs/2412.09993 |
| **Topic** | Multilingual idiom datasets; Evaluation metrics; LLM comparison |

## Abstract / Key Contribution

Introduced **PersianIdioms**: 2,200 idioms with meanings and 700 usage examples, plus parallel
bidirectional Persian↔English translation datasets. Evaluated open/closed-source LLMs and NMT
systems. Validated automated metrics (LLM-as-judge, BLEU, BERTScore) against human judgment.
Claude-3.5-Sonnet performed best in both directions; prompting complexity matters more for
weaker models.

## Methods

- Dataset construction via human experts + automated tools
- Model zoo evaluation: GPT-4, Claude, Llama, Mistral, mBART, M2M-100, OPUS-MT
- LLM-as-judge scoring (GPT-4 rates translations 1–5) vs. human inter-annotator agreement
- Metric correlation analysis: Kendall's τ between automatic metrics and human scores

## Relevance to IdiomTranslate30

- Provides a direct model comparison blueprint applicable to IdiomTranslate30's Gemini-generated
  translations — useful for contextualizing quality relative to other LLMs
- LLM-as-judge validation methodology directly applicable for automated evaluation of the dataset
- Shows which automatic metrics (BERTScore, LLM-judge) are most reliable for idiom translation
