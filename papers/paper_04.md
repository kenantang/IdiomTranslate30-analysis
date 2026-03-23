# Translate Meanings, Not Just Words: IdiomKB's Role in Optimizing Idiomatic Translation with Language Models

| Field | Value |
|---|---|
| **Authors** | Shuang Li, Jiangjie Chen, Siyu Yuan, Xinyi Wu, Hao Yang, Shimin Tao, Yanghua Xiao |
| **Venue** | AAAI 2024 |
| **Year** | 2024 |
| **URL** | https://ojs.aaai.org/index.php/AAAI/article/view/29817 |
| **arXiv** | https://arxiv.org/abs/2308.13961 |
| **Topic** | Multilingual idiom datasets; Computational approaches; Evaluation metrics |

## Abstract / Key Contribution

Built **IdiomKB**, a multilingual idiom knowledge base where LLMs distill figurative meanings.
Retrieving meanings from IdiomKB enables smaller LMs (BLOOMZ 7.1B, Alpaca 7B) to produce accurate
idiomatic translations comparable to GPT-4. Introduced a GPT-4-powered evaluation metric for
translation quality that aligns better with human judgments than standard automatic metrics.
Human evaluation confirmed KB quality at average score 2.92/3.

## Methods

- KB construction: GPT-4 generates meaning explanations for idioms; filtered and stored
- RAG-style prompting: inject retrieved meaning at inference time for smaller models
- GPT-4-as-judge evaluation: rate translations on faithfulness and idiomaticity (1–3 scale)
- Comparison against BLEU, BERTScore, and human annotations

## Relevance to IdiomTranslate30

- IdiomTranslate30's `translate_creatively` is a zero-shot strategy; IdiomKB shows what
  knowledge-grounded prompting achieves by contrast
- The GPT-4-as-judge framework is directly applicable as an evaluation paradigm for comparing
  the three strategies in IdiomTranslate30
- IdiomKB's Chinese/Japanese/Korean coverage may overlap with IdiomTranslate30 idiom inventory
